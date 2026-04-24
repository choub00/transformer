---
source_file: "d:\transformer\api\dashboard.py"
type: "rationale"
community: "Trading Account Manager + Auto"
location: "L165"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Trading_Account_Manager_+_Auto
---

# 获取指定股票的历史 K 线 + Alpha-Transformer-Next 未来5天预测。      返回两组对齐序列：     - history: 最近

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
- [[get_forecast()]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/INFERRED #community/Trading_Account_Manager_+_Auto