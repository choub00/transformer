"""
AlphaTransformer 超参数配置
所有数值型参数集中于此，便于调参与实验管理。
"""

from dataclasses import dataclass, field


@dataclass
class ModelConfig:
    """模型架构超参数"""
    # 输入维度
    history_len: int = 60        # 历史窗口长度（时间步数）
    num_assets: int = 16         # 资产数量（动态读取 x.shape[1]）
    feature_dim: int = 8         # 每个资产的特征维度（OHLCV + 技术指标）

    # Patching 层
    patch_size: int = 5           # 每个 Patch 包含多少个时间步
    patch_stride: int = 5         # Patch 滑动步长（不重叠设为等于 patch_size）

    # Embedding
    d_model: int = 128            # 嵌入维度
    asset_emb_dim: int = 64       # 资产 ID 嵌入维度

    # Attention
    num_heads: int = 4            # Multi-Head Attention 的头数
    num_layers: int = 3           # Encoder Block 层数
    d_ff: int = 256               # 前馈网络隐藏层维度

    # Gating (GRN)
    dropout: float = 0.1
    grn_dropout: float = 0.05     # GRN 内专用 dropout，更保守
    context_dim: int = 64         # asset_emb_dim 作为 context 传入 GRN

    # 输出
    output_horizon: int = 1      # 预测步数（对应 target_return 标签）

    @property
    def num_patches(self) -> int:
        """由 history_len 和 patch_size 计算出的 Patch 数量"""
        return self.history_len // self.patch_size


@dataclass
class DataConfig:
    """数据处理超参数"""
    history_len: int = 60         # 模型回看窗口
    target_horizon: int = 3       # 预测未来 N 日均值

    # 归一化
    norm_window: int = 60        # 60 日滚动归一化窗口（核心防泄露）

    # 数据集划分
    train_ratio: float = 0.7
    val_ratio: float = 0.15
    test_ratio: float = 0.15

    # 特征列（按顺序）
    feature_names: list = field(
        default_factory=lambda: [
            "open", "high", "low", "close", "volume",
            "returns_1d", "volatility_5d", "rsi_14"
        ]
    )

    # 数值稳定性
    eps: float = 1e-8            # 防止 log(0) / 除零


@dataclass
class TrainingConfig:
    """训练超参数"""
    batch_size: int = 32
    epochs: int = 100
    learning_rate: float = 1e-4
    weight_decay: float = 1e-5

    # 学习率调度
    warmup_epochs: int = 5
    min_lr: float = 1e-6

    # 正则化
    label_smoothing: float = 0.0  # 未来可扩展

    # 早停
    patience: int = 15
    early_stop_delta: float = 1e-5

    # 梯度裁剪
    grad_clip_norm: float = 1.0

    # 损失函数
    loss_fn: str = "mse"          # mse / huber / mixed_huber


@dataclass
class BacktestConfig:
    """回测引擎超参数"""
    initial_capital: float = 100_000.0

    # 交易成本
    transaction_cost: float = 0.0015   # 单边 0.15%

    # 仓位管理
    top_k_long: int = 2             # 做多 Top 2
    bottom_k_short: int = 2         # 做空 Bottom 2

    # Anti-Churn 防过度交易
    min_hold_days: int = 1          # 最小持仓天数（目前每天评仓，但通过集合差集实现防 churn）
    churn_threshold: float = 0.0     # 预测排名不变则不调仓

    # 基准
    benchmark_enabled: bool = True   # 是否输出等权基准曲线

    # 手续费类型
    cost_model: str = "log_return"  # 手续费从当日收益中扣除（对数域减法）


@dataclass
class SystemConfig:
    """系统级配置"""
    seed: int = 42
    device: str = "cuda"           # cuda / cpu / mps
    num_workers: int = 4
    pin_memory: bool = True
    log_interval: int = 10         # 每隔多少 step 打印一次日志
    checkpoint_dir: str = "checkpoints"
    log_dir: str = "logs"
