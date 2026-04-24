---
source_file: "d:\transformer\data\loader.py"
type: "rationale"
community: "AlphaTransformer Core Models"
location: "L1"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/AlphaTransformer_Core_Models
---

# 数据加载与预处理模块（严格 Anti-Leakage）  核心原则：   1. 所有未来数据不得进入当前时间点的特征   2. 目标值使用显式 shif

## Connections
- [[PanelNormalizer]] - `uses` [INFERRED]
- [[RollingNormalizer]] - `uses` [INFERRED]
- [[loader.py]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/INFERRED #community/AlphaTransformer_Core_Models