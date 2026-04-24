---
source_file: "d:\transformer\models\alpha_transformer_2026.py"
type: "rationale"
community: "AlphaTransformer 2026 Adaptive Layers"
location: "L600"
tags:
  - graphify/rationale
  - graphify/EXTRACTED
  - community/AlphaTransformer_2026_Adaptive_Layers
---

# Returns:             out:      [B, A, d_model]             all_attn: 注意力权重列表

## Connections
- [[.forward()_16]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/EXTRACTED #community/AlphaTransformer_2026_Adaptive_Layers