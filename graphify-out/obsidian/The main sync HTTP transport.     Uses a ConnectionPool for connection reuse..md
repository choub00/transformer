---
source_file: "d:\transformer\graphify\worked\httpx\raw\transport.py"
type: "rationale"
community: "HTTPX Auth + Client"
location: "L60"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/HTTPX_Auth_+_Client
---

# The main sync HTTP transport.     Uses a ConnectionPool for connection reuse.

## Connections
- [[ConnectError]] - `uses` [INFERRED]
- [[HTTPTransport]] - `rationale_for` [EXTRACTED]
- [[Request]] - `uses` [INFERRED]
- [[Response]] - `uses` [INFERRED]
- [[TimeoutException]] - `uses` [INFERRED]
- [[TransportError]] - `uses` [INFERRED]

#graphify/rationale #graphify/INFERRED #community/HTTPX_Auth_+_Client