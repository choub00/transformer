---
source_file: "d:\transformer\graphify\worked\httpx\raw\transport.py"
type: "rationale"
community: "HTTPX Auth + Client"
location: "L90"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/HTTPX_Auth_+_Client
---

# The async variant of HTTPTransport.

## Connections
- [[AsyncHTTPTransport]] - `rationale_for` [EXTRACTED]
- [[ConnectError]] - `uses` [INFERRED]
- [[Request]] - `uses` [INFERRED]
- [[Response]] - `uses` [INFERRED]
- [[TimeoutException]] - `uses` [INFERRED]
- [[TransportError]] - `uses` [INFERRED]

#graphify/rationale #graphify/INFERRED #community/HTTPX_Auth_+_Client