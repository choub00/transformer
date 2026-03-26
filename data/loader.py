"""
数据加载与预处理模块（严格 Anti-Leakage）

核心原则：
  1. 所有未来数据不得进入当前时间点的特征
  2. 目标值使用显式 shift(-1) + shift(-2) + shift(-3) 加和构造
  3. 归一化参数仅使用过去数据
  4. 数据集划分严格按时间顺序（绝对不打乱！）
"""

import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
from typing import Tuple, List, Optional
from sklearn.model_selection import train_test_split

from utils.normalization import RollingNormalizer, PanelNormalizer


class AlphaDataset(Dataset):
    """
    多资产时间序列数据集

    数据格式：
        features:  [num_samples, num_assets, history_len, num_features]
        targets:   [num_samples, num_assets]

    样本构建逻辑（严格时序）：
        样本 i 的时间索引 = train_start + history_len + i
        样本 i 的特征 = data[time_idx - history_len : time_idx]  （只用过去）
        样本 i 的标签 = target[time_idx - 1]                     （shift(-1)）
    """

    def __init__(
        self,
        features: np.ndarray,
        targets: np.ndarray,
        asset_ids: Optional[np.ndarray] = None,
        transform=None,
    ):
        """
        Args:
            features:  [num_samples, num_assets, history_len, num_features]
            targets:   [num_samples, num_assets]  未来3日对数收益均值
            asset_ids: [num_assets]  资产 ID（用于 V2 模型）
            transform: 数据变换函数
        """
        assert features.ndim == 4, f"features 必须是 4D，实际为 {features.ndim}D"
        assert targets.ndim == 2, f"targets 必须是 2D，实际为 {targets.ndim}D"
        assert features.shape[0] == targets.shape[0]
        assert features.shape[1] == targets.shape[1]

        self.features = features.astype(np.float32)
        self.targets = targets.astype(np.float32)
        self.asset_ids = asset_ids
        self.transform = transform
        self.num_samples, self.num_assets = targets.shape

    def __len__(self) -> int:
        return self.num_samples

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        x = torch.from_numpy(self.features[idx])
        y = torch.from_numpy(self.targets[idx]).unsqueeze(-1)  # [num_assets, 1]

        if self.asset_ids is not None:
            asset_ids = torch.from_numpy(self.asset_ids).long()
        else:
            asset_ids = None

        if self.transform:
            x = self.transform(x)

        return x, y, asset_ids


