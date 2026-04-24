---
source_file: "d:\transformer\models\alpha_transformer.py"
type: "rationale"
community: "AlphaTransformer Core Models"
location: "L142"
tags:
  - graphify/rationale
  - graphify/EXTRACTED
  - community/AlphaTransformer_Core_Models
---

# Args:             query/key/value: [Batch, Seq, d_model]             attn_mask:

## Connections
- [[.forward()_2]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/EXTRACTED #community/AlphaTransformer_Core_Models