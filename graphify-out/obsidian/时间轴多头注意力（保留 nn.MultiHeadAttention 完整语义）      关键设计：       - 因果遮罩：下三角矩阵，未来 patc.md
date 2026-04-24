---
source_file: "d:\transformer\models\alpha_transformer_2026.py"
type: "rationale"
community: "AlphaTransformer 2026 Adaptive Layers"
location: "L190"
tags:
  - graphify/rationale
  - graphify/EXTRACTED
  - community/AlphaTransformer_2026_Adaptive_Layers
---

# 时间轴多头注意力（保留 nn.MultiHeadAttention 完整语义）      关键设计：       - 因果遮罩：下三角矩阵，未来 patc

## Connections
- [[TemporalMultiHeadAttention]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/EXTRACTED #community/AlphaTransformer_2026_Adaptive_Layers