class DataProcessor:
    """
    数据预处理流水线（Anti-Leakage 版本）

    处理步骤（严格时序）：
        1. 计算对数收益率（shift(-1) 构造）
        2. 计算目标值（显式 shift(-1) + shift(-2) + shift(-3)）
        3. 滚动窗口归一化（仅用过去数据）
        4. 时间顺序划分（不打乱）
        5. 构建样本窗口
    """

    def __init__(
        self,
        history_len: int = 60,
        target_horizon: int = 3,
        norm_window: int = 60,
        train_ratio: float = 0.7,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15,
        eps: float = 1e-8,
    ):
        self.history_len = history_len
        self.target_horizon = target_horizon
        self.norm_window = norm_window
        self.train_ratio = train_ratio
        self.val_ratio = val_ratio
        self.test_ratio = test_ratio
        self.eps = eps

        self.feature_normalizer: Optional[PanelNormalizer] = None
        self.target_normalizer: Optional[PanelNormalizer] = None
        self.feature_params: Optional[dict] = None
        self.target_params: Optional[dict] = None

    def process_raw_data(
        self,
        price_df: pd.DataFrame,
        features_df: Optional[pd.DataFrame] = None,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, List[str], dict]:
        """
        处理原始价格数据，生成模型输入

        Args:
            price_df:  [Date, Asset] 收盘价（Raw Close Price）
            features_df: [Date, Asset, Feature] 可选的技术指标面板

        Returns:
            features:  [num_samples, num_assets, history_len, num_features]
            targets:   [num_samples, num_assets]
            dates:     样本对应的日期列表
            asset_names: 资产名称列表
            params:    归一化参数（用于 inference）
        """
        # ---- Step 1: 验证数据格式 ----
        assert isinstance(price_df, pd.DataFrame)
        assert price_df.index.name == "date" or isinstance(price_df.index, pd.DatetimeIndex)

        asset_names = price_df.columns.tolist()
        num_assets = len(asset_names)
        dates = price_df.index.tolist()
        num_dates = len(dates)

        # ---- Step 2: 计算对数收益率 ----
        # r_t = ln(P_t / P_{t-1}) — 只用当前和过去价格，无泄露
        log_returns = np.log(price_df.values[1:] / (price_df.values[:-1] + self.eps) + 1)
        dates_logret = dates[1:]  # 从第2天开始有收益率

        log_returns_df = pd.DataFrame(
            log_returns,
            index=pd.DatetimeIndex(dates_logret),
            columns=asset_names,
        )

        # ---- Step 3: 计算目标值（核心防泄露） ----
        # target_return = (r_{t} + r_{t+1} + r_{t+2}) / 3
        # 显式写法，禁止用 rolling(3).mean()（默认 backward-looking 会有问题）
        target_returns = (
            log_returns_df.shift(-1).fillna(0) +
            log_returns_df.shift(-2).fillna(0) +
            log_returns_df.shift(-3).fillna(0)
        ) / self.target_horizon

        # 最后 3 行无法计算完整 3 日均值，剔除
        valid_dates = dates_logret[:-self.target_horizon]  # 去掉最后 3 天
        log_returns_df = log_returns_df.loc[valid_dates]
        target_returns = target_returns.loc[valid_dates]

        # ---- Step 4: 合并技术指标（可选） ----
        if features_df is not None:
            # features_df: [Date, Asset, Feature] 或 [Date, Asset]
            if features_df.ndim == 2:
                # [Date, Asset] → reshape to [Date, Asset, 1]
                feat_array = features_df.values[:, :, np.newaxis]
            else:
                feat_array = features_df.values

            # 只取与 valid_dates 重叠的部分
            common_dates_feat = features_df.index.intersection(log_returns_df.index)
            feat_array = feat_array[features_df.index.get_indexer_for(common_dates_feat)]

            # concat log_returns + features
            combined_data = np.concatenate(
                [
                    log_returns_df.values[:, :, np.newaxis],
                    feat_array,
                ],
                axis=-1,
            )  # [valid_dates, num_assets, 1 + num_features]
        else:
            # 只有对数收益率作为特征
            combined_data = log_returns_df.values[:, :, np.newaxis]

        # ---- Step 5: 滚动窗口归一化 ----
        panel_normalizer = PanelNormalizer(window=self.norm_window, eps=self.eps)
        combined_norm, feature_params = panel_normalizer.fit_transform_panel(combined_data)

        target_normalizer = PanelNormalizer(window=self.norm_window, eps=self.eps)
        target_norm, target_params = target_normalizer.fit_transform_panel(
            target_returns.values[:, :, np.newaxis]
        )

        self.feature_normalizer = panel_normalizer
        self.target_normalizer = target_normalizer
        self.feature_params = feature_params
        self.target_params = target_params

        # ---- Step 6: 构建样本窗口 ----
        # 样本 i: 特征取 [i : i+history_len]，标签取 i+history_len-1
        features_list = []
        targets_list = []

        valid_start = self.norm_window  # 归一化需要至少 norm_window 天 warmup
        valid_end = len(valid_dates)   # 去掉最后 3 天（无完整 target）

        for t in range(valid_start, valid_end):
            feat_window = combined_norm[t - self.history_len : t]  # [history_len, assets, features]
            target_val = target_norm[t]                           # [assets]
            features_list.append(feat_window)
            targets_list.append(target_val)

        features = np.stack(features_list, axis=0).astype(np.float32)  # [N, A, T, F]
        targets = np.stack(targets_list, axis=0).astype(np.float32)    # [N, A]

        sample_dates = valid_dates[valid_start:valid_end]

        params = {
            "feature_params": feature_params,
            "target_params": target_params,
            "num_assets": num_assets,
            "num_features": combined_data.shape[-1],
            "history_len": self.history_len,
            "norm_window": self.norm_window,
        }

        return features, targets, sample_dates, asset_names, params

    def split_data(
        self,
        features: np.ndarray,
        targets: np.ndarray,
        dates: List[str],
    ) -> Tuple[dict, dict, dict]:
        """
        按时间顺序划分数据集（绝对不打乱！）

        Returns:
            {'train': (X, y), 'val': (X, y), 'test': (X, y)}
        """
        n = len(features)
        train_end = int(n * self.train_ratio)
        val_end = int(n * (self.train_ratio + self.val_ratio))

        train_data = {
            "features": features[:train_end],
            "targets": targets[:train_end],
            "dates": dates[:train_end],
        }
        val_data = {
            "features": features[train_end:val_end],
            "targets": targets[train_end:val_end],
            "dates": dates[train_end:val_end],
        }
        test_data = {
            "features": features[val_end:],
            "targets": targets[val_end:],
            "dates": dates[val_end:],
        }

        return train_data, val_data, test_data

    def create_dataloaders(
        self,
        train_data: dict,
        val_data: dict,
        test_data: dict,
        batch_size: int = 32,
        num_workers: int = 4,
        pin_memory: bool = True,
        asset_ids: Optional[np.ndarray] = None,
    ) -> Tuple[DataLoader, DataLoader, DataLoader]:
        """
        创建 PyTorch DataLoader
        注意：shuffle=False（时间序列绝对不打乱！）
        """
        def make_dataset(data_dict):
            return AlphaDataset(
                features=data_dict["features"],
                targets=data_dict["targets"],
                asset_ids=asset_ids,
            )

        train_loader = DataLoader(
            make_dataset(train_data),
            batch_size=batch_size,
            shuffle=False,   # 时间序列不打乱！
            num_workers=num_workers,
            pin_memory=pin_memory,
            drop_last=True,  # 最后不完整的 batch 丢弃
        )

        val_loader = DataLoader(
            make_dataset(val_data),
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=pin_memory,
            drop_last=False,
        )

        test_loader = DataLoader(
            make_dataset(test_data),
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=pin_memory,
            drop_last=False,
        )

        return train_loader, val_loader, test_loader


