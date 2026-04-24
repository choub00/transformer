---
source_file: "d:\transformer\graphify\worked\httpx\raw\transport.py"
type: "rationale"
community: "HTTPX Auth + Client"
location: "L31"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/HTTPX_Auth_+_Client
---

# Manages a pool of persistent HTTP connections.     Keys connections by (scheme,

## Connections
- [[ConnectError]] - `uses` [INFERRED]
- [[ConnectionPool]] - `rationale_for` [EXTRACTED]
- [[Request]] - `uses` [INFERRED]
- [[Response]] - `uses` [INFERRED]
- [[TimeoutException]] - `uses` [INFERRED]
- [[TransportError]] - `uses` [INFERRED]

#graphify/rationale #graphify/INFERRED #community/HTTPX_Auth_+_Client