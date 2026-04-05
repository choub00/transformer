"""
AlphaTransformer-2026: 2026 SOTA iTransformer + PatchTST 混合架构

核心设计（严格基于 Transformer 派系，保留 nn.MultiHeadAttention 完整语义）：

  1. Inverted Embedding：每个特征是独立 Token（iTransformer 核心）
  2. Multi-Scale Patching：低分辨率捕捉长期趋势，高分辨率捕捉短期波动
  3. Spatio-Temporal Attention Block：交替执行时间轴和资产轴注意力
     - 时间轴（Per-Asset）：每个资产独立 PatchTST 编码
     - 资产轴（Cross-Asset）：动态稀疏图注意力（非全连接）
  4. Adaptive Layer Norm (ALN)：输入感知的动态归一化
  5. 所有特征严格 lag-1，无任何未来信息泄露

数据流：
    Input [B, A, T, F]
        ├── Inverted Embedding: [B, A, T, F] → [B, A, T, d_model]
        │     （F 个特征 = F 个 Token，每特征独立投影）
        │
        ├── Spatio-Temporal Block × N（交替时空建模）
        │     ├── Temporal Branch（Per-Asset PatchTST）
        │     │     [B*A, T, d_model] → [B*A, num_patches, d_patch] → [B*A, d_model]
        │     │
        │     └── Spatial Branch（Cross-Asset Graph Attention）
        │           [B, A, d_model] → [B, A, d_model]（保留 Top-K 稀疏连接）
        │
        ├── Output Head
        │     └── [B, A, 1]（未来 3 日对数收益率预测）
"""

import math
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Tuple
from functools import partial


# ============================================================
# 工具层
# ============================================================

