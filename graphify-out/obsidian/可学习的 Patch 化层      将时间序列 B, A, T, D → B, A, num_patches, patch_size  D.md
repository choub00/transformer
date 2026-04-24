---
source_file: "d:\transformer\models\alpha_transformer_2026.py"
type: "rationale"
community: "AlphaTransformer 2026 Adaptive Layers"
location: "L127"
tags:
  - graphify/rationale
  - graphify/EXTRACTED
  - community/AlphaTransformer_2026_Adaptive_Layers
---

# 可学习的 Patch 化层      将时间序列 [B, A, T, D] → [B, A, num_patches, patch_size * D]

## Connections
- [[Patchify]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/EXTRACTED #community/AlphaTransformer_2026_Adaptive_Layers