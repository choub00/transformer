---
source_file: "d:\transformer\api\dashboard.py"
type: "rationale"
community: "Trading Account Manager + Auto"
location: "L308"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Trading_Account_Manager_+_Auto
---

# 获取实时 K 线数据（优先 Alpha Vantage，降级到模拟数据）      参数:     - ticker: 股票代码（如 AAPL, MSFT）

## Connections
- [[AccountBalance]] - `uses` [INFERRED]
- [[DashboardFull]] - `uses` [INFERRED]
- [[DashboardMetrics]] - `uses` [INFERRED]
- [[EquityCurve]] - `uses` [INFERRED]
- [[FeatureImportance]] - `uses` [INFERRED]
- [[FeatureImportanceResponse]] - `uses` [INFERRED]
- [[ForecastPoint]] - `uses` [INFERRED]
- [[ForecastResponse]] - `uses` [INFERRED]
- [[KLinePoint]] - `uses` [INFERRED]
- [[KLineResponse]] - `uses` [INFERRED]
- [[PredictionsResponse]] - `uses` [INFERRED]
- [[StockPrediction]] - `uses` [INFERRED]
- [[get_realtime_kline()]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/INFERRED #community/Trading_Account_Manager_+_Auto