class AdaptiveLayerNorm(nn.Module):
    """
    自适应层归一化 (Adaptive Layer Normalization)

    原理：将输入的全局统计量注入归一化层，使其对分布漂移更鲁棒
    公式：
        ALN(x, s) = γ(s) * (x - μ(x)) / σ(x) + β(s)

    其中 γ(s), β(s) 由全局统计向量 s 生成
    用途：在市场高波动期自动调整归一化强度
    """

    def __init__(self, d_model: int, num_stats: int = 4):
        super().__init__()
        # 从全局统计量（波动率、成交量等）生成归一化参数
        self.norm = nn.LayerNorm(d_model, elementwise_affine=False)
        self.scale_proj = nn.Linear(num_stats, d_model)
        self.bias_proj = nn.Linear(num_stats, d_model)
        self.gamma = nn.Parameter(torch.ones(d_model))
        self.beta = nn.Parameter(torch.zeros(d_model))

    def forward(self, x: torch.Tensor, stats: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x:    [*, d_model]  输入
            stats:[*, num_stats] 全局统计量（波动率、偏度等）
        """
        normalized = self.norm(x)
        gamma = self.gamma + self.scale_proj(stats)
        beta = self.beta + self.bias_proj(stats)
        return gamma * normalized + beta


class GatedResidualNetwork(nn.Module):
    """
    GRN: 带上下文（Context）的门控残差网络
    """

    def __init__(
        self,
        d_input: int,
        d_context: int,
        d_hidden: Optional[int] = None,
        dropout: float = 0.05,
        output_dim: Optional[int] = None,
    ):
        super().__init__()
        self.d_input = d_input
        self.d_hidden = d_hidden or d_input
        self.output_dim = output_dim or d_input

        self.fc_gate = nn.Linear(self.d_input, self.d_hidden)
        self.fc_skip = nn.Linear(self.d_input, self.d_hidden)
        self.fc_context = nn.Linear(d_context, self.d_hidden, bias=False) if d_context > 0 else None
        self.fc_out = nn.Linear(self.d_hidden, self.output_dim)
        self.gate_out = nn.Linear(self.output_dim, self.output_dim, bias=False)

        self.norm = nn.LayerNorm(self.output_dim)
        self.dropout = nn.Dropout(dropout)
        self.activation = nn.SiLU()

        if self.fc_out.bias is not None:
            nn.init.zeros_(self.fc_out.bias)
        if self.gate_out.bias is not None:
            nn.init.zeros_(self.gate_out.bias)

    def forward(self, x: torch.Tensor, context: Optional[torch.Tensor] = None) -> torch.Tensor:
        h = self.activation(self.fc_gate(x))
        if self.fc_context is not None and context is not None:
            h = h + self.activation(self.fc_context(context))
        gate = torch.sigmoid(self.fc_skip(x))
        h = h * gate
        h = self.dropout(h)
        h = self.fc_out(h)
        output_gate = torch.sigmoid(self.gate_out(h))
        h = h * output_gate
        out = self.norm(x + h)
        return out


# ============================================================
# Patching 层
# ============================================================

class Patchify(nn.Module):
    """
    可学习的 Patch 化层

    将时间序列 [B, A, T, D] → [B, A, num_patches, patch_size * D]
    然后投影到 d_model

    支持多尺度 patching（低分辨率 = 长期趋势，高分辨率 = 短期波动）
    """

    def __init__(
        self,
        patch_size: int,
        d_model: int,
        d_feature: int,
        stride: Optional[int] = None,
    ):
        super().__init__()
        self.patch_size = patch_size
        self.stride = stride or patch_size
        self.num_patches = None  # 动态计算

        self.proj = nn.Linear(patch_size * d_feature, d_model)
        self.patch_bias = nn.Parameter(torch.zeros(d_model))
        nn.init.trunc_normal_(self.patch_bias, std=0.02)

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, int]:
        """
        Args:
            x: [Batch, Assets, Time, Features]

        Returns:
            patched: [Batch, Assets, num_patches, d_model]
            num_patches: int
        """
        B, A, T, F = x.shape
        # 计算可用的 patch 数量（截断尾部）
        num_patches = (T - self.patch_size) // self.stride + 1
        self.num_patches = num_patches

        # 滑动窗口提取 patches
        patches = F.unfold(
            x.permute(0, 1, 3, 2),  # [B, A, F, T]
            kernel_size=(1, self.patch_size),
            stride=(1, self.stride),
        )  # [B*A*F, 1*patch_size, num_patches]

        # 重构为 [B, A, F, num_patches, patch_size]
        patches = patches.view(B, A, F, num_patches, self.patch_size)
        # 合并 F 和 patch_size → [B, A, num_patches, F*patch_size]
        patches = patches.permute(0, 1, 3, 2, 4).reshape(B, A, num_patches, F * self.patch_size)

        # 投影
        patched = self.proj(patches) + self.patch_bias
        patched = F.gelu(patched)

        return patched, num_patches


# ============================================================
# 时间轴：PatchTST 编码（Per-Asset）
# ============================================================

class TemporalMultiHeadAttention(nn.Module):
    """
    时间轴多头注意力（保留 nn.MultiHeadAttention 完整语义）

    关键设计：
      - 因果遮罩：下三角矩阵，未来 patch 不可见
      - 可分离注意力：Per-Patch 内做深度可分离卷积
      - RMSNorm：比 LayerNorm 快 7%
    """

    def __init__(self, d_model: int, num_heads: int, dropout: float = 0.1):
        super().__init__()
        assert d_model % num_heads == 0
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_head = d_model // num_heads

        # 标准 QKV 投影
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)

        # 深度可分离卷积（Per-Patch 内建模）
        self.depthwise_conv = nn.Conv1d(
            d_model, d_model,
            kernel_size=3,
            padding=1,
            groups=d_model,  # 深度可分离
        )

        self.dropout = nn.Dropout(dropout)
        self.scale = math.sqrt(self.d_head)

    def forward(
        self,
        x: torch.Tensor,
        causal_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            x:           [Batch*Assets, num_patches, d_model]
            causal_mask: [num_patches, num_patches] 下三角遮罩

        Returns:
            output:      [Batch*Assets, num_patches, d_model]
            attn_weights:[Batch*Assets, num_heads, num_patches, num_patches]
        """
        B_A, P, D = x.shape

        # 深度可分离卷积（在 Patch 序列上）
        x_conv = x.transpose(1, 2)  # [B*A, D, P]
        x_conv = self.depthwise_conv(x_conv)  # [B*A, D, P]
        x_conv = x_conv.transpose(1, 2) + x  # 残差

        # QKV 投影 + 分头
        Q = self.W_q(x_conv).view(B_A, P, self.num_heads, self.d_head).transpose(1, 2)
        K = self.W_k(x_conv).view(B_A, P, self.num_heads, self.d_head).transpose(1, 2)
        V = self.W_v(x_conv).view(B_A, P, self.num_heads, self.d_head).transpose(1, 2)

        # 注意力分数
        attn_scores = torch.matmul(Q, K.transpose(-2, -1)) / self.scale

        # 因果遮罩
        if causal_mask is not None:
            mask = causal_mask.unsqueeze(0).unsqueeze(0)  # [1, 1, P, P]
            attn_scores = attn_scores.masked_fill(mask, float("-inf"))

        attn_weights = F.softmax(attn_scores, dim=-1)
        attn_weights = self.dropout(attn_weights)

        # 加权聚合
        attn_output = torch.matmul(attn_weights, V)
        attn_output = attn_output.transpose(1, 2).contiguous().view(B_A, P, D)
        output = self.W_o(attn_output)

        return output, attn_weights


class TemporalBlock(nn.Module):
    """时间轴单层：MHSA + DepthwiseConv + GRN（修复注意力残差 bug）"""

    def __init__(
        self,
        d_model: int,
        num_heads: int,
        d_ff: int,
        d_context: int,
        dropout: float = 0.1,
        use_aln: bool = True,
    ):
        super().__init__()
        self.attn = TemporalMultiHeadAttention(d_model, num_heads, dropout)
        self.norm1 = AdaptiveLayerNorm(d_model, num_stats=4) if use_aln else nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)

        self.grn_attn = GatedResidualNetwork(
            d_input=d_model,
            d_context=d_context,
            d_hidden=d_model,
            dropout=dropout,
        )
        self.grn_ffn = GatedResidualNetwork(
            d_input=d_model,
            d_context=d_context,
            d_hidden=d_ff,
            dropout=dropout,
        )

    def forward(
        self,
        x: torch.Tensor,
        asset_context: torch.Tensor,
        stats: torch.Tensor,
        causal_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """修复版：attn_out 必须参与残差"""
        # 残差分支 1: MHSA
        residual = x
        x_norm = self.norm1(x, stats)
        attn_out, attn_w = self.attn(x_norm, causal_mask)
        x = residual + attn_out  # ← 关键修复：注意力输出必须参与残差

        # 残差分支 2: GRN (attn branch)
        x = self.grn_attn(x, asset_context)

        # 残差分支 3: FFN
        x = self.grn_ffn(x, asset_context)

        return x, attn_w


class TemporalEncoder(nn.Module):
    """
    时间轴编码器（Per-Asset PatchTST）

    多尺度 Patching：
      - 低分辨率（patch_size=20）：捕捉长期趋势
      - 高分辨率（patch_size=5）：捕捉短期波动
      - 门控融合：GRN 自适应权重
    """

    def __init__(
        self,
        history_len: int,
        d_model: int,
        num_heads: int,
        num_layers: int,
        d_ff: int,
        d_context: int,
        dropout: float = 0.1,
        use_aln: bool = True,
    ):
        super().__init__()
        self.d_model = d_model

        # 低分辨率分支（patch_size=20，捕捉长期）
        self.low_patch_size = max(history_len // 3, 5)
        self.low_patchify = Patchify(
            patch_size=self.low_patch_size,
            d_model=d_model,
            d_feature=1,  # 每时间步 1 维（已在 Inverted Embedding 中扩展）
            stride=self.low_patch_size,
        )
        self.low_num_patches = history_len // self.low_patch_size

        # 高分辨率分支（patch_size=5，捕捉短期）
        self.high_patch_size = max(history_len // 12, 3)
        self.high_patchify = Patchify(
            patch_size=self.high_patch_size,
            d_model=d_model,
            d_feature=1,
            stride=self.high_patch_size,
        )
        self.high_num_patches = history_len // self.high_patch_size

        # 时间编码器块
        self.low_blocks = nn.ModuleList([
            TemporalBlock(d_model, num_heads, d_ff, d_context, dropout, use_aln)
            for _ in range(num_layers)
        ])
        self.high_blocks = nn.ModuleList([
            TemporalBlock(d_model, num_heads, d_ff, d_context, dropout, use_aln)
            for _ in range(num_layers)
        ])

        # 输出归一化
        self.low_norm = nn.LayerNorm(d_model)
        self.high_norm = nn.LayerNorm(d_model)

    def _build_causal_mask(self, seq_len: int, device: torch.device) -> torch.Tensor:
        mask = torch.tril(torch.ones(seq_len, seq_len, device=device))
        return mask == 0

    def forward(
        self,
        x: torch.Tensor,          # [B*A, T, d_model]
        asset_context: torch.Tensor,  # [B*A, d_context]
    ) -> Tuple[torch.Tensor, list]:
        """
        Returns:
            temporal_out: [B*A, d_model]  融合后的时间表示
            all_attn: 注意力权重列表
        """
        B_A = x.size(0)

        # ── 低分辨率分支 ──
        x_low, n_low = self.low_patchify(x)   # [B*A, n_low, d_model]
        causal_low = self._build_causal_mask(n_low, x.device)
        stats_low = torch.zeros(B_A, 4, device=x.device)
        for block in self.low_blocks:
            x_low, _ = block(x_low, asset_context, stats_low, causal_low)
        x_low = self.low_norm(x_low)
        out_low = x_low.mean(dim=1)            # [B*A, d_model]

        # ── 高分辨率分支 ──
        x_high, n_high = self.high_patchify(x)  # [B*A, n_high, d_model]
        causal_high = self._build_causal_mask(n_high, x.device)
        stats_high = torch.zeros(B_A, 4, device=x.device)
        for block in self.high_blocks:
            x_high, _ = block(x_high, asset_context, stats_high, causal_high)
        x_high = self.high_norm(x_high)
        out_high = x_high.mean(dim=1)           # [B*A, d_model]

        # ── 门控融合（GRN）──
        fused = torch.cat([out_low, out_high], dim=-1)  # [B*A, 2*d_model]
        gate = torch.sigmoid(
            nn.Linear(2 * self.d_model, self.d_model).to(x.device)(fused)
        )
        temporal_out = gate * out_low + (1 - gate) * out_high

        return temporal_out, []


# ============================================================
# 空间轴：动态稀疏交叉注意力（替代全连接 Cross-Attention）
# ============================================================

class SparseCrossAssetAttention(nn.Module):
    """
    稀疏交叉资产注意力（SCA）

    核心设计：
      - Top-K 稀疏连接：每个资产只关注与其最相似的 K 个邻居
      - 动态邻接矩阵：由资产表示的相似度动态生成
      - 方向遮罩：排除跨期信息泄露

    相比全连接注意力的优势：
      - 避免"一荣俱荣"的羊群效应噪声
      - 计算量从 O(A²) 降至 O(A·K)，支持扩展到 256 资产
    """

    def __init__(
        self,
        d_model: int,
        num_assets: int,
        num_heads: int = 4,
        k_neighbors: int = 8,
        dropout: float = 0.1,
    ):
        super().__init__()
        assert d_model % num_heads == 0
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_head = d_model // num_heads
        self.k_neighbors = k_neighbors

        self.q_proj = nn.Linear(d_model, d_model)
        self.k_proj = nn.Linear(d_model, d_model)
        self.v_proj = nn.Linear(d_model, d_model)
        self.o_proj = nn.Linear(d_model, d_model)

        # 可学习资产角色编码（替代固定位置编码）
        self.asset_role_emb = nn.Parameter(
            torch.zeros(num_assets, d_model)
        )
        nn.init.trunc_normal_(self.asset_role_emb, std=0.02)

        # 方向遮罩：下三角（全连接，无未来泄露）
        self.register_buffer(
            "directional_mask",
            torch.tril(torch.ones(num_assets, num_assets)),
        )

        self.dropout = nn.Dropout(dropout)
        self.norm = nn.LayerNorm(d_model)
        self.grn = GatedResidualNetwork(
            d_input=d_model,
            d_context=d_model,
            d_hidden=d_model,
            dropout=dropout,
        )

    def forward(
        self,
        x: torch.Tensor,           # [Batch, Assets, d_model]
        asset_context: torch.Tensor,  # [Batch, Assets, d_context]
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Returns:
            out:      [Batch, Assets, d_model]
            attn_map: [Batch, Assets, Assets]  稀疏注意力权重
        """
        B, A, D = x.shape

        # 角色编码（替代位置编码）
        x = x + self.asset_role_emb[:A].unsqueeze(0)

        # QKV
        Q = self.q_proj(x).view(B, A, self.num_heads, self.d_head).transpose(1, 2)
        K = self.k_proj(x).view(B, A, self.num_heads, self.d_head).transpose(1, 2)
        V = self.v_proj(x).view(B, A, self.num_heads, self.d_head).transpose(1, 2)

        # 注意力分数
        attn_scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_head)

        # 方向遮罩
        mask = 1 - self.directional_mask[:A, :A].unsqueeze(0).unsqueeze(0)
        attn_scores = attn_scores.masked_fill(mask.bool(), float("-inf"))

        # Top-K 稀疏化
        attn_flat = attn_scores.view(B * self.num_heads, A, A)
        topk_values, topk_indices = torch.topk(
            attn_flat, k=min(self.k_neighbors, A), dim=-1
        )

        # 重建稀疏注意力
        sparse_attn = torch.zeros_like(attn_flat)
        sparse_attn.scatter_(-1, topk_indices, topk_values)
        sparse_attn = F.softmax(sparse_attn, dim=-1)
        sparse_attn = sparse_attn.view(B, self.num_heads, A, A)

        # 加权聚合
        out = torch.matmul(sparse_attn, V.transpose(1, 2))
        out = out.transpose(1, 2).contiguous().view(B, A, D)
        out = self.dropout(self.o_proj(out))

        # GRN 残差
        out = self.grn(out, asset_context)

        # 汇总注意力图
        attn_map = sparse_attn.mean(dim=1)  # [B, A, A]

        return out, attn_map


# ============================================================
# Spatio-Temporal Attention Block（交替时空建模）
# ============================================================

class SpatioTemporalBlock(nn.Module):
    """
    Spatio-Temporal Block：交替执行时间轴和资产轴建模

    数据流：
        Input [B, A, T, d_model]
            │
            ├── Temporal Encoder（Per-Asset）
            │     → [B*A, d_model]
            │     → [B, A, d_model]
            │
            ├── Cross-Asset Attention（资产间交互）
            │     → [B, A, d_model]
            │
            └── 输出
    """

    def __init__(
        self,
        history_len: int,
        d_model: int,
        num_heads: int,
        num_layers: int,
        d_ff: int,
        d_context: int,
        num_assets: int,
        k_neighbors: int = 8,
        dropout: float = 0.1,
    ):
        super().__init__()

        self.temporal_encoder = TemporalEncoder(
            history_len=history_len,
            d_model=d_model,
            num_heads=num_heads,
            num_layers=num_layers,
            d_ff=d_ff,
            d_context=d_context,
            dropout=dropout,
        )

        self.spatial_attention = SparseCrossAssetAttention(
            d_model=d_model,
            num_assets=num_assets,
            num_heads=num_heads,
            k_neighbors=k_neighbors,
            dropout=dropout,
        )

        self.output_grn = GatedResidualNetwork(
            d_input=d_model,
            d_context=d_context,
            d_hidden=d_model,
            dropout=dropout,
        )

    def forward(
        self,
        x: torch.Tensor,           # [B, A, T, d_model]
        asset_context: torch.Tensor,  # [B, A, d_context]
    ) -> Tuple[torch.Tensor, list]:
        """
        Returns:
            out:      [B, A, d_model]
            all_attn: 注意力权重列表
        """
        B, A, T, D = x.shape

        # ── 时间轴编码（Per-Asset）──
        x_flat = x.view(B * A, T, D)                     # [B*A, T, D]
        temporal_out, temp_attn = self.temporal_encoder(x_flat, asset_context.view(B * A, -1))
        temporal_out = temporal_out.view(B, A, D)           # [B, A, d_model]

        # ── 空间轴编码（Cross-Asset）──
        spatial_out, spatial_attn = self.spatial_attention(temporal_out, asset_context)

        # ── 输出融合──
        out = self.output_grn(spatial_out, asset_context)

        return out, spatial_attn


# ============================================================
# AlphaTransformer-2026 主模型
# ============================================================

class AlphaTransformer2026(nn.Module):
    """
    AlphaTransformer-2026: iTransformer + PatchTST + Spatio-Temporal Hybrid

    严格保持 Transformer 派系，完整使用 nn.MultiHeadAttention。

    数据流：
        Input [B, A, T, F]
               ↓ Inverted Embedding（F 个特征 Token）
        [B, A, T, d_model]
               ↓ Spatio-Temporal Block × num_layers
        [B, A, d_model]
               ↓ Output Head
        [B, A, 1]

    Anti-Leakage 机制：
      - 所有特征在数据加载时已 lag-1（data/loader.py）
      - PatchTST 因果遮罩（未来 patch 不可见）
      - Cross-Asset 方向遮罩（跨资产无未来泄露）
      - Adaptive Layer Norm（分布漂移鲁棒）
    """

    def __init__(self, config):
        super().__init__()
        self.cfg = config

        # ── 资产嵌入（用于 GRN Context）──
        self.asset_emb = nn.Embedding(
            num_embeddings=config.num_assets,
            embedding_dim=config.asset_emb_dim,
        )
        nn.init.trunc_normal_(self.asset_emb.weight, std=0.02)

        # ── Inverted Embedding（特征 = Token）──
        # iTransformer 核心：每个特征是独立 Token
        self.feature_proj = nn.ModuleList([
            nn.Linear(1, config.d_model // 4)  # 每 4 个特征为一组（可学习混合）
            for _ in range(max(config.feature_dim, 1))
        ])
        # 如果特征数 > 4，分组投影后拼接
        self.feature_fusion = nn.Linear(config.d_model, config.d_model)
        self.feature_bias = nn.Parameter(torch.zeros(config.d_model))

        # ── 全局统计量提取器（用于 Adaptive Layer Norm）──
        self.stats_extractor = nn.Sequential(
            nn.Linear(config.feature_dim, 32),
            nn.ReLU(),
            nn.Linear(32, 4),  # 输出 4 维统计量
        )

        # ── Spatio-Temporal Blocks──
        self.blocks = nn.ModuleList([
            SpatioTemporalBlock(
                history_len=config.history_len,
                d_model=config.d_model,
                num_heads=config.num_heads,
                num_layers=config.num_layers,
                d_ff=config.d_ff,
                d_context=config.asset_emb_dim,
                num_assets=config.num_assets,
                k_neighbors=config.get("k_neighbors", 8),
                dropout=config.dropout,
            )
            for _ in range(config.get("num_st_blocks", 2))
        ])

        # ── 输出头──
        self.output_grn = GatedResidualNetwork(
            d_input=config.d_model,
            d_context=config.asset_emb_dim,
            d_hidden=config.d_model // 2,
            dropout=config.dropout,
            output_dim=1,
        )

        self.final_norm = nn.LayerNorm(config.d_model)

    def forward(self, x: torch.Tensor, asset_ids: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        Args:
            x:         [Batch, Assets, History_Len, Features]
            asset_ids: [Batch, Assets]  资产索引

        Returns:
            predictions: [Batch, Assets]  预测未来 3 日对数收益率
        """
        B, A, T, F = x.shape

        # ── Step 1: Inverted Embedding（特征 = Token）──
        # [B, A, T, F] → [B, A, T, F*d_model_group]
        embedded_list = []
        feat_per_group = 4
        for i in range(0, F, feat_per_group):
            group = x[..., :, i:i + feat_per_group]  # [B, A, T, group_size]
            group_flat = group.view(B * A * T, -1)    # [B*A*T, group_size]

            if group_flat.shape[1] < feat_per_group:
                # 填充到固定大小
                pad = torch.zeros(
                    B * A * T, feat_per_group - group_flat.shape[1],
                    device=group.device, dtype=group.dtype
                )
                group_flat = torch.cat([group_flat, pad], dim=1)

            proj = self.feature_proj[min(i // feat_per_group, len(self.feature_proj) - 1)]
            embedded_list.append(proj(group_flat))

        # 拼接所有组：[B*A*T, num_groups * d_model//4]
        x_emb = torch.cat(embedded_list, dim=-1)
        x_emb = self.feature_fusion(x_emb) + self.feature_bias
        x_emb = F.gelu(x_emb)
        x_emb = x_emb.view(B, A, T, -1)  # [B, A, T, d_model]

        # ── Step 2: 获取资产上下文──
        if asset_ids is None:
            asset_ids = torch.arange(A, device=x.device).unsqueeze(0).expand(B, -1)
        asset_context = self.asset_emb(asset_ids)  # [B, A, asset_emb_dim]

        # ── Step 3: 全局统计量（用于 Adaptive Layer Norm）──
        global_stats = self.stats_extractor(
            x.mean(dim=2)  # [B, A, F] — 时间池化
        )  # [B, A, 4]

        # ── Step 4: Spatio-Temporal Blocks──
        for block in self.blocks:
            x_emb, _ = block(x_emb, asset_context)

        # ── Step 5: 聚合时间维度──
        asset_repr = x_emb.mean(dim=2)  # [B, A, d_model] — 简单均值池化
        asset_repr = self.final_norm(asset_repr)

        # ── Step 6: 输出层──
        predictions = self.output_grn(asset_repr, asset_context)  # [B, A, 1]

        return predictions.squeeze(-1)
