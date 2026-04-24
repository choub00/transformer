---
source_file: "d:\transformer\api\server.py"
type: "rationale"
community: "Trading Account Manager + Auto"
location: "L60"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Trading_Account_Manager_+_Auto
---

# 全局异常捕获：     - 所有未处理的异常返回 200 + error JSON（不崩溃）     - 只有 Pydantic 校验错误返回 422

## Connections
- [[ErrorResponse]] - `uses` [INFERRED]
- [[HealthResponse]] - `uses` [INFERRED]
- [[global_exception_handler()]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/INFERRED #community/Trading_Account_Manager_+_Auto