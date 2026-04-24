---
source_file: "d:\transformer\graphify\graphify\security.py"
type: "code"
community: "Graphify Ingest + Security"
location: "L26"
tags:
  - graphify/code
  - graphify/INFERRED
  - community/Graphify_Ingest_+_Security
---

# validate_url()

## Connections
- [[.redirect_request()]] - `calls` [EXTRACTED]
- [[Raise ValueError if url is not http or https, or targets a privateinternal IP]] - `rationale_for` [EXTRACTED]
- [[ingest()]] - `calls` [INFERRED]
- [[safe_fetch()]] - `calls` [EXTRACTED]
- [[security.py]] - `contains` [EXTRACTED]
- [[test_validate_url_accepts_http()]] - `calls` [INFERRED]
- [[test_validate_url_accepts_https()]] - `calls` [INFERRED]
- [[test_validate_url_rejects_data()]] - `calls` [INFERRED]
- [[test_validate_url_rejects_empty_scheme()]] - `calls` [INFERRED]
- [[test_validate_url_rejects_file()]] - `calls` [INFERRED]
- [[test_validate_url_rejects_ftp()]] - `calls` [INFERRED]

#graphify/code #graphify/INFERRED #community/Graphify_Ingest_+_Security