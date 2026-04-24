---
source_file: "d:\transformer\utils\normalization.py"
type: "rationale"
community: "AlphaTransformer Core Models"
location: "L120"
tags:
  - graphify/rationale
  - graphify/EXTRACTED
  - community/AlphaTransformer_Core_Models
---

# 使用已有参数对数据进行归一化（用于 test/val 阶段）         注意：test 阶段也需要用滚动窗口，因为每个时间点的归一化参数可能不同

## Connections
- [[.transform()]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/EXTRACTED #community/AlphaTransformer_Core_Models