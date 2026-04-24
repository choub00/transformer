---
source_file: "d:\transformer\Stock Forecast\api\routes.py"
type: "rationale"
community: "Stock Forecast API Predictor"
location: "L419"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Stock_Forecast_API_Predictor
---

# 获取 K线数据与 AI 预测          返回：     - 历史 K线数据 (OHLCV)     - AI 预测的未来走势

## Connections
- [[AlphaPredictor]] - `uses` [INFERRED]
- [[OrderType]] - `uses` [INFERRED]
- [[TradeReason]] - `uses` [INFERRED]
- [[TradeSide]] - `uses` [INFERRED]
- [[TradingEngine]] - `uses` [INFERRED]
- [[get_kline()]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/INFERRED #community/Stock_Forecast_API_Predictor