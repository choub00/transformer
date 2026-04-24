---
source_file: "d:\transformer\Stock Forecast\api\routes.py"
type: "rationale"
community: "Stock Forecast API Predictor"
location: "L653"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Stock_Forecast_API_Predictor
---

# 下延迟单 (T+1)          T 日收盘出信号 → T+1 日开盘价成交。     适用于专业量化规则的信号执行。

## Connections
- [[AlphaPredictor]] - `uses` [INFERRED]
- [[OrderType]] - `uses` [INFERRED]
- [[TradeReason]] - `uses` [INFERRED]
- [[TradeSide]] - `uses` [INFERRED]
- [[TradingEngine]] - `uses` [INFERRED]
- [[place_delayed_order()_1]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/INFERRED #community/Stock_Forecast_API_Predictor