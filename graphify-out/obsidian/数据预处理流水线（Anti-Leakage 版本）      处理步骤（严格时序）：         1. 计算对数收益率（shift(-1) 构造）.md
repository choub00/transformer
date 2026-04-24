---
source_file: "d:\transformer\data\loader.py"
type: "rationale"
community: "AlphaTransformer Core Models"
location: "L79"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/AlphaTransformer_Core_Models
---

# 数据预处理流水线（Anti-Leakage 版本）      处理步骤（严格时序）：         1. 计算对数收益率（shift(-1) 构造）

## Connections
- [[DataProcessor]] - `rationale_for` [EXTRACTED]
- [[PanelNormalizer]] - `uses` [INFERRED]
- [[RollingNormalizer]] - `uses` [INFERRED]

#graphify/rationale #graphify/INFERRED #community/AlphaTransformer_Core_Models