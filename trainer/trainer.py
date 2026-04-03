"""
训练器模块（AlphaTransformer）
支持：多阶段训练、早停、梯度裁剪、学习率调度、TensorBoard 日志
"""

import os
import time
import math
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.tensorboard import SummaryWriter
from typing import Optional, Dict, Tuple
import pandas as pd
from tqdm import tqdm

from models.alpha_transformer import AlphaTransformer, AlphaTransformerV2
from evaluation.backtest import BacktestEngine


class MixedHuberLoss(nn.Module):
    """
    Mixed Huber Loss: 结合 MSE 和 MAE 的优点

    当 |error| <= delta 时使用 MSE（平滑梯度）
    当 |error| > delta 时使用 MAE（鲁棒性）
    对金融数据中的极端收益更鲁棒
    """

    def __init__(self, delta: float = 1.0):
        super().__init__()
        self.delta = delta

    def forward(self, pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        abs_error = torch.abs(pred - target)
        quadratic = torch.clamp(abs_error, max=self.delta)
        linear = abs_error - quadratic
        return torch.mean(0.5 * quadratic ** 2 + self.delta * linear)


class HuberLoss(nn.Module):
    """标准 Huber Loss"""

    def __init__(self, delta: float = 1.0):
        super().__init__()
        self.delta = delta

    def forward(self, pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        error = pred - target
        abs_error = torch.abs(error)
        quadratic = torch.clamp(abs_error, max=self.delta)
        linear = abs_error - quadratic
        return torch.mean(0.5 * quadratic ** 2 + self.delta * linear)


class AlphaTransformerTrainer:
    """
    AlphaTransformer 训练器
    """

    def __init__(
        self,
        model: nn.Module,
        config,
        device: str = "cuda",
        log_dir: str = "logs",
        checkpoint_dir: str = "checkpoints",
    ):
        self.model = model.to(device)
        self.device = device
        self.cfg = config.training

        # ---- 损失函数 ----
        loss_fn_map = {
            "mse": nn.MSELoss(),
            "huber": HuberLoss(delta=1.0),
            "mixed_huber": MixedHuberLoss(delta=1.0),
        }
        self.criterion = loss_fn_map.get(self.cfg.loss_fn, nn.MSELoss())

        # ---- 优化器 ----
        self.optimizer = optim.AdamW(
            self.model.parameters(),
            lr=self.cfg.learning_rate,
            weight_decay=self.cfg.weight_decay,
        )

        # ---- 学习率调度：Cosine Annealing with Warmup ----
        self.scheduler = self._build_scheduler(
            total_epochs=self.cfg.epochs,
            warmup_epochs=self.cfg.warmup_epochs,
            min_lr=self.cfg.min_lr,
        )

        # ---- 日志 ----
        self.writer = SummaryWriter(log_dir=log_dir)
        self.log_interval = config.system.log_interval

        # ---- Checkpoint ----
        self.checkpoint_dir = checkpoint_dir
        os.makedirs(checkpoint_dir, exist_ok=True)

        # ---- 训练状态 ----
        self.global_step = 0
        self.best_val_loss = float("inf")
        self.patience_counter = 0
        self.train_losses = []
        self.val_losses = []

    def _build_scheduler(self, total_epochs, warmup_epochs, min_lr):
        warmup_steps = warmup_epochs

        def lr_lambda(step):
            if step < warmup_steps:
                return step / max(warmup_steps, 1)
            else:
                progress = (step - warmup_steps) / max(total_epochs - warmup_steps, 1)
                return max(min_lr / self.cfg.learning_rate, 0.5 * (1.0 + math.cos(math.pi * progress)))

        return optim.lr_scheduler.LambdaLR(self.optimizer, lr_lambda)

    def train_epoch(self, train_loader) -> float:
        """训练一个 epoch"""
        self.model.train()
        total_loss = 0.0
        num_batches = 0

        pbar = tqdm(train_loader, desc="Training", leave=False)
        for batch_idx, (x, y, asset_ids) in enumerate(pbar):
            x = x.to(self.device)
            y = y.to(self.device)

            self.optimizer.zero_grad()

            if asset_ids is not None:
                asset_ids = asset_ids.to(self.device)
                pred = self.model(x, asset_ids)
            else:
                pred = self.model(x)

            # pred: [B, A]   y: [B, A, 1]
            target = y.squeeze(-1)  # [B, A]

            loss = self.criterion(pred, target)

            # 反向传播
            loss.backward()

            # 梯度裁剪
            torch.nn.utils.clip_grad_norm_(
                self.model.parameters(), self.cfg.grad_clip_norm
            )

            self.optimizer.step()
            self.scheduler.step()

            total_loss += loss.item()
            num_batches += 1
            self.global_step += 1

            # 日志
            if batch_idx % self.log_interval == 0:
                pbar.set_postfix({"loss": f"{loss.item():.6f}"})
                self.writer.add_scalar("train/loss", loss.item(), self.global_step)
                self.writer.add_scalar(
                    "train/lr",
                    self.optimizer.param_groups[0]["lr"],
                    self.global_step,
                )

        avg_loss = total_loss / max(num_batches, 1)
        self.train_losses.append(avg_loss)
        return avg_loss

    def evaluate(self, val_loader) -> float:
        """评估"""
        self.model.eval()
        total_loss = 0.0
        num_batches = 0

        with torch.no_grad():
            for x, y, asset_ids in val_loader:
                x = x.to(self.device)
                y = y.to(self.device)

                if asset_ids is not None:
                    asset_ids = asset_ids.to(self.device)
                    pred = self.model(x, asset_ids)
                else:
                    pred = self.model(x)

                target = y.squeeze(-1)
                loss = self.criterion(pred, target)

                total_loss += loss.item()
                num_batches += 1

        avg_loss = total_loss / max(num_batches, 1)
        self.val_losses.append(avg_loss)
        self.writer.add_scalar("val/loss", avg_loss, len(self.train_losses))
        return avg_loss

    def train(
        self,
        train_loader,
        val_loader,
        epochs: Optional[int] = None,
    ) -> Dict[str, list]:
        """
        完整训练循环

        Returns:
            {'train_loss': [...], 'val_loss': [...]}
        """
        epochs = epochs or self.cfg.epochs

        print(f"\n{'='*60}")
        print(f"  开始训练 | Device: {self.device}")
        print(f"  模型参数量: {sum(p.numel() for p in self.model.parameters()):,}")
        print(f"{'='*60}\n")

        for epoch in range(epochs):
            epoch_start = time.time()

            # 训练
            train_loss = self.train_epoch(train_loader)

            # 评估
            val_loss = self.evaluate(val_loader)

            epoch_time = time.time() - epoch_start

            # 打印
            print(
                f"Epoch {epoch+1:03d}/{epochs} | "
                f"Train Loss: {train_loss:.6f} | "
                f"Val Loss: {val_loss:.6f} | "
                f"LR: {self.optimizer.param_groups[0]['lr']:.2e} | "
                f"Time: {epoch_time:.1f}s"
            )

            # 早停
            if val_loss < self.best_val_loss - self.cfg.early_stop_delta:
                self.best_val_loss = val_loss
                self.patience_counter = 0
                self.save_checkpoint("best_model.pt")
                print(f"  ★ 保存最佳模型 (Val Loss: {val_loss:.6f})")
            else:
                self.patience_counter += 1
                if self.patience_counter >= self.cfg.patience:
                    print(f"\n早停触发于 Epoch {epoch+1}")
                    break

            # 定期保存
            if (epoch + 1) % 10 == 0:
                self.save_checkpoint(f"checkpoint_epoch_{epoch+1}.pt")

        print(f"\n训练完成！最佳 Val Loss: {self.best_val_loss:.6f}")
        return {
            "train_loss": self.train_losses,
            "val_loss": self.val_losses,
        }

    def predict(self, dataloader) -> Tuple[np.ndarray, np.ndarray]:
        """
        对数据生成预测

        Returns:
            (predictions, targets) 均为 numpy 数组
        """
        self.model.eval()
        all_preds = []
        all_targets = []

        with torch.no_grad():
            for x, y, asset_ids in dataloader:
                x = x.to(self.device)
                if asset_ids is not None:
                    asset_ids = asset_ids.to(self.device)
                    pred = self.model(x, asset_ids)
                else:
                    pred = self.model(x)

                all_preds.append(pred.cpu().numpy())
                all_targets.append(y.squeeze(-1).numpy())

        return np.concatenate(all_preds, axis=0), np.concatenate(all_targets, axis=0)

    def save_checkpoint(self, filename: str):
        """保存模型检查点"""
        path = os.path.join(self.checkpoint_dir, filename)
        torch.save(
            {
                "model_state_dict": self.model.state_dict(),
                "optimizer_state_dict": self.optimizer.state_dict(),
                "scheduler_state_dict": self.scheduler.state_dict(),
                "best_val_loss": self.best_val_loss,
                "global_step": self.global_step,
            },
            path,
        )

    def load_checkpoint(self, filename: str):
        """加载模型检查点"""
        path = os.path.join(self.checkpoint_dir, filename)
        checkpoint = torch.load(path, map_location=self.device)
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        self.scheduler.load_state_dict(checkpoint["scheduler_state_dict"])
        self.best_val_loss = checkpoint["best_val_loss"]
        self.global_step = checkpoint["global_step"]


def run_backtest_from_predictions(
    predictions: np.ndarray,
    targets: np.ndarray,
    dates: list,
    asset_names: list,
    config,
    returns: Optional[np.ndarray] = None,
) -> Dict:
    """
    从模型预测结果运行完整回测的便捷函数

    Args:
        predictions: [num_samples, num_assets] 模型预测（未来3日对数收益均值）
        targets:     [num_samples, num_assets] 真实标签
        dates:       样本对应的日期
        asset_names: 资产名称
        returns:     可选的真实对数收益率 [num_samples, num_assets]
                    如果不提供，使用 targets 代替（但这不是真实收益！）

    Returns:
        回测指标字典

    关键防泄露设计：
        - 预测信号：predictions[t-1]（用前一天信号）
        - 真实收益：returns[t]（当日真实收益）
    """
    import pandas as pd

    engine = BacktestEngine(
        initial_capital=config.backtest.initial_capital,
        transaction_cost=config.backtest.transaction_cost,
        top_k_long=config.backtest.top_k_long,
        bottom_k_short=config.backtest.bottom_k_short,
    )

    # predictions_df: [Date, Asset] 预测信号
    pred_df = pd.DataFrame(predictions, index=dates, columns=asset_names)
    # 如果没有提供真实收益，使用 targets 作为代理（但这会降低信号精度）
    if returns is None:
        returns = targets
    returns_df = pd.DataFrame(returns, index=dates, columns=asset_names)

    # 关键：使用 Signal[t-1] * Return[t] 防止泄露
    # 这在 engine.run() 中已自动处理（使用 prev_preds）
    metrics = engine.run(pred_df, returns_df)
    engine.print_summary(metrics)

    return {
        "metrics": metrics,
        "equity_curve": engine.get_equity_curves(),
        "trade_log": engine.get_trade_log(),
    }
