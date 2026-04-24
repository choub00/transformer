---
source_file: "d:\transformer\Stock Forecast\api\predictor.py"
type: "code"
community: "Stock Forecast API Predictor"
location: "L15"
tags:
  - graphify/code
  - graphify/INFERRED
  - community/Stock_Forecast_API_Predictor
---

# AlphaPredictor

## Connections
- [[.__init__()_42]] - `method` [EXTRACTED]
- [[.__new__()]] - `method` [EXTRACTED]
- [[._generate_mock_data()]] - `method` [EXTRACTED]
- [[._get_direction()]] - `method` [EXTRACTED]
- [[._hash_score()]] - `method` [EXTRACTED]
- [[.dashboard_data()]] - `method` [EXTRACTED]
- [[.get_market_sentiment()]] - `method` [EXTRACTED]
- [[.predict()_1]] - `method` [EXTRACTED]
- [[.predict_batch()]] - `method` [EXTRACTED]
- [[.rank_stocks()]] - `method` [EXTRACTED]
- [[AI 股票预测器单例          提供股票评分和排名预测。]] - `rationale_for` [EXTRACTED]
- [[AIAdviceResponse]] - `uses` [INFERRED]
- [[AccountResponse]] - `uses` [INFERRED]
- [[AccountStats]] - `uses` [INFERRED]
- [[AlphaTransformer Trading Engine - 量化交易核心引擎  本模块实现了符合专业机构标准的量化交易逻辑：  1. 账户资金闭]] - `uses` [INFERRED]
- [[AutoLogsResponse]] - `uses` [INFERRED]
- [[AutoStartRequest]] - `uses` [INFERRED]
- [[AutoStatusResponse]] - `uses` [INFERRED]
- [[ConfigRequest]] - `uses` [INFERRED]
- [[ConfigResponse]] - `uses` [INFERRED]
- [[DelayedOrder]] - `uses` [INFERRED]
- [[DelayedOrderRequest_1]] - `uses` [INFERRED]
- [[DelayedOrderResponse]] - `uses` [INFERRED]
- [[HealthResponse_1]] - `uses` [INFERRED]
- [[KLineResponse_1]] - `uses` [INFERRED]
- [[MetricsResponse]] - `uses` [INFERRED]
- [[OrderRequest_1]] - `uses` [INFERRED]
- [[OrderResponse_1]] - `uses` [INFERRED]
- [[OrderType]] - `uses` [INFERRED]
- [[Position_2]] - `uses` [INFERRED]
- [[PositionItem]] - `uses` [INFERRED]
- [[PredictionItem]] - `uses` [INFERRED]
- [[PredictionsResponse_1]] - `uses` [INFERRED]
- [[RebalanceConfig]] - `uses` [INFERRED]
- [[TradeHistoryItem]] - `uses` [INFERRED]
- [[TradeHistoryResponse]] - `uses` [INFERRED]
- [[TradeReason]] - `uses` [INFERRED]
- [[TradeRecord]] - `uses` [INFERRED]
- [[TradeSide]] - `uses` [INFERRED]
- [[TradingEngine]] - `uses` [INFERRED]
- [[predictor.py_1]] - `contains` [EXTRACTED]
- [[下单          支持市价单和限价单。     自动计算手续费并更新持仓。]] - `uses` [INFERRED]
- [[下延迟单 (T+1)          T 日收盘出信号 → T+1 日开盘价成交。     适用于专业量化规则的信号执行。]] - `uses` [INFERRED]
- [[下延迟单 (T日收盘信号 → T+1开盘价成交)                  用于实现专业量化规则 T日收盘出信号，T+1日以开盘价成交]] - `uses` [INFERRED]
- [[单只股票持仓          Attributes         ticker 股票代码         quantity 持仓数量]] - `uses` [INFERRED]
- [[启动自动交易          AI 将自动：     1. 每 N 秒扫描市场     2. 检查止损止盈条件     3. 根据 Top-N 调]] - `uses` [INFERRED]
- [[将持仓字典转换为 PositionItem]] - `uses` [INFERRED]
- [[平仓          卖出全部持仓。]] - `uses` [INFERRED]
- [[延迟订单 (T+1 开盘价成交)          用于实现 T 日收盘出信号 → T+1 日开盘价成交的规则]] - `uses` [INFERRED]
- [[成交记录          Attributes         order_id 订单ID         ticker 股票代码]] - `uses` [INFERRED]
- [[执行买卖单                  Args             ticker 股票代码             price 成交价]] - `uses` [INFERRED]
- [[执行所有待成交的延迟订单 (T+1开盘价成交)                  Args             prices T+1日开盘价字典]] - `uses` [INFERRED]
- [[执行调仓                  Args             rebalance_signals 调仓信号 (from get_reb]] - `uses` [INFERRED]
- [[未实现盈亏率 (%) = (盈亏  成本) × 100]] - `uses` [INFERRED]
- [[检查所有持仓是否触发风控                  Returns             需要卖出的标的列表]] - `uses` [INFERRED]
- [[获取 AI 预测排名          返回股票的 AI 评分、方向、置信度等信息。]] - `uses` [INFERRED]
- [[获取 K线数据与 AI 预测          返回：     - 历史 K线数据 (OHLCV)     - AI 预测的未来走势]] - `uses` [INFERRED]
- [[获取历史成交          返回最近的成交记录列表。]] - `uses` [INFERRED]
- [[获取当前 AI 信号          包括：     - 所有股票的 AI 评分排名     - 当前持仓与目标持仓的调仓信号]] - `uses` [INFERRED]
- [[计算调仓信号 (方案C 集合替换逻辑)                  规则         1. 每日维持 Top-N 多头持仓]] - `uses` [INFERRED]
- [[账户统计摘要          包含完整的账户状态快照]] - `uses` [INFERRED]
- [[重置账户          清空所有持仓、成交历史、资金曲线，     恢复到初始资金状态。]] - `uses` [INFERRED]
- [[量化交易核心引擎 (线程安全)          设计原则     - 状态全在实例属性中，由 _lock 保护     - 不持有 HTTP 请求上]] - `uses` [INFERRED]

#graphify/code #graphify/INFERRED #community/Stock_Forecast_API_Predictor