"""
AlphaTransformer 核心模型
融合 iTransformer / PatchTST / TFT 三大 SOTA 架构

核心设计思想：
  - iTransformer: 将 [Batch, Assets, Time, Features] 视为"资产是 Token"
  - PatchTST: 时间维度按 Patch 分段，降低序列长度，提取局部趋势
  - TFT: GRN 门控残差网络实现资产特异性的特征过滤

输入维度: [Batch, Assets, History_Len, Features]
输出维度: [Batch, Assets, 1]  (每个资产的未来3日对数收益率预测)
"""

import math
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Tuple


# ============================================================
# 1. Gated Residual Network (TFT 风格, 带 Asset Context)
# ============================================================

class GatedResidualNetwork(nn.Module):
    """
    GRN: 带上下文（Context）的门控残差网络

    公式:
        GRN(x, context) = LayerNorm(x + GLU(FC(x) + FC(context)))

    其中 GLU (Gated Linear Unit):
        GLU(a) = sigmoid(W1·a) ⊙ (W2·a)

    作用：
        - context 为 None 时，退化为带 dropout 的残差块
        - context 为 asset_emb 时，实现资产特异性的特征过滤
        - sigmoid 门控自动学习抑制无效特征的贡献
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

        # 门控层: 将输入投影到 d_hidden
        self.fc_gate = nn.Linear(self.d_input, self.d_hidden)
        # 跳跃连接: 将输入投影到 d_hidden（用于 GLU 的非门控路径）
        self.fc_skip = nn.Linear(self.d_input, self.d_hidden)
        # 可选 context 投影
        self.fc_context = nn.Linear(d_context, self.d_hidden, bias=False) if d_context > 0 else None
        # 输出投影: d_hidden → output_dim
        self.fc_out = nn.Linear(self.d_hidden, self.output_dim)
        # 输出门控: 控制最终输出量级
        self.gate_out = nn.Linear(self.output_dim, self.output_dim, bias=False)

        self.norm = nn.LayerNorm(self.output_dim)
        self.dropout = nn.Dropout(dropout)
        self.activation = nn.SiLU()  # SiLU/Swish: 比 ReLU 更平滑的激活

        # 初始化：输出偏置置零（稳定的残差起点）
        nn.init.zeros_(self.fc_out.bias)
        nn.init.zeros_(self.gate_out.bias)

    def forward(self, x: torch.Tensor, context: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        Args:
            x:       [Batch, ..., d_input]  主输入张量
            context: [Batch, ..., d_context] 可选上下文，广播到 x 的所有非批次维度

        Returns:
            [Batch, ..., output_dim]
        """
        # 主路径: x → GLU
        h = self.激活(self.fc_gate(x))  # [B, ..., d_hidden]

        # 上下文接入（可选）
        if self.fc_context is not None and context is not None:
            # context 扩展到与 h 相同的维度
            h = h + self.激活(self.fc_context(context))

        # GLU: sigmoid(门控) ⊙ (跳跃)
        gate = torch.sigmoid(self.fc_skip(x))          # [B, ..., d_hidden] ∈ (0,1)
        h = h * gate                                   # [B, ..., d_hidden]

        h = self.dropout(h)
        h = self.fc_out(h)                             # [B, ..., output_dim]

        # 输出门控（线性，范围 0~1）
        output_gate = torch.sigmoid(self.gate_out(h))  # [B, ..., output_dim]
        h = h * output_gate                            # [B, ..., output_dim]

        # 残差连接（输入和输出维度需对齐）
        out = self.norm(x + h)
        return out


# ============================================================
# 2. 多头注意力（支持时间轴 / 资产轴）
# ============================================================

