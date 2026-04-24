---
source_file: "d:\transformer\graphify\worked\httpx\raw\client.py"
type: "rationale"
community: "HTTPX Auth + Client"
location: "L1"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/HTTPX_Auth_+_Client
---

# The main Client and AsyncClient classes. BaseClient holds all shared logic. Cli

## Connections
- [[AsyncHTTPTransport]] - `uses` [INFERRED]
- [[Auth]] - `uses` [INFERRED]
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
- [[client.py]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/INFERRED #community/HTTPX_Auth_+_Client