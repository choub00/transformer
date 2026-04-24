---
source_file: "d:\transformer\trainer\trainer.py"
type: "rationale"
community: "AlphaTransformer Core Models"
location: "L23"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/AlphaTransformer_Core_Models
---

# Mixed Huber Loss: 结合 MSE 和 MAE 的优点      当 |error| <= delta 时使用 MSE（平滑梯度）

## Connections
- [[AlphaTransformer]] - `uses` [INFERRED]
- [[AlphaTransformerV2]] - `uses` [INFERRED]
- [[BacktestEngine]] - `uses` [INFERRED]
- [[MixedHuberLoss]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/INFERRED #community/AlphaTransformer_Core_Models