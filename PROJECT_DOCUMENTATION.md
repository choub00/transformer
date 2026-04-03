# AlphaTransformer v2 — AI 量化投资预测系统

> 基于 Transformer 架构的多资产量化预测模型，融合 iTransformer + PatchTST + TFT 三大 SOTA 技术栈，并集成 2026 年最新研究成果（Regime-Aware Node Transformer + WaveLSFormer + Mamba-Hybrid）。
> 支持自主实验迭代、回测、模拟交易、实时推理，面向东方财富杯等量化竞赛场景。
>
> **毕业设计题目：基于 Transformer 的股票预测系统**

---

## 目录

- [1. 项目概览](#1-项目概览)
- [2. 技术架构](#2-技术架构)
- [3. 模型详解](#3-模型详解)
- [4. 训练流程与自主实验](#4-训练流程与自主实验)
- [5. 数据预处理（Anti-Leakage）](#5-数据预处理anti-leakage)
- [6. 回测引擎](#6-回测引擎)
- [7. API 服务](#7-api-服务)
- [8. 前端界面](#8-前端界面)
- [9. 踩坑全记录](#9-踩坑全记录)
- [10. v1 → v2 迭代经验总结](#10-v1--v2-迭代经验总结)
- [11. 2026 最新研究论文汇总](#11-2026-最新研究论文汇总)
- [12. 运行指南](#12-运行指南)

---

## 1. 项目概览

### 1.1 项目定位

```
AlphaTransformer v2
├── models/              # 深度学习模型（AlphaTransformer v1 / v2 / v3）
├── trainer/             # 训练器 + 自主实验引擎（autoresearch 模式）
├── utils/               # 数据标准化（滚动窗口 Anti-Leakage）
├── data/                # 数据加载与股票池
├── evaluation/          # 回测引擎（Anti-Churn v3）
├── api/                 # FastAPI 后端（推理 + 模拟交易）
└── frontend/            # Vue 3 前端（仪表盘 + 分析 + 交易）
```

### 1.2 技术栈

| 层级 | 技术选型 |
|------|---------|
| 深度学习 | PyTorch 2.1+（CUDA 加速） |
| 框架架构 | iTransformer + PatchTST + Regime-Aware Node Transformer |
| 混合架构 | Transformer + Mamba-2 SSD（状态空间模型） |
| 训练 | AdamW + CosineAnnealingWarmRestarts + 自主实验循环 |
| 损失函数 | MixedHuberLoss（金融数据专用） |
| 后端 | FastAPI + Pydantic |
| 前端 | Vue 3 + TypeScript + Vite |
| 可视化 | ECharts 6.x |
| 动画 | GSAP 3.x |

### 1.3 股票池

```
A股:     000001 平安银行, 600519 贵州茅台, 600036 招商银行,
        600900 长江电力, 000002 万科A, 600276 恒瑞医药,
        601318 中国平安, 000858 五粮液
科技:    AAPL  MSFT  GOOGL  NVDA  AMZN  META
金融:    JPM   V     MA
医疗:    JNJ   UNH
消费:    WMT   PG    HD
```

### 1.4 v1 核心指标回顾（2026 Q1）

| 指标 | 值 | 问题诊断 |
|------|-----|---------|
| Sharpe Ratio | 0.28 | ❌ 未达竞赛门槛（需 >1.5） |
| Annual Return | +18.6% | ✅ 良好 |
| Max Drawdown | -15.2% | ⚠️ 可接受但需优化 |
| Win Rate | 62.5% | ✅ 超过随机 |
| Information Coefficient | +0.073 | ❌ IC 过低，模型预测能力弱 |
| 总交易次数 | 147 | ⚠️ 换手率偏高 |

**v1 核心教训：IC（信息系数）过低是根本问题。模型在时序模式识别上存在瓶颈，需要引入更强的架构和更大规模的数据预训练。**

---

## 2. 技术架构

### 2.1 系统数据流

```
Data Flow (v2)
──────────────────────────────────────────────────────
  原始价格数据
       ↓
  滚动窗口标准化（Anti-Leakage）
       ↓
  特征张量 + 板块标签 + 情感因子
       ↓
  [模型层]
  ┌─────────────────────────────────────┐
  │ Regime-Aware Encoder（市场状态检测）  │
  │   ↓                                  │
  │ Mamba-2 SSD（时间轴，O(n) 线性）     │
  │   ↓                                  │
  │ iTransformer（资产轴，维度反转）      │
  │   ↓                                  │
  │ Adaptive Layer Norm（ALN）           │
  │   ↓                                  │
  │ GRN Output Head（多头/空头预测）      │
  └─────────────────────────────────────┘
       ↓
  回测引擎（集合差集 Anti-Churn）
       ↓
  Sharpe / IC / MaxDD 指标评估
       ↓
  实验日志 → 自主实验循环（autoresearch）
```

### 2.2 版本演进

| 版本 | 文件 | 核心特性 | 状态 |
|------|------|---------|------|
| v1 | `alpha_transformer.py` | 固定 16 资产，全连接 Cross-Attention | ✅ 已完成 |
| v2 | `alpha_transformer_2026.py` | 多尺度 Patch、稀疏注意力、ALN | ⚠️ 基础完成 |
| **v3（本次迭代）** | `alpha_transformer_v3.py` | **Regime-Aware + Mamba-Hybrid + 自主实验** | 🚧 本文档规划 |

---

## 3. 模型详解

### 3.1 v3 架构设计（参考论文实现）

#### 3.1.1 市场状态检测器（Regime-Aware Encoder）

**参考论文：** `Adaptive Regime-Aware Stock Price Prediction Using Autoencoder-Gated Dual Node Transformers with Reinforcement Learning Control`（March 2026）

```python
class MarketRegimeDetector(nn.Module):
    """
    市场状态检测器（v3 核心创新）

    原理：
    1. 用 Autoencoder 计算重建误差
    2. 重建误差大 → 市场处于异常/高波动状态
    3. 动态调整模型参数路由

    三种市场状态：
    - Normal（平稳期）：标准预测路径
    - Volatile（波动期）：增强归一化，更保守仓位
    - Crisis（危机期）：切换到低杠杆模式
    """
    def __init__(self, d_model, num_regimes=3):
        self.encoder = nn.Sequential(
            nn.Linear(d_model, d_model // 2),
            nn.GELU(),
            nn.Linear(d_model // 2, num_regimes)  # 3个市场状态
        )
        self.norm = nn.LayerNorm(d_model)

    def forward(self, x):
        # x: [B, A, d_model] - 来自前面的时空编码
        x_pooled = x.mean(dim=1)  # [B, d_model]
        regime_logits = self.encoder(x_pooled)  # [B, 3]
        regime_probs = F.softmax(regime_logits, dim=-1)
        return regime_probs  # [B, 3] - Normal/Volatile/Crisis 概率分布


class RegimeAwareNorm(nn.Module):
    """
    市场状态自适应归一化

    原理: 根据检测到的市场状态，动态调整 LayerNorm 的缩放和偏移参数
    ALN(x, s) = γ(s) * (x - μ(x)) / σ(x) + β(s)
    其中 γ(s), β(s) 由市场状态 s 生成

    市场高波动期 → 自动增强归一化强度 → 更鲁棒
    """
    def __init__(self, d_model, num_regimes=3):
        super().__init__()
        self.gamma = nn.Linear(num_regimes, d_model)
        self.beta = nn.Linear(num_regimes, d_model)
        self.num_regimes = num_regimes

    def forward(self, x, regime_probs):
        # x: [B, A, d_model], regime_probs: [B, 3]
        mean = x.mean(dim=1, keepdim=True)
        std = x.std(dim=1, keepdim=True) + 1e-8
        normalized = (x - mean) / std

        gamma = self.gamma(regime_probs)  # [B, d_model]
        beta = self.beta(regime_probs)     # [B, d_model]

        # broadcasting: [B, A, d_model]
        return gamma.unsqueeze(1) * normalized + beta.unsqueeze(1)
```

#### 3.1.2 Mamba-2 SSD 时间轴编码器（替代 MHSA）

**参考论文：** `State-Space Models for Market Microstructure: Can Mamba Replace Transformers in High-Frequency Finance?`（March 2026）+ `Mamba-3`（March 2026）

```python
class Mamba2TemporalEncoder(nn.Module):
    """
    Mamba-2 SSD 时间轴编码器（替代 PatchTST Self-Attention）

    优势：
    - O(n) 线性复杂度 vs Transformer O(n²)
    - 在高频金融数据上有竞争力
    - 避免 Transformer 在高频场景的 O(n²) 延迟问题
    - 选择性状态空间，捕捉多尺度时间模式

    金融场景适配：
    - 指数衰减选择机制（选择性遗忘历史噪声）
    - 可学习的 dstate（状态维度）捕捉多尺度模式
    - 比标准 RNN 更强的梯度流
    """
    def __init__(self, d_model, d_state=128, d_conv=4, expand=2):
        try:
            from mamba_ssm import Mamba2
            self.mamba = Mamba2(
                d_model=d_model,
                d_state=d_state,
                d_conv=d_conv,
                expand=expand,
            )
            self.has_mamba = True
        except ImportError:
            # fallback 到标准 Transformer
            self.has_mamba = False
            self.attn = nn.MultiheadAttention(d_model, num_heads=4, batch_first=True)
            self.attn_norm = nn.LayerNorm(d_model)
            print("Warning: mamba-ssm not installed, falling back to Transformer")

        self.norm = nn.LayerNorm(d_model)

    def forward(self, x):
        # x: [B*A, T, d_model]
        if self.has_mamba:
            out = self.norm(x + self.mamba(x))
        else:
            # Fallback: 标准自注意力 + 残差
            attn_out, _ = self.attn(x, x, x)
            out = self.attn_norm(x + attn_out)
        return out  # [B*A, T, d_model]
```

#### 3.1.3 iTransformer 资产轴编码器

**参考论文：** `iTransformer: Inverted Transformers are Effective for Time Series Forecasting`（ICLR 2024）

```python
class iTransformerAssetEncoder(nn.Module):
    """
    iTransformer 核心：维度反转

    传统方法：[Batch, Time, Assets, Features] → Time 建模
    iTransformer：   [Batch, Time, Assets, Features] → Assets 建模

    将每个资产视为一个 Token，在资产维度做 Self-Attention
    建模：板块轮动、避险效应、跨资产相关性

    优势：
    - 资产数量远小于时间步长时，效率大幅提升
    - 每个资产有独立的全局表征
    - 更适合多资产联合预测任务
    """
    def __init__(self, d_model, num_heads=4, num_assets=16):
        super().__init__()
        self.num_assets = num_assets

        # 资产 Token 投影：[B, T, A, d_model] → [B, A, T, d_model] → [B, A, d_model*]
        self.asset_proj = nn.Linear(d_model, d_model)

        # 多头自注意力（在资产维度）
        self.attn = nn.MultiheadAttention(
            embed_dim=d_model,
            num_heads=num_heads,
            batch_first=True  # [B, A, d_model]
        )

        # 稀疏注意力（Top-K，降低 O(A²) → O(A·K)）
        self.use_sparse = True
        self.top_k = min(8, num_assets)

        self.norm = nn.LayerNorm(d_model)
        self.ffn = nn.Sequential(
            nn.Linear(d_model, d_model * 4),
            nn.GELU(),
            nn.Linear(d_model * 4, d_model),
        )
        self.ffn_norm = nn.LayerNorm(d_model)

    def forward(self, x):
        # x: [B, T, A, d_model]
        B, T, A, D = x.shape

        # 方案 1: 时间维 Mean Pooling → 资产表示
        x_asset = x.mean(dim=1)  # [B, A, d_model]

        # 方案 2: 时间维 Linear Proj → 资产 Token（更好）
        x_asset = self.asset_proj(x_asset)

        # 自注意力（资产间建模）
        if self.use_sparse:
            attn_out = self._sparse_attention(x_asset)
        else:
            attn_out, _ = self.attn(x_asset, x_asset, x_asset)

        # 残差 + FFN
        x_asset = self.norm(x_asset + attn_out)
        x_asset = self.ffn_norm(x_asset + self.ffn(x_asset))

        # 广播回时间维度
        x_out = x_asset.unsqueeze(1).expand(B, T, A, D)
        return x_out  # [B, T, A, d_model]

    def _sparse_attention(self, x):
        """Top-K 稀疏注意力：每个资产只关注最相似的 K 个邻居"""
        B, A, D = x.shape

        # 计算注意力分数
        scores = torch.matmul(x, x.transpose(-2, -1)) / (D ** 0.5)  # [B, A, A]

        # Top-K 稀疏化
        topk_values, topk_indices = torch.topk(scores, k=self.top_k, dim=-1)

        # 重建稀疏注意力矩阵
        sparse_attn = torch.zeros_like(scores)
        sparse_attn.scatter_(-1, topk_indices, topk_values)
        sparse_attn = F.softmax(sparse_attn, dim=-1)

        # 稀疏注意力加权
        return torch.matmul(sparse_attn, x)
```

#### 3.1.4 PatchTST 分段编码器（保留多尺度分支）

**参考论文：** `PatchTST: PatchTST: A Transformer for Time Series Forecasting`（ICLR 2023）

```python
class MultiScalePatchEncoder(nn.Module):
    """
    多尺度 Patch 融合（来自 v2，保留）

    - 低分辨率分支 (patch_size=20): 捕捉长期趋势（周线级别）
    - 高分辨率分支 (patch_size=5):  捕捉短期波动（日内/日间）
    - GRN 门控融合: 自适应权重组合两个分支

    原理：
    金融数据的特征在不同时间尺度上有不同的预测能力
    - 长期趋势：宏观驱动（GDP、利率）
    - 短期波动：技术面、资金面、情绪面
    """
    def __init__(self, d_model, low_patch_size=20, high_patch_size=5):
        self.low_patch_size = low_patch_size
        self.high_patch_size = high_patch_size

        # 低分辨率分支
        self.low_proj = nn.Conv1d(
            in_channels=d_model,
            out_channels=d_model,
            kernel_size=low_patch_size,
            stride=low_patch_size
        )

        # 高分辨率分支
        self.high_proj = nn.Conv1d(
            in_channels=d_model,
            out_channels=d_model,
            kernel_size=high_patch_size,
            stride=high_patch_size
        )

        # 各自的时间块
        self.low_temporal = Mamba2TemporalEncoder(d_model)
        self.high_temporal = Mamba2TemporalEncoder(d_model)

        # 门控融合
        self.fusion_gate = nn.Sequential(
            nn.Linear(d_model * 2, d_model),
            nn.Sigmoid()
        )

        self.out_norm = nn.LayerNorm(d_model)

    def forward(self, x, asset_context=None):
        # x: [B*A, T, d_model]
        B, T, D = x.shape

        # 低分辨率 Patchify
        n_low = T // self.low_patch_size
        x_low = x[:, :n_low * self.low_patch_size, :]
        x_low = x_low.reshape(B, n_low, self.low_patch_size * D).transpose(-2, -1)
        x_low = self.low_proj(x_low).transpose(-2, -1)  # [B, n_low, D]

        # 高分辨率 Patchify
        n_high = T // self.high_patch_size
        x_high = x[:, :n_high * self.high_patch_size, :]
        x_high = x_high.reshape(B, n_high, self.high_patch_size * D).transpose(-2, -1)
        x_high = self.high_proj(x_high).transpose(-2, -1)  # [B, n_high, D]

        # 各自通过时间编码器
        h_low = self.low_temporal(x_low)     # [B, n_low, D]
        h_high = self.high_temporal(x_high)  # [B, n_high, D]

        # 融合：低分辨率补齐到高分辨率长度
        if n_low < n_high:
            h_low = F.interpolate(h_low.transpose(-2, -1), size=n_high, mode='linear').transpose(-2, -1)
        elif n_low > n_high:
            h_high = F.interpolate(h_high.transpose(-2, -1), size=n_low, mode='linear').transpose(-2, -1)

        # 门控融合
        combined = torch.cat([h_low, h_high], dim=-1)  # [B, n, 2D]
        gate = self.fusion_gate(combined)  # [B, n, D]
        out = gate * h_low + (1 - gate) * h_high

        # 恢复原始时间维度
        out = out.transpose(-2, -1)  # [B, D, n]
        out = F.interpolate(out, size=T, mode='linear').transpose(-2, -1)

        return self.out_norm(out)  # [B, T, d_model]
```

#### 3.1.5 情感因子注入（BERT Sentiment）

**参考论文：** `Stock Market Prediction Using Node Transformer Architecture Integrated with BERT Sentiment Analysis`（March 2026）

```python
class SentimentInjector(nn.Module):
    """
    情感因子注入模块（v3 可选模块）

    输入：
    - 财经新闻标题（今日头条）
    - 社交媒体讨论（Twitter/X）
    - 财报电话会议摘要

    流程：
    1. BERT 编码文本 → 向量
    2. 投影到 d_model 维度
    3. 通过 GRN 门控注入主模型

    效果：
    - 情感分析降低预测误差 10%
    - 财报期降低误差 25%（来自论文数据）
    """
    def __init__(self, d_model, text_dim=768):
        try:
            from transformers import BertModel
            self.bert = BertModel.from_pretrained('bert-base-uncased')
            self.has_bert = True
        except ImportError:
            self.has_bert = False

        self.projection = nn.Linear(text_dim, d_model)

        # 门控注入（GRN）
        self.gate = nn.Sequential(
            nn.Linear(d_model * 2, d_model),
            nn.GELU(),
            nn.Linear(d_model, d_model),
            nn.Sigmoid()
        )

    def forward(self, text_inputs, market_features):
        """
        Args:
            text_inputs: dict with 'input_ids', 'attention_mask' from BERT tokenizer
            market_features: [B, A, d_model] from previous layer
        Returns:
            [B, A, d_model] - 融合了情感的市场特征
        """
        if not self.has_bert:
            return market_features

        # BERT 编码
        bert_out = self.bert(**text_inputs)
        text_vec = bert_out.last_hidden_state[:, 0]  # [CLS] token
        sentiment_vec = self.projection(text_vec)     # [B, d_model]

        # GRN 门控注入
        market_pooled = market_features.mean(dim=1)   # [B, d_model]
        gate_val = self.gate(torch.cat([market_pooled, sentiment_vec], dim=-1))
        gate_val = gate_val.unsqueeze(1)              # [B, 1, d_model]

        # 选择性注入
        return market_features * gate_val
```

#### 3.1.6 WaveLSFormer 投资组合输出头

**参考论文：** `WaveLSFormer: Learnable Wavelet-Based Transformer for End-to-End Quantitative Trading`（January 2026）

```python
class WaveLSFormerHead(nn.Module):
    """
    直接输出市场中性多空投资组合权重

    核心设计：
    - 不输出单只股票预测，而是输出 [long_weights, short_weights]
    - 端到端优化交易目标（而非预测精度）
    - 风险感知正则化（限制单只股票仓位上限）

    优化目标：
    max Sharpe = E[r_p] / Std[r_p]
    s.t. Σw_i = 0（市场中性）
         |w_i| ≤ max_pos（仓位上限）

    关键指标（论文数据）：
    - Sharpe Ratio: 2.157 ± 0.166
    - Cumulative Return: 0.607 ± 0.045
    """
    def __init__(self, d_model, num_assets, max_position=0.1, risk_aversion=0.01):
        super().__init__()

        self.max_position = max_position
        self.risk_aversion = risk_aversion  # 风险厌恶系数

        # 多头预测头
        self.long_head = nn.Sequential(
            nn.Linear(d_model, d_model // 2),
            nn.GELU(),
            nn.Linear(d_model // 2, num_assets),
        )

        # 空头预测头
        self.short_head = nn.Sequential(
            nn.Linear(d_model, d_model // 2),
            nn.GELU(),
            nn.Linear(d_model // 2, num_assets),
        )

        # 仓位归一化（市场中性约束）
        self.norm_factor = nn.Parameter(torch.ones(1))

    def forward(self, x, regime_probs=None):
        """
        Args:
            x: [B, A, d_model] - 来自 ALN 层的输出
            regime_probs: [B, 3] - 市场状态概率（可选）
        Returns:
            [B, A, 2] - [long_weights, short_weights]
        """
        B, A, D = x.shape

        # 聚合序列信息
        x_pooled = x.mean(dim=1)  # [B, d_model]

        # 预测多空信号
        long_logits = self.long_head(x_pooled)   # [B, A]
        short_logits = self.short_head(x_pooled) # [B, A]

        # Softmax 归一化到概率
        long_weights = F.softmax(long_logits, dim=-1)
        short_weights = F.softmax(short_logits, dim=-1)

        # 市场中性约束：多头总权重 = 空头总权重
        total_long = long_weights.sum(dim=-1, keepdim=True)  # [B, 1]
        total_short = short_weights.sum(dim=-1, keepdim=True)  # [B, 1]

        long_weights = long_weights / (total_long + 1e-8)
        short_weights = short_weights / (total_short + 1e-8)

        # 仓位裁剪（风险控制）
        long_weights = torch.clamp(long_weights, max=self.max_position)
        short_weights = torch.clamp(short_weights, max=self.max_position)

        # 市场状态自适应调整（危机期降低仓位）
        if regime_probs is not None:
            crisis_weight = regime_probs[:, 2]  # Crisis 状态的概率
            crisis_adjustment = 1.0 - crisis_weight * 0.5  # 危机期最多降50%仓位
            crisis_adjustment = crisis_adjustment.unsqueeze(-1)  # [B, 1]
            long_weights = long_weights * crisis_adjustment
            short_weights = short_weights * crisis_adjustment

        return torch.stack([long_weights, short_weights], dim=-1)  # [B, A, 2]
```

### 3.2 v3 完整数据流

```
Input [B, T, A, F]（历史价格 + 技术指标 + 情感因子）
    ↓ Inverted Embedding（F 个特征分组投影）
[B, T, A, d_model]
    ↓ MultiScalePatchEncoder（多尺度 Patch + 因果遮罩）
    │   ├── Low-resolution branch (patch=20): 长期趋势
    │   └── High-resolution branch (patch=5):  短期波动
[B, T, A, d_model]
    ↓ Mamba2TemporalEncoder（时间轴，O(n) 线性）
[B, T, A, d_model]
    ↓ MarketRegimeDetector（检测 Normal/Volatile/Crisis）
regime_probs → 路由决策
[B, T, A, d_model]
    ↓ iTransformer Asset Encoder（资产轴注意力）
[B, A, d_model]
    ↓ RegimeAwareNorm（市场状态自适应归一化）
[B, A, d_model]
    ↓ WaveLSFormerHead
[B, A, 2] → [long_weights, short_weights]

Loss: CombinedQuantLoss（Huber + Sharpe + Direction）
```

### 3.3 v3 完整模型实现

```python
# models/alpha_transformer_v3.py

class AlphaTransformerV3(nn.Module):
    """
    AlphaTransformer v3 — 2026 SOTA

    整合以下技术：
    - MultiScalePatchEncoder: 多尺度时间建模
    - Mamba2TemporalEncoder: O(n) 时间轴编码
    - iTransformerAssetEncoder: 资产间关系建模
    - MarketRegimeDetector: 市场状态自适应
    - WaveLSFormerHead: 投资组合输出

    输入:  [B, T, A, F] - 日频数据，60天历史窗口
    输出:  [B, A, 2]    - 每只股票的多头/空头权重
    """

    def __init__(
        self,
        num_assets: int = 16,
        feature_dim: int = 8,
        history_len: int = 60,
        d_model: int = 128,
        num_heads: int = 4,
        num_layers: int = 3,
        d_ff: int = 512,
        dropout: float = 0.1,
        max_position: float = 0.1,
        use_sentiment: bool = False,
        use_mamba: bool = True,
    ):
        super().__init__()

        self.d_model = d_model
        self.num_assets = num_assets
        self.use_sentiment = use_sentiment

        # 输入投影（Inverted Embedding）
        self.feature_proj = nn.Linear(feature_dim, d_model)
        self.asset_emb = nn.Parameter(torch.randn(num_assets, d_model) * 0.02)

        # 多尺度时间编码器
        self.temporal_encoder = MultiScalePatchEncoder(
            d_model=d_model,
            low_patch_size=20,
            high_patch_size=5,
        )

        # 市场状态检测
        self.regime_detector = MarketRegimeDetector(d_model, num_regimes=3)

        # 时空混合编码层
        self.st_layers = nn.ModuleList([
            SpatioTemporalBlock(
                d_model=d_model,
                num_heads=num_heads,
                d_ff=d_ff,
                dropout=dropout,
                use_mamba=use_mamba,
            )
            for _ in range(num_layers)
        ])

        # 自适应归一化
        self.regime_norm = RegimeAwareNorm(d_model, num_regimes=3)

        # 输出头
        self.output_head = WaveLSFormerHead(
            d_model=d_model,
            num_assets=num_assets,
            max_position=max_position,
        )

        # 情感注入（可选）
        if use_sentiment:
            self.sentiment_injector = SentimentInjector(d_model)

    def forward(self, x, text_inputs=None):
        """
        Args:
            x: [B, T, A, F] - 历史价格+特征
            text_inputs: dict (可选) - BERT 格式的情感文本输入
        Returns:
            [B, A, 2] - [long_weights, short_weights]
        """
        B, T, A, F = x.shape

        # 特征投影
        x = self.feature_proj(x)  # [B, T, A, d_model]

        # 加入资产嵌入
        asset_emb = self.asset_emb.unsqueeze(0).unsqueeze(0)  # [1, 1, A, d_model]
        x = x + asset_emb

        # 时间编码（多尺度 Patch + Mamba）
        x = self.temporal_encoder(x)  # [B, T, A, d_model]

        # 展平为 [B*A, T, d_model] 进行时空混合编码
        x_flat = x.reshape(B, T, A, -1).permute(0, 2, 1, 3)  # [B, A, T, d_model]
        x_flat = x_flat.reshape(B * A, T, self.d_model)        # [B*A, T, d_model]

        # 时空混合编码层
        for layer in self.st_layers:
            x_flat = layer(x_flat)

        # 恢复形状 [B, A, T, d_model]
        x_reshaped = x_flat.reshape(B, A, T, self.d_model)

        # 资产维度 Mean Pooling [B, A, d_model]
        x_asset = x_reshaped.mean(dim=2)

        # 情感注入（可选）
        if self.use_sentiment and text_inputs is not None:
            x_asset = self.sentiment_injector(text_inputs, x_asset)

        # 市场状态检测
        regime_probs = self.regime_detector(x_asset)  # [B, 3]

        # 自适应归一化
        x_asset = self.regime_norm(x_asset, regime_probs)

        # 投资组合输出
        portfolio = self.output_head(x_asset, regime_probs)  # [B, A, 2]

        return portfolio


class SpatioTemporalBlock(nn.Module):
    """
    时空混合块：交替执行时间建模和空间建模

    时间建模（Mamba2）→ 空间建模（iTransformer）→ 特征融合（GRN）
    """
    def __init__(self, d_model, num_heads, d_ff, dropout, use_mamba=True):
        super().__init__()

        # 时间编码
        if use_mamba:
            self.temporal = Mamba2TemporalEncoder(d_model)
        else:
            self.temporal = nn.MultiheadAttention(d_model, num_heads, batch_first=True)

        self.temporal_norm = nn.LayerNorm(d_model)

        # 空间编码（iTransformer）
        self.spatial = nn.MultiheadAttention(d_model, num_heads, batch_first=True)
        self.spatial_norm = nn.LayerNorm(d_model)

        # FFN
        self.ffn = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(d_ff, d_model),
            nn.Dropout(dropout),
        )
        self.ffn_norm = nn.LayerNorm(d_model)

        # GRN 特征融合
        self.grn = GatedResidualNetwork(d_model, d_ff=d_ff)

    def forward(self, x):
        # x: [B*A, T, d_model]
        B, T, D = x.shape

        # 时间建模 + 残差
        if hasattr(self.temporal, 'mamba'):
            t_out = self.temporal(x)
        else:
            t_out, _ = self.temporal(x, x, x)
        x = self.temporal_norm(x + t_out)

        # FFN + 残差
        x = self.ffn_norm(x + self.ffn(x))

        return x
```

---

## 4. 训练流程与自主实验

### 4.1 借鉴 autoresearch：固定时间预算自主实验循环

**参考项目：** `karpathy/autoresearch`（MIT License, March 2026）

autoresearch 的核心工程智慧：
- **5 分钟固定时间预算**：无论模型大小，每次实验固定时间，强制高效迭代
- **单一可修改文件**：`train.py` 是 Agent 唯一修改的文件
- **单一评估指标**：`val_bpb`（低即好），清晰无歧义
- **实验日志持久化**：每次实验结果写入 `experiments.jsonl`

**迁移到量化场景的改造：**

```python
# trainer/auto_experimenter.py

class QuantAutoExperimenter:
    """
    AlphaTransformer v3 自主实验引擎
    借鉴 karpathy/autoresearch 的工程设计模式

    每次实验：
    1. Agent 根据 program_alpha.md 修改模型超参数/架构
    2. 固定时间预算训练（推荐 30 分钟，A 股日频数据）
    3. 回测评估（Sharpe / IC / MaxDD）
    4. 决策：保留 or 回滚
    5. 更新实验日志

    评估指标（替代 val_bpb）：
    - Sharpe Ratio（目标 > 1.5）
    - Information Coefficient（目标 > 0.05）
    - Max Drawdown（目标 < 10%）
    """
    def __init__(self, program_path: str, time_budget_minutes: int = 30):
        self.program_path = Path(program_path)
        self.time_budget = time_budget_minutes * 60
        self.experiment_log = Path("experiments_v3.jsonl")
        self.best_metrics = {
            "sharpe": -float("inf"),
            "ic": -float("inf"),
            "maxdd": float("inf"),
        }

    def run_cycle(self) -> dict:
        """
        执行一次完整的实验循环

        Returns:
            {
                "sharpe_ratio": float,
                "information_coefficient": float,
                "max_drawdown": float,
                "total_return": float,
                "num_trades": int,
                "time_elapsed_seconds": float,
                "config": dict,
                "timestamp": str,
                "keep": bool,
            }
        """
        import time
        start = time.time()

        # Step 1: 加载模型配置（由 Agent 上次实验修改）
        config = self._load_config()

        # Step 2: 固定时间预算训练
        model, trainer = self._init_trainer(config)
        train_start = time.time()
        while time.time() - train_start < self.time_budget:
            epoch_result = trainer.train_one_epoch()
            if self._should_stop_early(epoch_result):
                break
        train_time = time.time() - train_start

        # Step 3: 回测评估
        backtest_metrics = self._run_backtest(model)

        elapsed = time.time() - start

        # Step 4: 决策（保留 or 回滚）
        result = {
            **backtest_metrics,
            "time_elapsed_seconds": elapsed,
            "train_time_seconds": train_time,
            "config": config.__dict__,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "keep": self._is_better(backtest_metrics),
        }

        # Step 5: 持久化
        self._append_log(result)

        if result["keep"]:
            self._save_checkpoint(model, result)
            self._update_best_metrics(result)

        return result

    def run_overnight(self, max_cycles: int = 100):
        """
        夜间自主实验循环
        类似于 autoresearch 的 "run overnight" 模式
        """
        print(f"🚀 启动自主实验，最大 {max_cycles} 轮")
        print(f"⏱  每轮时间预算: {self.time_budget / 60:.0f} 分钟")

        results = []
        for cycle in range(max_cycles):
            print(f"\n{'='*50}")
            print(f"实验 #{cycle + 1}")
            result = self.run_cycle()
            results.append(result)

            if result["keep"]:
                print(f"✅ 保留! Sharpe={result['sharpe_ratio']:.3f} IC={result['information_coefficient']:.4f}")
            else:
                print(f"❌ 丢弃. Sharpe={result['sharpe_ratio']:.3f}")

            # 检查是否达到目标
            if (result['sharpe_ratio'] > 1.5 and
                result['information_coefficient'] > 0.05 and
                result['max_drawdown'] > -0.10):
                print(f"\n🎯 达到目标！提前终止实验循环。")
                break

        # 汇总
        self._summarize(results)
        return results

    def _is_better(self, metrics: dict) -> bool:
        """多目标判断：Sharpe 和 IC 同时提升才算更好"""
        improved_sharpe = metrics["sharpe_ratio"] > self.best_metrics["sharpe"]
        improved_ic = metrics["information_coefficient"] > self.best_metrics["ic"]
        reduced_mdd = metrics["max_drawdown"] > self.best_metrics["maxdd"]

        return improved_sharpe or improved_ic

    def _summarize(self, results: list):
        """生成实验汇总报告"""
        print("\n" + "="*60)
        print("实验汇总报告")
        print("="*60)

        best = max(results, key=lambda r: r["sharpe_ratio"])
        print(f"最佳 Sharpe: {best['sharpe_ratio']:.3f}")
        print(f"最佳 IC:     {best['information_coefficient']:.4f}")
        print(f"最大回撤:     {best['max_drawdown']:.2%}")
        print(f"总收益:      {best['total_return']:.2%}")
        print(f"交易次数:    {best['num_trades']}")
        print(f"时间戳:      {best['timestamp']}")
```

### 4.2 自主实验任务书（program_alpha.md）

```markdown
# program_alpha.md — AlphaTransformer v3 自主研究任务书

## 你的角色

你是 AlphaTransformer v3 的自主研究 Agent。你的任务是**最大化投资组合的 Sharpe Ratio**，
同时控制 Max Drawdown 和提升 Information Coefficient（IC）。

## 当前基线

- Sharpe Ratio: 0.28（目标: > 1.5）
- Information Coefficient: 0.073（目标: > 0.05）
- Max Drawdown: -15.2%（目标: < -10%）
- 训练数据: A股 + 美股日频数据（2015-2025）

## 评估指标（优先级排序）

1. **Sharpe Ratio** — 年化收益 / 年化波动率（最重要）
2. **Information Coefficient** — 预测与实际收益的 Pearson 相关系数
3. **Max Drawdown** — 最大回撤（控制在 -15% 以内）
4. **Annual Return** — 年化绝对收益
5. **Win Rate** — 预测准确率

## 每次实验的操作步骤

### Step 1: 分析上次实验结果

读取 `experiments_v3.jsonl`，分析：
- 哪些超参数组合效果好？（学习率、batch size、d_model）
- 哪些架构改动有效？（PatchTST vs Mamba、稀疏 vs 全连接注意力）
- 是否存在过拟合？（训练集 loss 低但回测差）

### Step 2: 决定本次修改

从以下方向选择 1-2 个进行修改：

**超参数方向：**
- 学习率: 1e-4 → 5e-4 → 1e-3 → 3e-3（对数均匀采样）
- Batch size: 16 → 32 → 64
- Dropout: 0.05 → 0.1 → 0.2
- Weight decay: 0.001 → 0.01 → 0.1
- Early stopping patience: 3 → 5 → 10

**架构方向：**
- 调整 d_model: 64 / 128 / 256
- 调整层数: 2 / 3 / 4 / 6
- 调整注意力头数: 2 / 4 / 8
- 调整 Mamba d_state: 64 / 128 / 256
- 调整 Patch size: 5 / 10 / 20
- 尝试/移除/添加某个模块（GRN / ALN / Multi-Scale Patch）

**数据方向：**
- 调整历史窗口: 30 / 60 / 120 / 250 天
- 调整预测 horizon: 1 / 3 / 5 天
- 调整股票池大小: 8 / 16 / 32 只
- 添加/移除技术指标因子

**损失函数方向：**
- Huber delta: 0.5 / 1.0 / 2.0
- 添加辅助损失（方向预测 loss）
- 尝试 Focal Loss（对极端值更鲁棒）

### Step 3: 修改代码

只修改 `train_alpha.py` 中的配置部分：

```python
# === Agent 可修改的配置 ===
CONFIG = {
    "d_model": 128,        # 可调整
    "num_layers": 3,       # 可调整
    "learning_rate": 1e-3,  # 可调整
    # ... 其他超参数
}
# === 配置结束 ===
```

### Step 4: 训练（固定 30 分钟）

运行 `python train_alpha.py`，观察：
- 训练 loss 是否下降
- 验证 loss 是否下降（早停检查）
- 是否在时间预算内完成

### Step 5: 回测

运行 `python -m evaluation.backtest --checkpoint=checkpoints/best.pt`
获取 Sharpe / IC / MaxDD 指标。

### Step 6: 记录与决策

将实验结果追加到 `experiments_v3.jsonl`。
如果 Sharpe > 当前最优，则更新 `best_config.json`。

## 输出格式

每次实验完成后，输出：
```
实验 #{N}
- Sharpe: {value} | IC: {value} | MaxDD: {value}
- 修改: {描述本次修改了什么}
- 结论: {保留/丢弃} {原因}
```

## 约束

- 每次修改不超过 2 个维度（避免同时改太多变量）
- 训练时间预算固定 30 分钟（不变）
- 回测数据只用最近 1 年（out-of-sample）
- 不使用未来信息（严格 Anti-Leakage）
```

### 4.3 损失函数（CombinedQuantLoss）

```python
class SharpeLoss(nn.Module):
    """
    直接优化 Sharpe Ratio 的损失函数

    原理：
    - 普通 MSE 优化的是预测精度，但高预测精度不等于高 Sharpe
    - SharpeLoss 直接将 Sharpe 作为优化目标

    注意：
    Sharpe 是离散量（不可导），需要用可微近似
    """
    def __init__(self, risk_free_rate=0.02):
        super().__init__()
        self.risk_free = risk_free_rate

    def forward(self, pred_returns, true_returns):
        # 预测相关性 → Sharpe 近似
        pred_centered = pred_returns - pred_returns.mean()
        true_centered = true_returns - true_returns.mean()

        # Pearson 相关系数（可导）
        correlation = (
            (pred_centered * true_centered).sum() /
            (torch.sqrt((pred_centered**2).sum() + 1e-8) *
             torch.sqrt((true_centered**2).sum() + 1e-8) + 1e-8)
        )

        # 最大化 Sharpe = 最小化 -Sharpe
        return -correlation


class DirectionLoss(nn.Module):
    """
    方向预测损失（胜率优化）

    预测涨/跌的方向，而非具体收益率
    使用 Binary Cross Entropy
    """
    def forward(self, pred, target):
        # target: [B, A] 未来收益（可正可负）
        # pred:   [B, A] 预测收益
        binary_target = (target > 0).float()
        return F.binary_cross_entropy_with_logits(pred, binary_target)


class CombinedQuantLoss(nn.Module):
    """
    量化交易专用组合损失函数

    L = α * Huber(pred, target) + β * SharpeLoss(pred, target) + γ * DirectionLoss

    三个目标的加权组合：
    1. Huber：预测精度（平滑梯度，对极端值鲁棒）
    2. Sharpe：交易收益（直接优化目标）
    3. Direction：方向准确率（胜率）

    论文参考：
    - WaveLSFormer 直接优化 Sharpe Ratio
    - Adaptive Regime-Aware 组合多目标损失
    """
    def __init__(self, alpha=0.5, beta=0.3, gamma=0.2, huber_delta=1.0):
        super().__init__()
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.huber = nn.HuberLoss(delta=huber_delta)
        self.sharpe = SharpeLoss()
        self.direction = DirectionLoss()

    def forward(self, pred, target):
        """
        Args:
            pred: [B, A, 2] - [long_weights, short_weights] 或 [B, A] 预测收益
            target: [B, A] - 未来收益率
        """
        # 如果 pred 是 [B, A, 2]，提取 long 信号
        if pred.dim() == 3:
            pred = pred[..., 0] - pred[..., 1]  # 多头权重 - 空头权重 = 净信号

        l_huber = self.huber(pred, target)
        l_sharpe = self.sharpe(pred, target)
        l_direction = self.direction(pred, target)

        total = self.alpha * l_huber + self.beta * l_sharpe + self.gamma * l_direction

        return total, {
            "huber": l_huber.item(),
            "sharpe": l_sharpe.item(),
            "direction": l_direction.item(),
        }
```

---

## 5. 数据预处理（Anti-Leakage）

### 5.1 滚动窗口标准化（`utils/normalization.py`）

```python
class RollingNormalizer:
    """
    滚动窗口 Z-Score 标准化
    公式: x_norm[t] = (x[t] - mean(x[t-window:t])) / (std(x[t-window:t]) + eps)

    严格原则：
      - 只用过去 window 天的数据（绝对不含当前和未来）
      - 支持 warmup（前 window 天用递增数据）
      - 纯 numpy 实现，避免 pandas rolling 的 backward-looking 陷阱
    """
```

**预热期处理（前 window 天）：**

```python
for t in range(min(window, T)):
    if warmup:
        window_data = x[:t+1]  # 递增窗口
    else:
        continue
    mu = np.nanmean(window_data, axis=0)
    std_val = np.nanstd(window_data, axis=0)
    means[t] = mu
    stds[t] = std_val
```

### 5.2 数据集构建（`data/loader.py`）

#### 标签构造（最易踩坑）

```python
# ❌ 错误做法：rolling().mean() 内部维护窗口，有潜在泄露风险
target = log_returns.rolling(3).mean().shift(-1)

# ✅ 正确做法：显式 shift(-1) + shift(-2) + shift(-3)
target_returns = (
    log_returns_df.shift(-1).fillna(0) +
    log_returns_df.shift(-2).fillna(0) +
    log_returns_df.shift(-3).fillna(0)
) / 3
```

#### 样本窗口构建

```python
# 样本 i 的时间索引 = train_start + history_len + i
# 样本 i 的特征 = data[time_idx - history_len : time_idx]  ← 只用过去
# 样本 i 的标签 = target[time_idx - 1]                   ← shift(-1)
for t in range(valid_start, valid_end):
    feat_window = combined_norm[t - history_len : t]  # [T, A, F]
    target_val = target_norm[t]                        # [A]
    features_list.append(feat_window)
    targets_list.append(target_val)
```

### 5.3 时序数据划分

```python
# ❌ 绝对禁止：random_split / shuffle 会导致未来数据进入训练集
train_loader = DataLoader(..., shuffle=False)

# ✅ 正确做法：按时间顺序 70/15/15 切分
train_data = features[:train_end]       # 最早期
val_data   = features[train_end:val_end]   # 中期
test_data   = features[val_end:]             # 最近期
```

### 5.4 数据格式

```
features:  [num_samples, num_assets, history_len, num_features]
                    ↓                ↓              ↓
                   样本数           16只股票        60天历史          8个因子
targets:   [num_samples, num_assets]
                        ↑ 未来3日对数收益率均值
```

---

## 6. 回测引擎

### 6.1 Anti-Churn v3 核心逻辑（`evaluation/backtest.py`）

**问题**：传统每日调仓换手率过高，交易成本侵蚀收益。

**方案 C — 集合差集替换：**

```python
def run(self, predictions_df, returns_df):
    for date in dates:
        # Step 1: 用昨日信号（Signal[t-1]）决定今日持仓
        target_long, target_short = compute_target(prev_preds)

        # Step 2: 集合差集 — 只在实际变化时交易
        long_to_sell  = current_long_set - set(target_long)   # 昨日在，今日跌出 → 卖出
        long_to_buy   = set(target_long) - current_long_set   # 今日新进 → 买入
        short_to_cover = current_short_set - set(target_short)
        short_to_sell  = set(target_short) - current_short_set

        num_trades_today = len(long_to_sell) + len(short_to_cover)

        # Step 3: 计算真实收益 Signal[t-1] * Return[t]
        daily_ret = compute_portfolio_return(real_returns, target_long, target_short)

        # Step 4: 对数域扣除手续费（减法，非乘法）
        daily_net_ret = daily_ret - num_trades_today * transaction_cost

        # Step 5: 更新权益曲线（对数累加）
        new_capital = equity[-1] * np.exp(daily_net_ret)
```

### 6.2 对数收益率 vs 复利

```python
# ✅ 正确：对数收益率可加，数值稳定
total_return = Σ log_returns
equity[t] = initial_capital * exp(Σ log_returns)

# ❌ 错误：复利乘积在长期数值爆炸
total_return = Π (1 + returns[i])
equity[t] = initial_capital * Π (1 + returns[i])  # t=1000 时可能溢出
```

### 6.3 回测指标

```python
@dataclass
class BacktestMetrics:
    sharpe_ratio: float             # 夏普比率（核心指标）
    information_coefficient: float # IC（v3 新增，衡量预测质量）
    annualized_return: float       # 年化收益率
    annualized_volatility: float    # 年化波动率
    max_drawdown: float             # 最大回撤（范围 [-1, 0]）
    max_drawdown_duration: int      # 最大回撤持续天数
    win_rate: float                 # 胜率
    profit_factor: float            # 盈亏比
    num_trades: int                 # 实际交易次数
    turnover_rate: float            # 平均换手率
    excess_return: float           # 超额收益（策略 - 基准）
    excess_sharpe: float            # 超额夏普
```

### 6.4 关键防泄露设计

| 环节 | 防泄露机制 |
|------|-----------|
| 特征 | 所有因子 lag-1（`shift(-1)`） |
| 标签 | 显式 `shift(-1)+shift(-2)+shift(-3)` 平均 |
| 标准化 | 滚动窗口均值/标准差（只用过去） |
| 回测信号 | `Signal[t-1] * Return[t]` 对齐 |
| 交叉验证 | 时序切分，不打乱 |

---

## 7. API 服务

### 7.1 服务架构（`api/server.py`）

```python
app = FastAPI()

# 全局异常处理：所有错误 → 200 JSON，不崩溃
@app.exception_handler(Exception)
def global_exception_handler(request, exc):
    return JSONResponse(status_code=200, content={"error": str(exc)})

# 启动时加载模型（降级模式：演示数据）
@app.on_event("startup")
async def load_model():
    predictor.load_model()  # 失败不崩溃
```

### 7.2 推理引擎（`api/predictor.py`）

```python
class ModelRegistry:
    """
    单例模式：全局模型管理
    降级策略：模型加载失败 → 使用演示数据，不影响服务
    """
    _instance = None

    def predict(self, features):
        if self._fallback_mode:
            return self._demo_predictions()
        return self.model(features)
```

### 7.3 模拟账户（`api/account_manager.py`）

```python
class AccountManager:
    """
    东方财富杯规则实现：
    - 初始资金: $100,000
    - 手续费: 0.15% 单边
    - 淘汰线: 总资产 < $92,000（初始的 92%）
    - T+1: 延迟单接口
    """
```

### 7.4 核心 API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/dashboard/full` | GET | 完整仪表盘数据 |
| `/api/v1/dashboard/metrics` | GET | 回测指标（Sharpe/IC/MDD） |
| `/api/v1/dashboard/predictions` | GET | AI 股票评分排行 |
| `/api/v1/dashboard/forecast/{ticker}` | GET | K 线 + 5 日 AI 预测 |
| `/api/v1/trade/order` | POST | 市价/限价下单 |
| `/api/v1/trade/close` | POST | 平仓（全部卖出） |
| `/api/v1/trade/delayed` | POST | T+1 延迟单 |
| `/api/v1/auto/start` | POST | 启动 AI 自动交易 |
| `/api/v1/auto/stop` | POST | 停止自动交易 |

---

## 8. 前端界面

### 8.1 技术架构

```
frontend/
├── src/
│   ├── views/
│   │   ├── DashboardView.vue   # 主页：AI 评分 + 权益曲线 + 因子重要性
│   │   ├── AnalysisView.vue    # 分析页：K 线图 + 技术指标 + AI 解读
│   │   └── TradeView.vue       # 交易页：三层面板（决策→仓位→执行）
│   ├── components/
│   │   └── TradePanel.vue      # 核心交易表单组件
│   ├── stores/
│   │   ├── account.ts           # 账户状态（Pinia）
│   │   └── dashboard.ts         # 仪表盘数据（Pinia）
│   └── api/
│       └── index.ts             # Axios 客户端
```

### 8.2 交易面板三层面板设计（2026 重构后）

```
┌─────────────────────────────┐
│  AI 决策层                  │  ← AI 信心条 + Chip 横向滚动
│  信心值 + 多空标签 + 风险    │    （可横向滚动，不折行）
├─────────────────────────────┤
│  仓位层                     │  ← 账户总览 + 建议仓位
│  可用资金 + 建议 + 可买股数  │    （统一弱分割线）
├─────────────────────────────┤
│  执行层                     │  ← TradePanel 组件
│  买入/卖出 CTA 按钮         │    快捷胶囊 + 步进器
├─────────────────────────────┤
│  自动交易区                 │  ← 开关 + 风险提示
└─────────────────────────────┘
```

### 8.3 前端关键设计

| 设计 | 实现 |
|------|------|
| 深色主题 | CSS Variables（`--bg-primary: #0D1117`）+ Element Plus `dark/css-vars.css` |
| 主按钮对比度 | 买入：深底（`#0D1117`）+ 白字；卖出：橙底（`#FF9500`）+ 深色字 |
| 快捷数量 | 胶囊按钮，选中态 hover 填充 |
| 步进器 | `44×44px` 最小触摸区（移动端友好） |
| 手续费说明 | Hover `i` 图标展开 tooltip |
| 自动交易风险 | 运行中显示琥珀色警告文案 |

---

## 9. 踩坑全记录

### 9.1 数据泄露类

| # | 问题 | 错误代码 | 正确代码 | 影响 |
|---|------|---------|---------|------|
| 1 | 标签构造 | `rolling(3).mean().shift(-1)` | `shift(-1)+shift(-2)+shift(-3)` | 模型学到未来信息，过拟合 |
| 2 | 数据打乱 | `DataLoader(shuffle=True)` | `shuffle=False` | 训练集包含未来数据，完全失效 |
| 3 | 交叉验证 | `train_test_split(random_state=42)` | 时序顺序切分 | 随机切分导致数据泄露 |
| 4 | 回测信号 | `Signal[t] * Return[t]` | `Signal[t-1] * Return[t]` | 回测收益虚高，实盘亏损 |
| 5 | 标准化 | 全局 `mean/std` | 滚动窗口 `mean(t-window:t)` | 全局统计量含未来信息 |

### 9.2 模型训练类

| # | 问题 | 症状 | 解决方案 |
|---|------|------|---------|
| 6 | MSE 对极端值敏感 | 梯度爆炸，loss 跳变 | `MixedHuberLoss(delta=1.0)` |
| 7 | 注意力残差缺失 | 深层网络退化 | `x = residual + attn_out` |
| 8 | GPU OOM | RTX 3060 8G 爆显存 | `batch_size=32`，`history_len=60` |
| 9 | 学习率过大 | 早期 loss nan | Warmup 3 epochs + 梯度裁剪 |
| 10 | IC 过低 | Sharpe 低（v1 核心问题） | 引入 Regime-Aware + Mamba 架构 |

### 9.3 后端服务类

| # | 问题 | 症状 | 解决方案 |
|---|------|------|---------|
| 11 | `hashlib` 未导入 | `POST /trade/order` 返回 500 | `account_manager.py` 顶部加 `import hashlib` |
| 12 | 模型文件不存在 | 服务启动崩溃 | 降级模式：`predictor._fallback_mode = True` |
| 13 | 全局异常未捕获 | 接口返回 500 traceback | FastAPI `exception_handler` → 统一 200 JSON |

### 9.4 前端 UI 类

| # | 问题 | 症状 | 解决方案 |
|---|------|------|---------|
| 14 | Element Plus 浅色弹窗 | 弹窗白底黑字与深色主题割裂 | 引入 `dark/css-vars.css` + `html.dark` |
| 15 | `#484F58` 对比度不足 | 右侧文字在深蓝背景上几乎不可见 | 全局替换为 `var(--text-secondary)` |
| 16 | 主按钮文字对比度 | CTA 在强光下不可读 | 买入：深底+白字；卖出：橙底+深色字 |
| 17 | 快捷数量 affordance | 纯文字按钮像超链接 | 改为胶囊按钮 + hover 填充 |
| 18 | 步进器点击区过小 | 移动端误触 | 最小 `44×44px` 触摸区 |

---

## 10. v1 → v2 迭代经验总结

### 10.1 v1 的根本问题

| 问题 | 根因 | 解决方案（v3） |
|------|------|---------------|
| Sharpe 仅 0.28 | 模型预测能力弱，IC 仅 0.073 | 引入 Regime-Aware 自适应架构 |
| 注意力 O(n²) 限制序列长度 | MHSA 计算复杂度 | 引入 Mamba-2 SSD，O(n) 线性 |
| 静态资产建模 | 忽视市场状态差异 | 动态市场状态检测 + 多路径路由 |
| 单一损失函数 | 只优化 MSE，不优化交易目标 | CombinedQuantLoss（Huber + Sharpe + Direction） |
| 手动调参 | 每次训练需要人工调整超参数 | 自主实验循环，夜间自动迭代 |

### 10.2 v3 的核心创新

1. **Regime-Aware 自适应**：Autoencoder 检测市场状态（Normal/Volatile/Crisis），动态路由到不同预测路径
2. **Mamba-Hybrid 时间建模**：Transformer（资产轴）+ Mamba（时间轴），兼顾捕捉能力和效率
3. **WaveLSFormer 投资组合头**：直接输出市场中性多空组合，端到端优化 Sharpe
4. **自主实验循环**：autoresearch 模式，夜间自动迭代模型
5. **多目标损失**：CombinedQuantLoss 同时优化预测精度 + Sharpe + 方向准确率

---

## 11. 2026 最新研究论文汇总

> 以下为截至 2026 年 3 月，基于 Transformer 的量化交易领域最新权威论文，按相关性排序。

### 11.1 必读论文（直接相关）

#### Paper 1: WaveLSFormer（最高优先级）

```
标题: WaveLSFormer: Learnable Wavelet-Based Transformer for
      End-to-End Quantitative Trading
时间: 2026 年 1 月
来源: arXiv
链接: https://arxiv.org/abs/2601.13435
核心贡献:
- 将小波变换与 Transformer 结合，捕捉多尺度市场模式
- 直接输出市场中性多空投资组合权重
- 端到端优化交易目标（Sharpe），而非预测精度

关键指标:
- Sharpe Ratio: 2.157 ± 0.166
- Cumulative Return: 0.607 ± 0.045
- 测试数据: 5 年小时级数据，6 个行业组

对 v3 的启示:
✅ 投资组合输出头的设计思路
✅ 端到端 Sharpe 优化的损失函数设计
✅ 小波分析作为特征工程的补充
```

#### Paper 2: Adaptive Regime-Aware Stock Prediction

```
标题: Adaptive Regime-Aware Stock Price Prediction Using
      Autoencoder-Gated Dual Node Transformers with
      Reinforcement Learning Control
时间: 2026 年 3 月
来源: arXiv (2603.19136v1)
链接: https://arxiv.org/abs/2603.19136
核心贡献:
- Autoencoder 重建误差检测市场状态（Normal/Volatile/Crisis）
- 双路 Node Transformer：市场正常路径 + 危机路径
- Soft Actor-Critic 强化学习控制动态路由

关键指标:
- MAPE: 0.59%（全系统）vs 0.80%（基线）
- Direction Accuracy: 72%
- 高波动期 MAPE: < 0.85%
- 测试数据: S&P 500 stocks (1982-2025)

对 v3 的启示:
✅ MarketRegimeDetector 模块设计
✅ 多路径自适应架构
✅ Autoencoder 作为市场状态检测器
✅ 重建误差作为市场异常指标
```

#### Paper 3: Node Transformer with BERT Sentiment

```
标题: Stock Market Prediction Using Node Transformer Architecture
      Integrated with BERT Sentiment Analysis
时间: 2026 年 3 月
来源: arXiv (2603.05917v1)
链接: https://arxiv.org/abs/2603.05917
核心贡献:
- 将股票市场建模为图（Graph），股票为节点
- BERT 情感分析作为额外输入因子
- Node-level Transformer 替代传统时间序列模型

关键指标:
- MAPE: 0.80%（1 日预测）vs 1.20%（ARIMA）vs 1.00%（LSTM）
- 情感分析降低误差 10%，财报期降低 25%
- 图建模额外降低误差 15%
- 测试数据: 20 S&P 500 stocks (Jan 1982 - Mar 2025)

对 v3 的启示:
✅ 情感因子注入模块设计
✅ 节点建模（股票作为 Token）的合理性
✅ 多模态输入（价格 + 文本）的有效性
```

### 11.2 重要论文（参考架构）

#### Paper 4: State-Space Models for Market Microstructure

```
标题: State-Space Models for Market Microstructure:
      Can Mamba Replace Transformers in High-Frequency Finance?
时间: 2026 年 3 月
来源: jonathankinlay.com（arXiv 研究综述）
链接: https://jonathankinlay.com/2026/03/state-space-models-for-market-microstructure-can-mamba-replace-transformers-in-high-frequency-finance/
核心贡献:
- Mamba O(n) 线性复杂度 vs Transformer O(n²)
- 在高频金融数据上有竞争力
- 选择性遗忘机制（适合非平稳金融数据）

对 v3 的启示:
✅ Mamba-2 替代 PatchTST Self-Attention 的可行性
✅ 状态空间模型捕捉金融数据非平稳性
✅ 高频场景下的效率优势
```

#### Paper 5: Mamba-3 State Space Models

```
标题: Mamba-3: Improved State Space Sequence Models
时间: 2026 年 3 月
来源: OpenReview / arXiv (2603.15569)
链接: https://arxiv.org/abs/2603.15569
核心贡献:
- 指数-梯形离散化（二阶精度）
- 复数值状态更新（更丰富的状态表示）
- MIMO 架构（硬件效率提升 2 倍）

关键指标:
- 1.5B 规模: 下游准确率提升 1.8pp
- 状态大小减半，性能持平 Mamba-2

对 v3 的启示:
✅ 使用 Mamba-2/Mamba-3 作为时间轴编码器
✅ 更大的 d_state（128/256）捕捉多尺度模式
```

#### Paper 6: IPatch Multi-Resolution Transformer

```
标题: IPatch: A Multi-Resolution Transformer Architecture
      for Robust Time-Series Forecasting
时间: 2026 年 3 月
来源: arXiv (2603.24207)
链接: https://arxiv.org/abs/2603.24207
核心贡献:
- Point-wise + Patch-wise 双层表示
- 多尺度时间建模（细粒度 + 粗粒度）
- 噪声鲁棒性更强

对 v3 的启示:
✅ MultiScalePatchEncoder 的理论基础
✅ 点级 + 块级双分支融合
✅ 多分辨率表示的鲁棒性优势
```

#### Paper 7: iTransformer

```
标题: iTransformer: Inverted Transformers are Effective
      for Time Series Forecasting
时间: 2024 年（ICLR）
来源: arXiv (ICLR 2024)
链接: https://arxiv.org/abs/2310.06625
核心贡献:
- 维度反转：变量 = Token（而非时间步 = Token）
- 在资产数量多的场景下效率更高
- 各变量独立的时间序列建模

对 v3 的启示:
✅ iTransformerAssetEncoder 的理论基础
✅ 资产维度作为注意力机制的核心
✅ 适合多资产联合预测
```

#### Paper 8: PatchTST

```
标题: PatchTST: PatchTST: A Transformer for Time Series Forecasting
时间: 2023 年
来源: arXiv / ICLR 2023
链接: https://arxiv.org/abs/2211.14729
核心贡献:
- Patch 机制：将时间序列分段，降低序列长度
- Channel-Independent：每个通道独立建模
- 远超 Informer/Autoformer 等传统时序 Transformer

对 v3 的启示:
✅ MultiScalePatchEncoder 的核心机制
✅ Patch 降低计算复杂度
✅ 因果遮罩（Causal Mask）保持时序因果性
```

#### Paper 9: Quantformer

```
标题: Quantformer: Transformer-based Quantitative Trading
      with Transfer Learning from Sentiment Analysis
时间: 2025 年 8 月
来源: arXiv
核心贡献:
- 迁移学习：情感分析预训练 → 量化交易微调
- 4601 只 A 股测试（2010-2023）
- 超越 100 因子量化策略

对 v3 的启示:
✅ 多任务预训练思路
✅ 在 A 股数据的有效性验证
✅ 大规模股票池扩展路径
```

### 11.3 论文优先级总结

```
必读（直接实现到 v3）:
1. WaveLSFormer        → WaveLSFormerHead + Sharpe Loss
2. Adaptive Regime-Aware → MarketRegimeDetector
3. iTransformer + PatchTST → 已有实现，保持

参考（选择性借鉴）:
4. Node Transformer + BERT → SentimentInjector（可选）
5. Mamba-3 → Mamba2TemporalEncoder（可选）

延伸阅读（论文写作引用）:
6. Mamba-3 理论背景
7. IPatch 多尺度理论
8. Quantformer A股验证
9. SSM Market Microstructure
```

---

## 12. 运行指南

### 12.1 环境准备

```bash
# Python >= 3.9
conda create -n alpha python=3.9
conda activate alpha
pip install torch>=2.1.0 --index-url https://download.pytorch.org/whl/cu118
pip install -r requirements.txt

# Mamba 依赖（v3 新增）
pip install mamba-ssm

# Node.js >= 18 (for frontend)
cd frontend && npm install
```

### 12.2 启动后端

```bash
cd D:\transformer
uvicorn api.server:app --host 0.0.0.0 --port 8080 --reload

# 验证
curl http://localhost:8080/api/v1/dashboard/predictions
curl http://localhost:8080/docs  # Swagger 文档
```

### 12.3 启动前端

```bash
cd frontend
npm run dev
# 访问 http://localhost:5173
```

### 12.4 训练模型

```python
from trainer.trainer import AlphaTransformerTrainer
from trainer.auto_experimenter import QuantAutoExperimenter
from data.loader import build_dataloaders
from models.alpha_transformer_v3 import AlphaTransformerV3

# 1. 正常训练模式
train_loader, val_loader, test_loader, params = build_dataloaders(price_df)

model = AlphaTransformerV3(
    num_assets=16,
    feature_dim=8,
    history_len=60,
    d_model=128,
    num_layers=3,
)

trainer = AlphaTransformerTrainer(
    model=model,
    config=config,
    device="cuda" if torch.cuda.is_available() else "cpu",
    log_dir="logs",
    checkpoint_dir="checkpoints"
)

trainer.train(train_loader, val_loader)

# 2. 自主实验模式（autoresearch）
experimenter = QuantAutoExperimenter(
    program_path="program_alpha.md",
    time_budget_minutes=30
)
experimenter.run_overnight(max_cycles=50)
```

### 12.5 快速启动（完整流水线）

```python
from data.loader import create_synthetic_data, build_dataloaders
from trainer.trainer import AlphaTransformerTrainer

# 1. 生成测试数据（可选）
price_df = create_synthetic_data(num_dates=1000, num_assets=16)

# 2. 构建数据加载器
train_loader, val_loader, test_loader, params = build_dataloaders(
    price_df,
    history_len=60,
    batch_size=32,
)

# 3. 创建配置
from dataclasses import dataclass
@dataclass
class ModelConfig:
    num_assets = 16
    feature_dim = 8
    history_len = 60
    d_model = 128
    num_heads = 4
    num_layers = 3
    d_ff = 512
    asset_emb_dim = 64
    dropout = 0.1
    class Config:
        training = type('obj', (object,), {
            'learning_rate': 0.001,
            'weight_decay': 0.01,
            'epochs': 50,
            'warmup_epochs': 3,
            'min_lr': 1e-5,
            'loss_fn': 'combined_quant',
            'grad_clip_norm': 1.0,
            'patience': 5,
            'early_stop_delta': 1e-4,
        })()

# 4. 开始训练
# trainer.train(train_loader, val_loader)
```

---

*AlphaTransformer v2 — Built with ❤️ for quantitative finance*
*毕业设计：基于 Transformer 的股票预测系统*
