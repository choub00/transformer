---
source_file: "d:\transformer\Stock Forecast\api\trading_engine.py"
type: "rationale"
community: "Stock Forecast API Predictor"
location: "L211"
tags:
  - graphify/rationale
  - graphify/EXTRACTED
  - community/Stock_Forecast_API_Predictor
---

# 延迟订单 (T+1 开盘价成交)          用于实现 T 日收盘出信号 → T+1 日开盘价成交的规则

## Connections
- [[AlphaPredictor]] - `uses` [INFERRED]
- [[DelayedOrder]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/EXTRACTED #community/Stock_Forecast_API_Predictor