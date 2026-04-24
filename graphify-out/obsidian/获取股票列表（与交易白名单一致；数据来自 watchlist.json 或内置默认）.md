---
source_file: "d:\transformer\api\dashboard.py"
type: "rationale"
community: "Trading Account Manager + Auto"
location: "L243"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Trading_Account_Manager_+_Auto
---

# 获取股票列表（与交易白名单一致；数据来自 watchlist.json 或内置默认）

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
- [[get_tickers()]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/INFERRED #community/Trading_Account_Manager_+_Auto