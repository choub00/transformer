---
source_file: "d:\transformer\api\trading.py"
type: "rationale"
community: "Trading Account Manager + Auto"
location: "L22"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Trading_Account_Manager_+_Auto
---

# 下单接口（支持市价/限价）      错误码：       - INSUFFICIENT_FUNDS: 资金不足       - POSITION_NO

## Connections
- [[AISignal]] - `uses` [INFERRED]
- [[AutoTradeStatus]] - `uses` [INFERRED]
- [[DelayedOrderRequest]] - `uses` [INFERRED]
- [[OrderRequest]] - `uses` [INFERRED]
- [[OrderResponse]] - `uses` [INFERRED]
- [[TradeHistory]] - `uses` [INFERRED]
- [[TradeLog]] - `uses` [INFERRED]
- [[place_order()]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/INFERRED #community/Trading_Account_Manager_+_Auto