---
source_file: "d:\transformer\data\loader.py"
type: "rationale"
community: "AlphaTransformer Core Models"
location: "L118"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/AlphaTransformer_Core_Models
---

# 处理原始价格数据，生成模型输入          Args:             price_df:  [Date, Asset] 收盘价（Raw C

## Connections
- [[.process_raw_data()]] - `rationale_for` [EXTRACTED]
- [[PanelNormalizer]] - `uses` [INFERRED]
- [[RollingNormalizer]] - `uses` [INFERRED]

#graphify/rationale #graphify/INFERRED #community/AlphaTransformer_Core_Models