---
source_file: "d:\transformer\api\predictor.py"
type: "rationale"
community: "AlphaTransformer Core Models"
location: "L51"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/AlphaTransformer_Core_Models
---

# 加载模型检查点到指定设备         健壮性保证：           - map_location 强制 CPU（防止 CUDA OOM 导致 500

## Connections
- [[.load()]] - `rationale_for` [EXTRACTED]
- [[AlphaTransformer]] - `uses` [INFERRED]
- [[AlphaTransformer2026]] - `uses` [INFERRED]
- [[AlphaTransformerV2]] - `uses` [INFERRED]
- [[PanelNormalizer]] - `uses` [INFERRED]
- [[RollingNormalizer]] - `uses` [INFERRED]

#graphify/rationale #graphify/INFERRED #community/AlphaTransformer_Core_Models