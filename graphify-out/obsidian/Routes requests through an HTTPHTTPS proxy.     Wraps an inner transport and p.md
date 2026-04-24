---
source_file: "d:\transformer\graphify\worked\httpx\raw\transport.py"
type: "rationale"
community: "HTTPX Auth + Client"
location: "L117"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/HTTPX_Auth_+_Client
---

# Routes requests through an HTTP/HTTPS proxy.     Wraps an inner transport and p

## Connections
- [[ConnectError]] - `uses` [INFERRED]
- [[ProxyTransport]] - `rationale_for` [EXTRACTED]
- [[Request]] - `uses` [INFERRED]
- [[Response]] - `uses` [INFERRED]
- [[TimeoutException]] - `uses` [INFERRED]
- [[TransportError]] - `uses` [INFERRED]

#graphify/rationale #graphify/INFERRED #community/HTTPX_Auth_+_Client