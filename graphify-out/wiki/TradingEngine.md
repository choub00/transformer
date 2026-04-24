# TradingEngine

> God node · 62 connections · `d:\transformer\Stock Forecast\api\trading_engine.py`

## Connections by Relation

### contains
- [[trading_engine.py]] `EXTRACTED`

### method
- [[._auto_scan()]] `EXTRACTED`
- [[.get_mock_price()]] `EXTRACTED`
- [[._append_auto_log()]] `EXTRACTED`
- [[.execute_delayed_orders()]] `EXTRACTED`
- [[.place_order()]] `EXTRACTED`
- [[.get_stats()]] `EXTRACTED`
- [[.execute_rebalance()]] `EXTRACTED`
- [[._execute_trade()]] `EXTRACTED`
- [[.get_rebalance_signals()]] `EXTRACTED`
- [[.get_ai_signals()]] `EXTRACTED`
- [[.place_delayed_order()]] `EXTRACTED`
- [[.reset()]] `EXTRACTED`
- [[.update_price()]] `EXTRACTED`
- [[.close_all_positions()]] `EXTRACTED`
- [[.check_risk_controls()]] `EXTRACTED`
- [[.start_auto_trading()]] `EXTRACTED`
- [[._auto_trading_loop()]] `EXTRACTED`
- [[.configure()]] `EXTRACTED`
- [[.get_position()]] `EXTRACTED`
- [[.get_all_positions()]] `EXTRACTED`

### rationale_for
- [[量化交易核心引擎 (线程安全)          设计原则:     - 状态全在实例属性中，由 _lock 保护     - 不持有 HTTP 请求上]] `EXTRACTED`

### uses
- [[AlphaPredictor]] `INFERRED`
- [[OrderResponse]] `INFERRED`
- [[KLineResponse]] `INFERRED`
- [[PredictionsResponse]] `INFERRED`
- [[HealthResponse]] `INFERRED`
- [[PositionItem]] `INFERRED`
- [[AccountResponse]] `INFERRED`
- [[ConfigResponse]] `INFERRED`
- [[DelayedOrderResponse]] `INFERRED`
- [[TradeHistoryItem]] `INFERRED`
- [[TradeHistoryResponse]] `INFERRED`
- [[PredictionItem]] `INFERRED`
- [[AutoStatusResponse]] `INFERRED`
- [[AutoLogsResponse]] `INFERRED`
- [[AIAdviceResponse]] `INFERRED`
- [[MetricsResponse]] `INFERRED`
- [[ConfigRequest]] `INFERRED`
- [[OrderRequest]] `INFERRED`
- [[DelayedOrderRequest]] `INFERRED`
- [[AutoStartRequest]] `INFERRED`

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*