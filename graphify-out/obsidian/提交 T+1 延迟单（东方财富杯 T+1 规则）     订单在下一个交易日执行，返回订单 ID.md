---
source_file: "d:\transformer\api\trading.py"
type: "rationale"
community: "Trading Account Manager + Auto"
location: "L99"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Trading_Account_Manager_+_Auto
---

# 提交 T+1 延迟单（东方财富杯 T+1 规则）     订单在下一个交易日执行，返回订单 ID

## Connections
- [[AISignal]] - `uses` [INFERRED]
- [[AutoTradeStatus]] - `uses` [INFERRED]
- [[DelayedOrderRequest]] - `uses` [INFERRED]
- [[OrderRequest]] - `uses` [INFERRED]
- [[OrderResponse]] - `uses` [INFERRED]
- [[TradeHistory]] - `uses` [INFERRED]
- [[TradeLog]] - `uses` [INFERRED]
- [[place_delayed_order()]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/INFERRED #community/Trading_Account_Manager_+_Auto