def create_synthetic_data(
    num_dates: int = 1000,
    num_assets: int = 16,
    num_features: int = 8,
    seed: int = 42,
) -> pd.DataFrame:
    """
    生成合成价格数据用于测试

    Args:
        num_dates:  交易日数量
        num_assets: 资产数量
        seed:       随机种子
    """
    np.random.seed(seed)

    dates = pd.date_range(start="2020-01-01", periods=num_dates, freq="B")
    asset_names = [f"Asset_{i:02d}" for i in range(num_assets)]

    # 随机游走 + 趋势
    log_returns = np.random.randn(num_dates, num_assets) * 0.02
    trend = np.linspace(0, 0.001, num_dates)[:, np.newaxis]
    log_returns += trend

    # 还原价格（任意初始价格，取 100）
    price = 100 * np.exp(np.cumsum(log_returns, axis=0))
    price[0] = 100

    price_df = pd.DataFrame(price, index=dates, columns=asset_names)
    price_df.index.name = "date"

    return price_df


# ------------------------------------------------------------------
# 便捷入口：完整数据处理流水线
# ------------------------------------------------------------------

def build_dataloaders(
    price_df: pd.DataFrame,
    features_df: Optional[pd.DataFrame] = None,
    history_len: int = 60,
    target_horizon: int = 3,
    norm_window: int = 60,
    batch_size: int = 32,
    train_ratio: float = 0.7,
    val_ratio: float = 0.15,
) -> Tuple[DataLoader, DataLoader, DataLoader, dict]:
    """
    一键构建完整数据流水线

    Example:
        >>> price_df = create_synthetic_data()
        >>> train_loader, val_loader, test_loader, params = build_dataloaders(price_df)
    """
    processor = DataProcessor(
        history_len=history_len,
        target_horizon=target_horizon,
        norm_window=norm_window,
        train_ratio=train_ratio,
        val_ratio=val_ratio,
    )

    features, targets, sample_dates, asset_names, params = processor.process_raw_data(
        price_df, features_df
    )

    train_data, val_data, test_data = processor.split_data(features, targets, sample_dates)

    asset_ids = np.arange(len(asset_names))
    train_loader, val_loader, test_loader = processor.create_dataloaders(
        train_data, val_data, test_data,
        batch_size=batch_size,
        asset_ids=asset_ids,
    )

    params["asset_names"] = asset_names

    return train_loader, val_loader, test_loader, params
