---
type: community
cohesion: 0.07
members: 42
---

# AlphaTransformer 2026 Adaptive Layers

**Cohesion:** 0.07 - loosely connected
**Members:** 42 nodes

## Members
- [[.__init__()_33]] - code - d:\transformer\models\alpha_transformer_2026.py
- [[.__init__()_41]] - code - d:\transformer\models\alpha_transformer_2026.py
- [[.__init__()_34]] - code - d:\transformer\models\alpha_transformer_2026.py
- [[.__init__()_35]] - code - d:\transformer\models\alpha_transformer_2026.py
- [[.__init__()_39]] - code - d:\transformer\models\alpha_transformer_2026.py
- [[.__init__()_40]] - code - d:\transformer\models\alpha_transformer_2026.py
- [[.__init__()_37]] - code - d:\transformer\models\alpha_transformer_2026.py
- [[.__init__()_38]] - code - d:\transformer\models\alpha_transformer_2026.py
- [[.__init__()_36]] - code - d:\transformer\models\alpha_transformer_2026.py
- [[._build_causal_mask()_2]] - code - d:\transformer\models\alpha_transformer_2026.py
- [[.forward()_9]] - code - d:\transformer\models\alpha_transformer_2026.py
- [[.forward()_10]] - code - d:\transformer\models\alpha_transformer_2026.py
- [[.forward()_11]] - code - d:\transformer\models\alpha_transformer_2026.py
- [[.forward()_15]] - code - d:\transformer\models\alpha_transformer_2026.py
- [[.forward()_16]] - code - d:\transformer\models\alpha_transformer_2026.py
- [[.forward()_13]] - code - d:\transformer\models\alpha_transformer_2026.py
- [[.forward()_14]] - code - d:\transformer\models\alpha_transformer_2026.py
- [[.forward()_12]] - code - d:\transformer\models\alpha_transformer_2026.py
- [[AdaptiveLayerNorm]] - code - d:\transformer\models\alpha_transformer_2026.py
- [[AlphaTransformer-2026 2026 SOTA iTransformer + PatchTST 混合架构  核心设计（严格基于 Trans]] - rationale - d:\transformer\models\alpha_transformer_2026.py
- [[Args             x           BatchAssets, num_patches, d_model]] - rationale - d:\transformer\models\alpha_transformer_2026.py
- [[Args             x    , d_model  输入             stats, num_stats 全局统计]] - rationale - d:\transformer\models\alpha_transformer_2026.py
- [[Args             x Batch, Assets, Time, Features          Returns]] - rationale - d:\transformer\models\alpha_transformer_2026.py
- [[GRN 带上下文（Context）的门控残差网络]] - rationale - d:\transformer\models\alpha_transformer_2026.py
- [[GatedResidualNetwork_1]] - code - d:\transformer\models\alpha_transformer_2026.py
- [[Patchify]] - code - d:\transformer\models\alpha_transformer_2026.py
- [[Returns             out      B, A, d_model             all_attn 注意力权重列表]] - rationale - d:\transformer\models\alpha_transformer_2026.py
- [[Returns             out      Batch, Assets, d_model             attn_map]] - rationale - d:\transformer\models\alpha_transformer_2026.py
- [[Returns             temporal_out BA, d_model  融合后的时间表示             all_at]] - rationale - d:\transformer\models\alpha_transformer_2026.py
- [[SparseCrossAssetAttention]] - code - d:\transformer\models\alpha_transformer_2026.py
- [[Spatio-Temporal Block：交替执行时间轴和资产轴建模      数据流：         Input B, A, T, d_model]] - rationale - d:\transformer\models\alpha_transformer_2026.py
- [[SpatioTemporalBlock]] - code - d:\transformer\models\alpha_transformer_2026.py
- [[TemporalBlock]] - code - d:\transformer\models\alpha_transformer_2026.py
- [[TemporalEncoder]] - code - d:\transformer\models\alpha_transformer_2026.py
- [[TemporalMultiHeadAttention]] - code - d:\transformer\models\alpha_transformer_2026.py
- [[alpha_transformer_2026.py]] - code - d:\transformer\models\alpha_transformer_2026.py
- [[可学习的 Patch 化层      将时间序列 B, A, T, D → B, A, num_patches, patch_size  D]] - rationale - d:\transformer\models\alpha_transformer_2026.py
- [[时间轴单层：MHSA + DepthwiseConv + GRN（修复注意力残差 bug）]] - rationale - d:\transformer\models\alpha_transformer_2026.py
- [[时间轴多头注意力（保留 nn.MultiHeadAttention 完整语义）      关键设计：       - 因果遮罩：下三角矩阵，未来 patc]] - rationale - d:\transformer\models\alpha_transformer_2026.py
- [[时间轴编码器（Per-Asset PatchTST）      多尺度 Patching：       - 低分辨率（patch_size=20）：捕捉长]] - rationale - d:\transformer\models\alpha_transformer_2026.py
- [[稀疏交叉资产注意力（SCA）      核心设计：       - Top-K 稀疏连接：每个资产只关注与其最相似的 K 个邻居       - 动态邻]] - rationale - d:\transformer\models\alpha_transformer_2026.py
- [[自适应层归一化 (Adaptive Layer Normalization)      原理：将输入的全局统计量注入归一化层，使其对分布漂移更鲁棒]] - rationale - d:\transformer\models\alpha_transformer_2026.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/AlphaTransformer_2026_Adaptive_Layers
SORT file.name ASC
```

## Connections to other communities
- 2 edges to [[_COMMUNITY_AlphaTransformer Core Models]]
- 1 edge to [[_COMMUNITY_Thesis Debug + Cross-File Analysis]]

## Top bridge nodes
- [[.__init__()_41]] - degree 12, connects to 2 communities
- [[alpha_transformer_2026.py]] - degree 10, connects to 1 community