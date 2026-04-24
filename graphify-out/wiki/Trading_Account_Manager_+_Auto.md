# Trading Account Manager + Auto

> 94 nodes · cohesion 0.06

## Key Concepts

- **BaseModel** (44 connections)
- **schemas.py** (26 connections) — `d:\transformer\api\schemas.py`
- **dashboard.py** (13 connections) — `d:\transformer\api\dashboard.py`
- **Dashboard API 路由 — 健壮版 所有错误被捕获并转换为中文友好的结构化响应。** (13 connections) — `d:\transformer\api\dashboard.py`
- **获取指定股票的历史 K 线 + Alpha-Transformer-Next 未来5天预测。      返回两组对齐序列：     - history: 最近** (13 connections) — `d:\transformer\api\dashboard.py`
- **获取股票列表（与交易白名单一致；数据来自 watchlist.json 或内置默认）** (13 connections) — `d:\transformer\api\dashboard.py`
- **从 Alpha Vantage 获取 K 线数据     返回格式化的 K 线数据字典，或在失败时返回 None** (13 connections) — `d:\transformer\api\dashboard.py`
- **获取实时 K 线数据（优先 Alpha Vantage，降级到模拟数据）      参数:     - ticker: 股票代码（如 AAPL, MSFT）** (13 connections) — `d:\transformer\api\dashboard.py`
- **AccountManager** (10 connections) — `d:\transformer\api\account_manager.py`
- **get_reasonable_price()** (10 connections) — `d:\transformer\api\account_manager.py`
- **.execute_order()** (9 connections) — `d:\transformer\api\account_manager.py`
- **get_account_manager()** (9 connections) — `d:\transformer\api\account_manager.py`
- **ForecastResponse** (9 connections) — `d:\transformer\api\schemas.py`
- **KLinePoint** (9 connections) — `d:\transformer\api\schemas.py`
- **place_order()** (9 connections) — `d:\transformer\api\trading.py`
- **account_manager.py** (8 connections) — `d:\transformer\api\account_manager.py`
- **_generate_predictions()** (8 connections) — `d:\transformer\api\dashboard.py`
- **get_dashboard_full()** (8 connections) — `d:\transformer\api\dashboard.py`
- **get_forecast()** (8 connections) — `d:\transformer\api\dashboard.py`
- **AutoTradeStatus** (8 connections) — `d:\transformer\api\schemas.py`
- **DashboardFull** (8 connections) — `d:\transformer\api\schemas.py`
- **DashboardMetrics** (8 connections) — `d:\transformer\api\schemas.py`
- **EquityCurve** (8 connections) — `d:\transformer\api\schemas.py`
- **FeatureImportanceResponse** (8 connections) — `d:\transformer\api\schemas.py`
- **ForecastPoint** (8 connections) — `d:\transformer\api\schemas.py`
- *... and 69 more nodes in this community*

## Relationships

- No strong cross-community connections detected

## Source Files

- `d:\transformer\Stock Forecast\api\server.py`
- `d:\transformer\api\account.py`
- `d:\transformer\api\account_manager.py`
- `d:\transformer\api\auto.py`
- `d:\transformer\api\dashboard.py`
- `d:\transformer\api\schemas.py`
- `d:\transformer\api\server.py`
- `d:\transformer\api\tickers_registry.py`
- `d:\transformer\api\trading.py`

## Audit Trail

- EXTRACTED: 277 (50%)
- INFERRED: 280 (50%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*