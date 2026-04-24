---
source_file: "d:\transformer\Stock Forecast\api\trading_engine.py"
type: "rationale"
community: "Stock Forecast API Predictor"
location: "L332"
tags:
  - graphify/rationale
  - graphify/EXTRACTED
  - community/Stock_Forecast_API_Predictor
---

# 量化交易核心引擎 (线程安全)          设计原则:     - 状态全在实例属性中，由 _lock 保护     - 不持有 HTTP 请求上

## Connections
- [[AlphaPredictor]] - `uses` [INFERRED]
- [[TradingEngine]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/EXTRACTED #community/Stock_Forecast_API_Predictor