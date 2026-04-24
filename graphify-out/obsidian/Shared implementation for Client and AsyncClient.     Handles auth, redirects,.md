---
source_file: "d:\transformer\graphify\worked\httpx\raw\client.py"
type: "rationale"
community: "HTTPX Auth + Client"
location: "L32"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/HTTPX_Auth_+_Client
---

# Shared implementation for Client and AsyncClient.     Handles auth, redirects,

## Connections
- [[AsyncHTTPTransport]] - `uses` [INFERRED]
- [[Auth]] - `uses` [INFERRED]
- [[BaseClient]] - `rationale_for` [EXTRACTED]
- [[BaseTransport]] - `uses` [INFERRED]
- [[BasicAuth]] - `uses` [INFERRED]
- [[Cookies]] - `uses` [INFERRED]
- [[HTTPTransport]] - `uses` [INFERRED]
- [[Headers]] - `uses` [INFERRED]
- [[InvalidURL]] - `uses` [INFERRED]
- [[Request]] - `uses` [INFERRED]
- [[Response]] - `uses` [INFERRED]
- [[TooManyRedirects]] - `uses` [INFERRED]
- [[URL]] - `uses` [INFERRED]

#graphify/rationale #graphify/INFERRED #community/HTTPX_Auth_+_Client