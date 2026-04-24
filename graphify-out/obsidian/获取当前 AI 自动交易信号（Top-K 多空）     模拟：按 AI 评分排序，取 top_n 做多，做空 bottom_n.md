---
source_file: "d:\transformer\api\auto.py"
type: "rationale"
community: "Trading Account Manager + Auto"
location: "L63"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Trading_Account_Manager_+_Auto
---

# 获取当前 AI 自动交易信号（Top-K 多空）     模拟：按 AI 评分排序，取 top_n 做多，做空 bottom_n

## Connections
- [[AISignal]] - `uses` [INFERRED]
- [[AutoTradeStatus]] - `uses` [INFERRED]
- [[get_auto_signals()]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/INFERRED #community/Trading_Account_Manager_+_Auto