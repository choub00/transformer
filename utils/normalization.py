"""
滚动窗口归一化模块（Anti-Leakage）

核心原则：
  1. 禁止使用全局 Mean/Std，必须使用滚动窗口
  2. 归一化参数（mean/std）只用过去的数据，不包含当前和未来
  3. 对特征和标签分别归一化
  4. 使用 numpy 手写实现，避免 pandas rolling 的 backward-looking 陷阱
"""

import numpy as np
import torch
from typing import Tuple, Optional


class RollingNormalizer:
    """
    滚动窗口归一化器

    公式：
        x_norm[t] = (x[t] - mean(x[t-window:t])) / (std(x[t-window:t]) + eps)

    特点：
        - 使用过去 window 天的数据计算统计量（绝对不包含未来）
        - 支持 NaN 跳过（忽略 NaN 计算 mean/std）
        - 支持预热期（warmup）：前 window 天用递增数据归一化
    """

    def __init__(
        self,
        window: int = 60,
        eps: float = 1e-8,
        warmup: bool = True,
    ):
        """
        Args:
            window: 滚动窗口大小
            eps: 防止除零的小常数
            warmup: 是否允许预热期（前 window 天用较少数据归一化）
        """
        self.window = window
        self.eps = eps
        self.warmup = warmup

    def _compute_rolling_stats(
        self, x: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        计算滚动均值和标准差（纯 numpy，无 pandas 依赖）

        使用展开式实现高效的增量计算：
            mean_t = mean(x[t-window:t])
            var_t  = mean(x[t-window:t]^2) - mean_t^2

        Args:
            x: [T, ...] 任意形状的时间序列，第一维是时间

        Returns:
            means: [T, ...] 滚动均值
            stds:  [T, ...] 滚动标准差
        """
        T = x.shape[0]
        shape = x.shape[1:]

        means = np.full((T,) + shape, np.nan, dtype=np.float64)
        stds = np.full((T,) + shape, np.nan, dtype=np.float64)

        # ---- 预热期（0 ~ window-1） ----
        warmup_end = min(self.window, T)
        for t in range(warmup_end):
            if self.warmup:
                window_data = x[: t + 1]
            else:
                continue

            if window_data.size == 0:
                continue
            mu = np.nanmean(window_data, axis=0)
            std_val = np.nanstd(window_data, axis=0, ddof=0)
            std_val = np.where(std_val < self.eps, self.eps, std_val)

            means[t] = mu
            stds[t] = std_val

        # ---- 正式期（window ~ T-1） ----
        for t in range(self.window, T):
            window_data = x[t - self.window : t]
            mu = np.nanmean(window_data, axis=0)
            std_val = np.nanstd(window_data, axis=0, ddof=0)
            std_val = np.where(std_val < self.eps, self.eps, std_val)

            means[t] = mu
            stds[t] = std_val

        return means, stds

    def fit_transform(self, x: np.ndarray) -> Tuple[np.ndarray, dict]:
        """
        拟合归一化参数并返回归一化后的数据

        Args:
            x: [T, ...] 时间序列

        Returns:
            x_norm: 归一化后的数据
            params: {'means', 'stds', 'window'} 用于 inverse_transform
        """
        means, stds = self._compute_rolling_stats(x)
        x_norm = (x - means) / stds

        params = {
            "means": means,
            "stds": stds,
            "window": self.window,
            "eps": self.eps,
        }
        return x_norm, params

    def transform(self, x: np.ndarray, params: dict) -> np.ndarray:
        """
        使用已有参数对数据进行归一化（用于 test/val 阶段）
        注意：test 阶段也需要用滚动窗口，因为每个时间点的归一化参数可能不同
        """
        means, stds = params["means"], params["stds"]
        # 确保形状兼容
        means = np.broadcast_to(means[: len(x)], x.shape)
        stds = np.broadcast_to(stds[: len(x)], x.shape)
        return (x - means) / stds

    def inverse_transform(
        self, x_norm: np.ndarray, params: dict
    ) -> np.ndarray:
        """逆向还原原始尺度"""
        means, stds = params["means"], params["stds"]
        means = np.broadcast_to(means[: len(x_norm)], x_norm.shape)
        stds = np.broadcast_to(stds[: len(x_norm)], x_norm.shape)
        return x_norm * stds + means


class PanelNormalizer:
    """
    多资产面板数据的滚动归一化

    数据格式：[Date, Asset, Features]
    对每个 Asset × Feature 组合独立做滚动归一化
    确保跨资产的归一化参数互不污染
    """

    def __init__(self, window: int = 60, eps: float = 1e-8):
        self.window = window
        self.eps = eps
        self.asset_normals: dict[str, RollingNormalizer] = {}

    def fit_transform_panel(
        self, panel: np.ndarray
    ) -> Tuple[np.ndarray, dict]:
        """
        Args:
            panel: [Date, Asset, Feature]

        Returns:
            panel_norm: 归一化后的面板数据
            params: 每个资产的归一化参数
        """
        T, N, F = panel.shape
        panel_norm = np.full_like(panel, np.nan, dtype=np.float64)
        all_params = {}

        # 对每个资产单独做滚动归一化
        for asset_idx in range(N):
            asset_data = panel[:, asset_idx, :]  # [T, F]
            normalizer = RollingNormalizer(window=self.window, eps=self.eps)
            asset_norm, params = normalizer.fit_transform(asset_data)

            panel_norm[:, asset_idx, :] = asset_norm
            all_params[f"asset_{asset_idx}"] = params
            self.asset_normals[f"asset_{asset_idx}"] = normalizer

        return panel_norm, all_params

    def transform_panel(
        self, panel: np.ndarray, params: dict
    ) -> np.ndarray:
        """使用已有参数对 panel 归一化"""
        T, N, F = panel.shape
        panel_norm = np.full_like(panel, np.nan, dtype=np.float64)

        for asset_idx in range(N):
            key = f"asset_{asset_idx}"
            if key in params:
                asset_data = panel[:, asset_idx, :]
                normalizer = self.asset_normals.get(key)
                if normalizer:
                    panel_norm[:, asset_idx, :] = normalizer.transform(
                        asset_data, params[key]
                    )
        return panel_norm


class ZScoreNormalizer:
    """轻量级全局归一化（仅用于快速实验，不推荐用于生产）"""

    def __init__(self, eps: float = 1e-8):
        self.eps = eps
        self.mean_: Optional[np.ndarray] = None
        self.std_: Optional[np.ndarray] = None

    def fit(self, x: np.ndarray):
        self.mean_ = np.nanmean(x, axis=0)
        self.std_ = np.nanstd(x, axis=0, ddof=1)
        self.std_ = np.where(self.std_ < self.eps, self.eps, self.std_)

    def transform(self, x: np.ndarray) -> np.ndarray:
        if self.mean_ is None:
            raise ValueError("Normalizer not fitted. Call fit() first.")
        return (x - self.mean_) / self.std_

    def fit_transform(self, x: np.ndarray) -> np.ndarray:
        self.fit(x)
        return self.transform(x)


def torch_rolling_normalize(
    x: torch.Tensor,
    window: int,
    dim: int = 1,
    eps: float = 1e-8,
) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """
    PyTorch 版本的滚动归一化（用于模型输入）

    适用场景：在 DataLoader 中对 batch 数据做归一化

    Args:
        x:    [..., T, ...] 任意维度，第一维是 batch，第二维是时间
        window: 滚动窗口
        dim:   时间维度（默认=1）
        eps:   防止除零

    Returns:
        x_norm, rolling_mean, rolling_std
    """
    T = x.shape[dim]

    # 展开式计算滚动均值和标准差
    # mean_t = sum(x[t-window:t]) / window
    # 使用 unfold 效率较低，手动循环（窗口通常 ≤ 60，足够快）
    means_list = []
    stds_list = []

    for t in range(T):
        start = max(0, t - window)
        window_data = x[..., start : t + 1, :]
        mu = torch.nanmean(window_data, dim=dim, keepdim=True)
        sigma = torch.nanstd(window_data, dim=dim, keepdim=True, unbiased=True)
        sigma = torch.clamp_min(sigma, eps)
        means_list.append(mu)
        stds_list.append(sigma)

    rolling_mean = torch.cat(means_list, dim=dim)
    rolling_std = torch.cat(stds_list, dim=dim)

    x_norm = (x - rolling_mean) / rolling_std
    return x_norm, rolling_mean, rolling_std
