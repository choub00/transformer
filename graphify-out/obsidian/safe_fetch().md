---
source_file: "d:\transformer\graphify\graphify\security.py"
type: "code"
community: "Graphify Ingest + Security"
location: "L87"
tags:
  - graphify/code
  - graphify/INFERRED
  - community/Graphify_Ingest_+_Security
---

# safe_fetch()

## Connections
- [[.read()]] - `calls` [INFERRED]
- [[Fetch url and return raw bytes.      Protections applied     - URL scheme]] - `rationale_for` [EXTRACTED]
- [[HTTPError]] - `calls` [INFERRED]
- [[Request]] - `calls` [INFERRED]
- [[_build_opener()]] - `calls` [EXTRACTED]
- [[_download_binary()]] - `calls` [INFERRED]
- [[safe_fetch_text()]] - `calls` [EXTRACTED]
- [[security.py]] - `contains` [EXTRACTED]
- [[test_safe_fetch_raises_on_non_2xx()]] - `calls` [INFERRED]
- [[test_safe_fetch_raises_on_size_exceeded()]] - `calls` [INFERRED]
- [[test_safe_fetch_rejects_file_url()]] - `calls` [INFERRED]
- [[test_safe_fetch_rejects_ftp_url()]] - `calls` [INFERRED]
- [[test_safe_fetch_returns_bytes()]] - `calls` [INFERRED]
- [[validate_url()]] - `calls` [EXTRACTED]

#graphify/code #graphify/INFERRED #community/Graphify_Ingest_+_Security