class MultiHeadAttention(nn.Module):
    """
    标准化 Multi-Head Attention
    支持 Casual Masking（用于时间轴自回归建模）
    """

    def __init__(self, d_model: int, num_heads: int, dropout: float = 0.1):
        super().__init__()
        assert d_model % num_heads == 0, "d_model 必须能被 num_heads 整除"

        self.d_model = d_model
        self.num_heads = num_heads
        self.d_head = d_model // num_heads

        # QKV 投影（将 d_model 映射到 d_model）
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)

        self.dropout = nn.Dropout(dropout)
        self.scale = math.sqrt(self.d_head)

    def forward(
        self,
        query: torch.Tensor,
        key: torch.Tensor,
        value: torch.Tensor,
        attn_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            query/key/value: [Batch, Seq, d_model]
            attn_mask:       [Seq, Seq] 遮罩矩阵（True=遮蔽）

        Returns:
            output: [Batch, Seq, d_model]
            attn_weights: [Batch, num_heads, Seq, Seq]
        """
        B = query.size(0)
        seq_len = query.size(1)

        # QKV 投影 + 分头
        Q = self.W_q(query).view(B, seq_len, self.num_heads, self.d_head).transpose(1, 2)
        K = self.W_k(key).view(B, -1, self.num_heads, self.d_head).transpose(1, 2)
        V = self.W_v(value).view(B, -1, self.num_heads, self.d_head).transpose(1, 2)

        # 注意力分数
        attn_scores = torch.matmul(Q, K.transpose(-2, -1)) / self.scale  # [B, H, Seq, Seq]

        # 因果遮罩（时间轴用）
        if attn_mask is not None:
            attn_scores = attn_scores.masked_fill(attn_mask, float("-inf"))

        attn_weights = F.softmax(attn_scores, dim=-1)
        attn_weights = self.dropout(attn_weights)

        # 加权聚合
        attn_output = torch.matmul(attn_weights, V)          # [B, H, Seq, d_head]
        attn_output = attn_output.transpose(1, 2).contiguous().view(B, seq_len, self.d_model)
        output = self.W_o(attn_output)

        return output, attn_weights


# ============================================================
# 3. 时间轴：Patch-based Temporal Attention (PatchTST)
# ============================================================

class PatchTSTEncoder(nn.Module):
    """
    PatchTST 编码器：对 [Assets, Patches, d_patch] 在时间维度做 Self-Attention

    维度流转（以单个资产为例）:
        [Batch*Assets, History_Len, d_model]
              ↓ Patching (reshape, 无卷积)
        [Batch*Assets, num_patches, patch_size * d_model]
              ↓ Linear Projection
        [Batch*Assets, num_patches, d_model]
              ↓ Add [CLS] Token
        [Batch*Assets, num_patches + 1, d_model]
              ↓ Self-Attention (Causal Mask)
        [Batch*Assets, num_patches + 1, d_model]
              ↓ Mean Pooling over Patches
        [Batch*Assets, d_model]
    """

    def __init__(
        self,
        history_len: int,
        patch_size: int,
        d_model: int,
        num_heads: int,
        num_layers: int,
        d_ff: int,
        grn_context_dim: int,
        dropout: float = 0.1,
        use_cls_token: bool = False,
    ):
        super().__init__()
        self.patch_size = patch_size
        self.num_patches = history_len // patch_size
        self.use_cls_token = use_cls_token

        # Patch Projection: 将 patch_size 个时间步投影到 d_model
        self.patch_proj = nn.Linear(patch_size, d_model)

        # 可学习的 [CLS] Token（参考 BERT / ViT）
        if use_cls_token:
            self.cls_token = nn.Parameter(torch.zeros(1, 1, d_model))
            nn.init.trunc_normal_(self.cls_token, std=0.02)

        # 时间轴 Self-Attention 层
        self.temporal_blocks = nn.ModuleList([
            TemporalAttentionBlock(d_model, num_heads, d_ff, grn_context_dim, dropout)
            for _ in range(num_layers)
        ])

        # 输出投影
        self.norm = nn.LayerNorm(d_model)

    def forward(
        self,
        x: torch.Tensor,
        asset_context: torch.Tensor,
        causal_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[torch.Tensor, list]:
        """
        Args:
            x:             [Batch * Assets, History_Len, d_model]
            asset_context: [Batch * Assets, grn_context_dim]  资产嵌入
            causal_mask:   [num_patches+1, num_patches+1]

        Returns:
            temporal_out: [Batch * Assets, d_model]
            all_attn_weights: 注意力权重列表
        """
        B_A, T, D = x.shape  # Batch*Assets, History_Len, d_model

        # ---- Patching: [B*A, T, D] → [B*A, num_patches, patch_size*D] ----
        x = x.view(B_A, self.num_patches, self.patch_size * D)

        # ---- Patch Projection: [B*A, num_patches, patch_size*D] → [B*A, num_patches, d_model] ----
        x = self.patch_proj(x)  # [B*A, num_patches, d_model]

        # ---- 添加 [CLS] Token ----
        if self.use_cls_token:
            cls_tokens = self.cls_token.expand(B_A, -1, -1)
            x = torch.cat([cls_tokens, x], dim=1)  # [B*A, num_patches+1, d_model]
            if causal_mask is not None:
                # 扩展 causal mask 适配 CLS token
                cls_mask = torch.zeros(
                    causal_mask.size(0), 1,
                    device=causal_mask.device, dtype=causal_mask.dtype
                )
                causal_mask = torch.cat([cls_mask, causal_mask], dim=1)

        # ---- Temporal Self-Attention Blocks ----
        all_attn = []
        for block in self.temporal_blocks:
            x, attn_w = block(x, asset_context, causal_mask)
            all_attn.append(attn_w)

        x = self.norm(x)

        # ---- Patch 聚合策略：Mean Pooling over patches ----
        if self.use_cls_token:
            # 取 CLS token
            temporal_out = x[:, 0, :]  # [B*A, d_model]
        else:
            # 所有 Patch 的均值
            temporal_out = x.mean(dim=1)  # [B*A, d_model]

        return temporal_out, all_attn


class TemporalAttentionBlock(nn.Module):
    """时间轴单层注意力块：MHSA + GRN + FFN"""

    def __init__(
        self,
        d_model: int,
        num_heads: int,
        d_ff: int,
        grn_context_dim: int,
        dropout: float = 0.1,
    ):
        super().__init__()
        self.attn = MultiHeadAttention(d_model, num_heads, dropout)
        self.grn_attn = GatedResidualNetwork(
            d_input=d_model,
            d_context=grn_context_dim,
            d_hidden=d_model,
            dropout=dropout,
        )
        self.grn_ffn = GatedResidualNetwork(
            d_input=d_model,
            d_context=grn_context_dim,
            d_hidden=d_ff,
            dropout=dropout,
        )

    def forward(
        self,
        x: torch.Tensor,
        asset_context: torch.Tensor,
        causal_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            x:             [B*A, num_patches+1, d_model]
            asset_context: [B*A, grn_context_dim]
            causal_mask:   [num_patches+1, num_patches+1]

        Returns:
            out: [B*A, num_patches+1, d_model]
            attn_weights
        """
        # Multi-Head Self-Attention + GRN 残差
        attn_out, attn_w = self.attn(x, x, x, causal_mask)
        x = self.grn_attn(x + attn_out, asset_context)  # ← FIX: attn_out 必须参与残差

        # FFN + GRN 残差
        ff_out = self.grn_ffn(x, asset_context)

        return ff_out, attn_w


# ============================================================
# 4. 空间轴：Cross-Asset Attention (iTransformer 维度反转)
# ============================================================

class CrossAssetAttention(nn.Module):
    """
    资产间交叉注意力：iTransformer 的核心创新

    维度反转思想：
        将 [Batch, Assets, Time, Features] 在特征维度做投影
        然后在 Asset 维度做 Cross-Attention

        即：每个资产可以看到其他所有资产的"特征表示"
        从而建模截面相关性（如板块轮动、避险效应等）
    """

    def __init__(
        self,
        d_model: int,
        num_heads: int,
        num_assets: int,
        grn_context_dim: int,
        dropout: float = 0.1,
    ):
        super().__init__()
        self.num_assets = num_assets  # 用于注册可变长度位置编码
        self.attn = MultiHeadAttention(d_model, num_heads, dropout)
        self.grn = GatedResidualNetwork(
            d_input=d_model,
            d_context=grn_context_dim,
            d_hidden=d_model,
            dropout=dropout,
        )

        # 可学习的资产位置编码（比正弦编码更灵活）
        self.asset_pos_emb = nn.Parameter(torch.zeros(1, num_assets, d_model))
        nn.init.trunc_normal_(self.asset_pos_emb, std=0.02)

    def forward(
        self,
        x: torch.Tensor,
        asset_context: torch.Tensor,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            x:             [Batch, Assets, d_model]   ← 经过时间编码后的资产表示
            asset_context: [Batch, Assets, grn_context_dim]  ← 资产嵌入（作 context）

        Returns:
            out: [Batch, Assets, d_model]
            attn_weights: [Batch, num_heads, Assets, Assets]
        """
        B, A, D = x.shape

        # 添加资产位置编码
        x = x + self.asset_pos_emb[:, :A, :]

        # Cross-Asset Self-Attention
        # Q = K = V = x → 每个资产attend其他所有资产
        out, attn_w = self.attn(x, x, x)

        # GRN 残差（用资产嵌入作为 context）
        out = self.grn(out, asset_context)

        return out, attn_w


# ============================================================
# 5. AlphaTransformer 主模型
# ============================================================

class AlphaTransformer(nn.Module):
    """
    AlphaTransformer: 多资产量化预测模型

    数据流:
        Input [B, A, T, F]
               ↓ Feature Embedding（每个资产独立投影）
        [B, A, T, d_model]
               ↓ Inverted Embedding（特征维度独立建模）
        [B, A, T, d_model]
               ↓ Temporal Encoder（PatchTST，时间轴）
        [B*A, T, d_model] → [B*A, d_model]
               ↓ 重组
        [B, A, d_model]
               ↓ Cross-Asset Attention（空间轴）
        [B, A, d_model]
               ↓ GRN Feature Filtering
        [B, A, d_model]
               ↓ Output Head
        [B, A, 1]  (未来3日对数收益率预测)

    关键设计：
        1. Asset Embedding: 资产ID嵌入，同时作为 GRN 的 context
        2. Patching: 在时间编码前，将时间维度分 patch
        3. Inverted Attention: 在特征维度做交叉，而非简单 flatten
    """

    def __init__(self, config):
        super().__init__()
        self.cfg = config

        # ---- 资产嵌入（用于 GRN Context + 位置编码） ----
        self.asset_emb = nn.Embedding(
            num_embeddings=config.num_assets,
            embedding_dim=config.asset_emb_dim,
        )
        # Xavier 初始化（适合嵌入层）
        nn.init.trunc_normal_(self.asset_emb.weight, std=0.02)

        # ---- 特征嵌入层：Inverted Embedding ----
        # 将 [Assets, Time, Features] 中的 Features 维度映射到 d_model
        # 这是 iTransformer 的关键：每个特征被视为独立 Token
        self.feature_proj = nn.Linear(
            config.feature_dim, config.d_model
        )
        # Per-Feature 可学习偏置（让不同特征的初始分布对齐）
        self.feature_bias = nn.Parameter(torch.zeros(config.d_model))

        # ---- 时间轴编码器（PatchTST） ----
        # 注意：这里是 Per-Asset 的，即每个资产独立做时间编码后再做资产间交互
        self.temporal_encoder = PatchTSTEncoder(
            history_len=config.history_len,
            patch_size=config.patch_size,
            d_model=config.d_model,
            num_heads=config.num_heads,
            num_layers=config.num_layers,
            d_ff=config.d_ff,
            grn_context_dim=config.asset_emb_dim,
            dropout=config.dropout,
            use_cls_token=False,
        )

        # ---- 资产间交叉注意力（空间轴） ----
        # num_assets 设为 0 表示动态读取（支持扩展）
        self.asset_attention = CrossAssetAttention(
            d_model=config.d_model,
            num_heads=config.num_heads,
            num_assets=config.num_assets,
            grn_context_dim=config.asset_emb_dim,
            dropout=config.dropout,
        )

        # ---- 资产间 FFN ----
        self.asset_ffn = GatedResidualNetwork(
            d_input=config.d_model,
            d_context=config.asset_emb_dim,
            d_hidden=config.d_ff,
            dropout=config.dropout,
        )

        # ---- 输出层 ----
        self.output_grn = GatedResidualNetwork(
            d_input=config.d_model,
            d_context=config.asset_emb_dim,
            d_hidden=config.d_model // 2,
            dropout=config.dropout,
            output_dim=1,
        )
        # 最终激活：回归目标，无激活（线性输出）
        # 如果做分类，改这里为 sigmoid / tanh

    def _build_causal_mask(self, seq_len: int, device: torch.device) -> torch.Tensor:
        """生成下三角因果遮罩（未来信息不可见）"""
        mask = torch.tril(torch.ones(seq_len, seq_len, device=device), diagonal=0)
        return mask == 0  # True = 被遮蔽

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: [Batch, Assets, History_Len, Features]
               典型值: [32, 16, 60, 8]

        Returns:
            predictions: [Batch, Assets, 1]  每个资产的预测目标值
        """
        B, A, T, F = x.shape

        # ---- Step 1: 特征维度 Inverted Embedding ----
        # [B, A, T, F] → [B, A, T, d_model]
        x = self.feature_proj(x)
        x = x + self.feature_bias
        x = F.gelu(x)

        # ---- Step 2: 获取资产嵌入（作 Context） ----
        asset_ids = torch.arange(A, device=x.device)
        asset_context = self.asset_emb(asset_ids)                 # [A, asset_emb_dim]
        asset_context = asset_context.unsqueeze(0).expand(B, -1, -1)  # [B, A, asset_emb_dim]
        # 用于时间轴 GRN（需展平为 B*A）
        asset_context_flat = asset_context.view(B * A, -1)         # [B*A, asset_emb_dim]

        # ---- Step 3: 时间轴编码（PatchTST，per-asset） ----
        # 展平资产维度：每个资产独立做时间编码
        x_temporal = x.view(B * A, T, -1)                           # [B*A, T, d_model]

        # 因果遮罩（Patch 级别）
        num_patches = T // self.cfg.patch_size
        causal_mask = self._build_causal_mask(num_patches, x.device)

        temporal_out, _ = self.temporal_encoder(
            x_temporal, asset_context_flat, causal_mask
        )  # [B*A, d_model]

        # 重组回 [Batch, Assets, d_model]
        asset_repr = temporal_out.view(B, A, -1)                     # [B, A, d_model]

        # ---- Step 4: 空间轴 Cross-Asset Attention ----
        asset_out, asset_attn = self.asset_attention(
            asset_repr, asset_context
        )  # [B, A, d_model]

        # ---- Step 5: 资产间 FFN ----
        asset_out = self.asset_ffn(asset_out, asset_context)         # [B, A, d_model]

        # ---- Step 6: 输出层 ----
        # 使用资产嵌入作为 context 的 GRN 输出
        predictions = self.output_grn(asset_out, asset_context)      # [B, A, 1]

        return predictions.squeeze(-1)                               # [B, A]


class AlphaTransformerV2(nn.Module):
    """
    AlphaTransformer V2: 支持动态资产数的版本

    与 V1 的区别：
        1. 不硬编码 num_assets，通过 x.shape[1] 动态获取
        2. 资产位置编码在 forward 中动态生成，支持任意资产数
        3. 适合数据集中资产数量不固定的情况（扩展到 50-100 只）

    注意：训练时需要确保 batch 内所有样本的资产数一致
    """

    def __init__(self, config):
        super().__init__()
        self.cfg = config

        # 资产嵌入（num_embeddings 设为足够大的上限）
        max_assets = getattr(config, "max_assets", 256)
        self.asset_emb_table = nn.Embedding(
            num_embeddings=max_assets,
            embedding_dim=config.asset_emb_dim,
        )
        nn.init.trunc_normal_(self.asset_emb_table.weight, std=0.02)

        # 特征嵌入
        self.feature_proj = nn.Linear(config.feature_dim, config.d_model)
        self.feature_bias = nn.Parameter(torch.zeros(config.d_model))

        # 时间编码器
        self.temporal_encoder = PatchTSTEncoder(
            history_len=config.history_len,
            patch_size=config.patch_size,
            d_model=config.d_model,
            num_heads=config.num_heads,
            num_layers=config.num_layers,
            d_ff=config.d_ff,
            grn_context_dim=config.asset_emb_dim,
            dropout=config.dropout,
            use_cls_token=False,
        )

        # 空间轴注意力（不在 __init__ 注册 num_assets）
        self.asset_attention = DynamicCrossAssetAttention(
            d_model=config.d_model,
            num_heads=config.num_heads,
            grn_context_dim=config.asset_emb_dim,
            dropout=config.dropout,
        )
        self.asset_ffn = GatedResidualNetwork(
            d_input=config.d_model,
            d_context=config.asset_emb_dim,
            d_hidden=config.d_ff,
            dropout=config.dropout,
        )
        self.output_grn = GatedResidualNetwork(
            d_input=config.d_model,
            d_context=config.asset_emb_dim,
            d_hidden=config.d_model // 2,
            dropout=config.dropout,
            output_dim=1,
        )

    def _build_causal_mask(self, seq_len: int, device: torch.device) -> torch.Tensor:
        mask = torch.tril(torch.ones(seq_len, seq_len, device=device))
        return mask == 0

    def forward(self, x: torch.Tensor, asset_ids: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        Args:
            x:         [Batch, Assets, History_Len, Features]
            asset_ids: [Batch, Assets]  资产索引（支持动态映射）
        """
        B, A, T, F = x.shape

        # 动态资产 ID（若未提供则用 0~A-1）
        if asset_ids is None:
            asset_ids = torch.arange(A, device=x.device).unsqueeze(0).expand(B, -1)

        # ---- 特征 Inverted Embedding ----
        x = self.feature_proj(x)
        x = x + self.feature_bias
        x = F.gelu(x)

        # ---- 资产嵌入（动态查询） ----
        asset_context = self.asset_emb_table(asset_ids)              # [B, A, asset_emb_dim]
        asset_context_flat = asset_context.view(B * A, -1)           # [B*A, asset_emb_dim]

        # ---- 时间轴编码 ----
        x_temporal = x.view(B * A, T, -1)
        num_patches = T // self.cfg.patch_size
        causal_mask = self._build_causal_mask(num_patches, x.device)
        temporal_out, _ = self.temporal_encoder(x_temporal, asset_context_flat, causal_mask)
        asset_repr = temporal_out.view(B, A, -1)

        # ---- 空间轴 ----
        asset_out, _ = self.asset_attention(asset_repr, asset_context)
        asset_out = self.asset_ffn(asset_out, asset_context)
        predictions = self.output_grn(asset_out, asset_context)

        return predictions.squeeze(-1)


class DynamicCrossAssetAttention(nn.Module):
    """动态资产数的 Cross-Asset Attention"""

    def __init__(self, d_model: int, num_heads: int, grn_context_dim: int, dropout: float):
        super().__init__()
        self.attn = MultiHeadAttention(d_model, num_heads, dropout)
        self.grn = GatedResidualNetwork(
            d_input=d_model,
            d_context=grn_context_dim,
            d_hidden=d_model,
            dropout=dropout,
        )
        # 用正弦编码，支持任意长度
        self.max_assets = 256
        self.register_buffer(
            "pos_emb_cache",
            self._generate_pos_emb(self.max_assets, d_model),
            persistent=False,
        )

    def _generate_pos_emb(self, max_len: int, d_model: int) -> torch.Tensor:
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len).unsqueeze(1).float()
        div_term = torch.exp(
            torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model)
        )
        pe[:, 0::2] = torch.sin(position * div_term)
        if d_model % 2 == 0:
            pe[:, 1::2] = torch.cos(position * div_term)
        else:
            pe[:, 1::2] = torch.cos(position * div_term[:-1])
        return pe.unsqueeze(0)  # [1, max_len, d_model]

    def forward(
        self,
        x: torch.Tensor,
        asset_context: torch.Tensor,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        B, A, D = x.shape
        # 动态截取位置编码
        pos_emb = self.pos_emb_cache[:, :A, :].to(x.device)
        x = x + pos_emb

        out, attn_w = self.attn(x, x, x)
        out = self.grn(out, asset_context)
        return out, attn_w
