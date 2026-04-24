---
source_file: "d:\transformer\Stock Forecast\api\routes.py"
type: "rationale"
community: "Stock Forecast API Predictor"
location: "L780"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Stock_Forecast_API_Predictor
---

# 获取当前 AI 信号          包括：     - 所有股票的 AI 评分排名     - 当前持仓与目标持仓的调仓信号

## Connections
- [[AlphaPredictor]] - `uses` [INFERRED]
- [[OrderType]] - `uses` [INFERRED]
- [[TradeReason]] - `uses` [INFERRED]
- [[TradeSide]] - `uses` [INFERRED]
- [[TradingEngine]] - `uses` [INFERRED]
- [[get_ai_signals()]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/INFERRED #community/Stock_Forecast_API_Predictor