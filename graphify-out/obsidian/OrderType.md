---
source_file: "d:\transformer\Stock Forecast\api\trading_engine.py"
type: "code"
community: "Stock Forecast API Predictor"
location: "L56"
tags:
  - graphify/code
  - graphify/INFERRED
  - community/Stock_Forecast_API_Predictor
---

# OrderType

## Connections
- [[AIAdviceResponse]] - `uses` [INFERRED]
- [[AccountResponse]] - `uses` [INFERRED]
- [[AlphaPredictor]] - `uses` [INFERRED]
- [[AutoLogsResponse]] - `uses` [INFERRED]
- [[AutoStartRequest]] - `uses` [INFERRED]
- [[AutoStatusResponse]] - `uses` [INFERRED]
- [[ConfigRequest]] - `uses` [INFERRED]
- [[ConfigResponse]] - `uses` [INFERRED]
- [[DelayedOrderRequest_1]] - `uses` [INFERRED]
- [[DelayedOrderResponse]] - `uses` [INFERRED]
- [[Enum]] - `inherits` [EXTRACTED]
- [[HealthResponse_1]] - `uses` [INFERRED]
- [[KLineResponse_1]] - `uses` [INFERRED]
- [[MetricsResponse]] - `uses` [INFERRED]
- [[OrderRequest_1]] - `uses` [INFERRED]
- [[OrderResponse_1]] - `uses` [INFERRED]
- [[PositionItem]] - `uses` [INFERRED]
- [[PredictionItem]] - `uses` [INFERRED]
- [[PredictionsResponse_1]] - `uses` [INFERRED]
- [[TradeHistoryItem]] - `uses` [INFERRED]
- [[TradeHistoryResponse]] - `uses` [INFERRED]
- [[str]] - `inherits` [EXTRACTED]
- [[trading_engine.py]] - `contains` [EXTRACTED]
- [[下单          支持市价单和限价单。     自动计算手续费并更新持仓。]] - `uses` [INFERRED]
- [[下延迟单 (T+1)          T 日收盘出信号 → T+1 日开盘价成交。     适用于专业量化规则的信号执行。]] - `uses` [INFERRED]
- [[启动自动交易          AI 将自动：     1. 每 N 秒扫描市场     2. 检查止损止盈条件     3. 根据 Top-N 调]] - `uses` [INFERRED]
- [[将持仓字典转换为 PositionItem]] - `uses` [INFERRED]
- [[平仓          卖出全部持仓。]] - `uses` [INFERRED]
- [[获取 AI 预测排名          返回股票的 AI 评分、方向、置信度等信息。]] - `uses` [INFERRED]
- [[获取 K线数据与 AI 预测          返回：     - 历史 K线数据 (OHLCV)     - AI 预测的未来走势]] - `uses` [INFERRED]
- [[获取历史成交          返回最近的成交记录列表。]] - `uses` [INFERRED]
- [[获取当前 AI 信号          包括：     - 所有股票的 AI 评分排名     - 当前持仓与目标持仓的调仓信号]] - `uses` [INFERRED]
- [[重置账户          清空所有持仓、成交历史、资金曲线，     恢复到初始资金状态。]] - `uses` [INFERRED]

#graphify/code #graphify/INFERRED #community/Stock_Forecast_API_Predictor