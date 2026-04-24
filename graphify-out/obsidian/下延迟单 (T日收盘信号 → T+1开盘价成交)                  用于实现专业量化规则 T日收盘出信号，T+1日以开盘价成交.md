---
source_file: "d:\transformer\Stock Forecast\api\trading_engine.py"
type: "rationale"
community: "Stock Forecast API Predictor"
location: "L543"
tags:
  - graphify/rationale
  - graphify/EXTRACTED
  - community/Stock_Forecast_API_Predictor
---

# 下延迟单 (T日收盘信号 → T+1开盘价成交)                  用于实现专业量化规则: T日收盘出信号，T+1日以开盘价成交

## Connections
- [[.place_delayed_order()]] - `rationale_for` [EXTRACTED]
- [[AlphaPredictor]] - `uses` [INFERRED]

#graphify/rationale #graphify/EXTRACTED #community/Stock_Forecast_API_Predictor