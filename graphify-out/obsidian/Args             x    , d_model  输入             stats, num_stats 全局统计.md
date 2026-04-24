---
source_file: "d:\transformer\models\alpha_transformer_2026.py"
type: "rationale"
community: "AlphaTransformer 2026 Adaptive Layers"
location: "L64"
tags:
  - graphify/rationale
  - graphify/EXTRACTED
  - community/AlphaTransformer_2026_Adaptive_Layers
---

# Args:             x:    [*, d_model]  输入             stats:[*, num_stats] 全局统计

## Connections
- [[.forward()_9]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/EXTRACTED #community/AlphaTransformer_2026_Adaptive_Layers