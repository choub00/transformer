---
source_file: "d:\transformer\data\loader.py"
type: "rationale"
community: "AlphaTransformer Core Models"
location: "L326"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/AlphaTransformer_Core_Models
---

# 生成合成价格数据用于测试      Args:         num_dates:  交易日数量         num_assets: 资产数量

## Connections
- [[PanelNormalizer]] - `uses` [INFERRED]
- [[RollingNormalizer]] - `uses` [INFERRED]
- [[create_synthetic_data()]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/INFERRED #community/AlphaTransformer_Core_Models