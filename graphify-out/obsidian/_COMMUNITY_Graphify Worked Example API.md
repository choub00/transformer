---
type: community
cohesion: 0.05
members: 72
---

# Graphify Worked Example API

**Cohesion:** 0.05 - loosely connected
**Members:** 72 nodes

## Members
- [[API module - exposes the document pipeline over HTTP. Thin layer over parser, v]] - rationale - d:\transformer\graphify\worked\example\raw\api.py
- [[Accept a list of file paths, run the full pipeline on each,     and return a su]] - rationale - d:\transformer\graphify\worked\example\raw\api.py
- [[Add keyword index and cross-references to a validated document.]] - rationale - d:\transformer\graphify\worked\example\raw\processor.py
- [[Clean up text fields using the processor.]] - rationale - d:\transformer\graphify\worked\example\raw\validator.py
- [[Delete a document by ID.]] - rationale - d:\transformer\graphify\worked\example\raw\api.py
- [[Enrich a validated document and persist it. Returns the record ID.]] - rationale - d:\transformer\graphify\worked\example\raw\processor.py
- [[Extract title, sections, and links from markdown.]] - rationale - d:\transformer\graphify\worked\example\raw\parser.py
- [[Fetch a document by ID and return it.]] - rationale - d:\transformer\graphify\worked\example\raw\api.py
- [[Fetch a single document by ID.]] - rationale - d:\transformer\graphify\worked\example\raw\storage.py
- [[Full pipeline parse, validate, save. Returns the saved record ID.]] - rationale - d:\transformer\graphify\worked\example\raw\parser.py
- [[List all document IDs in storage.]] - rationale - d:\transformer\graphify\worked\example\raw\api.py
- [[Load the full document index from disk.]] - rationale - d:\transformer\graphify\worked\example\raw\storage.py
- [[Look up the index and return IDs of related documents by keyword overlap.]] - rationale - d:\transformer\graphify\worked\example\raw\processor.py
- [[Lowercase, strip extra whitespace, remove control characters.]] - rationale - d:\transformer\graphify\worked\example\raw\processor.py
- [[Parse a JSON document into a structured dict.]] - rationale - d:\transformer\graphify\worked\example\raw\parser.py
- [[Parse a list of files and return their record IDs.]] - rationale - d:\transformer\graphify\worked\example\raw\parser.py
- [[Parser module - reads raw input documents and converts them into a structured f]] - rationale - d:\transformer\graphify\worked\example\raw\parser.py
- [[Persist the index to disk.]] - rationale - d:\transformer\graphify\worked\example\raw\storage.py
- [[Processor module - transforms validated documents into enriched records ready f]] - rationale - d:\transformer\graphify\worked\example\raw\processor.py
- [[Pull non-stopword tokens from text, deduplicated.]] - rationale - d:\transformer\graphify\worked\example\raw\processor.py
- [[Raise if any required field is missing.]] - rationale - d:\transformer\graphify\worked\example\raw\validator.py
- [[Raise if the format is not in the allowed list.]] - rationale - d:\transformer\graphify\worked\example\raw\validator.py
- [[Re-enrich a document to pick up new cross-references.]] - rationale - d:\transformer\graphify\worked\example\raw\api.py
- [[Re-enrich all records in the index. Returns count of records updated.]] - rationale - d:\transformer\graphify\worked\example\raw\processor.py
- [[Read a file from disk and return a structured document.]] - rationale - d:\transformer\graphify\worked\example\raw\parser.py
- [[Remove a document and its index entry. Returns True if it existed.]] - rationale - d:\transformer\graphify\worked\example\raw\storage.py
- [[Return all record IDs currently in storage.]] - rationale - d:\transformer\graphify\worked\example\raw\storage.py
- [[Run all validation checks on a parsed document. Raises ValidationError on failur]] - rationale - d:\transformer\graphify\worked\example\raw\validator.py
- [[Simple keyword search over the index.     Returns documents whose keyword list]] - rationale - d:\transformer\graphify\worked\example\raw\api.py
- [[Split plaintext into paragraphs.]] - rationale - d:\transformer\graphify\worked\example\raw\parser.py
- [[Storage module - persists documents to disk and maintains the search index. All]] - rationale - d:\transformer\graphify\worked\example\raw\storage.py
- [[Validate a list of documents. Returns (valid_docs, errors).]] - rationale - d:\transformer\graphify\worked\example\raw\validator.py
- [[ValidationError]] - code - d:\transformer\graphify\worked\example\raw\validator.py
- [[Validator module - checks that parsed documents meet schema requirements before]] - rationale - d:\transformer\graphify\worked\example\raw\validator.py
- [[Write a parsed document to storage. Returns the assigned record ID.]] - rationale - d:\transformer\graphify\worked\example\raw\storage.py
- [[Write an enriched document to storage, updating the index with keywords.]] - rationale - d:\transformer\graphify\worked\example\raw\storage.py
- [[_ensure_storage()]] - code - d:\transformer\graphify\worked\example\raw\storage.py
- [[api.py]] - code - d:\transformer\graphify\worked\example\raw\api.py
- [[batch_parse()]] - code - d:\transformer\graphify\worked\example\raw\parser.py
- [[check_format()]] - code - d:\transformer\graphify\worked\example\raw\validator.py
- [[check_required_fields()]] - code - d:\transformer\graphify\worked\example\raw\validator.py
- [[delete_record()]] - code - d:\transformer\graphify\worked\example\raw\storage.py
- [[enrich_document()]] - code - d:\transformer\graphify\worked\example\raw\processor.py
- [[extract_keywords()]] - code - d:\transformer\graphify\worked\example\raw\processor.py
- [[find_cross_references()]] - code - d:\transformer\graphify\worked\example\raw\processor.py
- [[handle_delete()]] - code - d:\transformer\graphify\worked\example\raw\api.py
- [[handle_enrich()]] - code - d:\transformer\graphify\worked\example\raw\api.py
- [[handle_get()]] - code - d:\transformer\graphify\worked\example\raw\api.py
- [[handle_list()]] - code - d:\transformer\graphify\worked\example\raw\api.py
- [[handle_search()]] - code - d:\transformer\graphify\worked\example\raw\api.py
- [[handle_upload()]] - code - d:\transformer\graphify\worked\example\raw\api.py
- [[list_records()]] - code - d:\transformer\graphify\worked\example\raw\storage.py
- [[load_index()]] - code - d:\transformer\graphify\worked\example\raw\storage.py
- [[load_record()]] - code - d:\transformer\graphify\worked\example\raw\storage.py
- [[normalize_fields()]] - code - d:\transformer\graphify\worked\example\raw\validator.py
- [[normalize_text()]] - code - d:\transformer\graphify\worked\example\raw\processor.py
- [[parse_and_save()]] - code - d:\transformer\graphify\worked\example\raw\parser.py
- [[parse_file()]] - code - d:\transformer\graphify\worked\example\raw\parser.py
- [[parse_json()]] - code - d:\transformer\graphify\worked\example\raw\parser.py
- [[parse_markdown()]] - code - d:\transformer\graphify\worked\example\raw\parser.py
- [[parse_plaintext()]] - code - d:\transformer\graphify\worked\example\raw\parser.py
- [[parser.py]] - code - d:\transformer\graphify\worked\example\raw\parser.py
- [[process_and_save()]] - code - d:\transformer\graphify\worked\example\raw\processor.py
- [[processor.py]] - code - d:\transformer\graphify\worked\example\raw\processor.py
- [[reprocess_all()]] - code - d:\transformer\graphify\worked\example\raw\processor.py
- [[save_index()]] - code - d:\transformer\graphify\worked\example\raw\storage.py
- [[save_parsed()]] - code - d:\transformer\graphify\worked\example\raw\storage.py
- [[save_processed()]] - code - d:\transformer\graphify\worked\example\raw\storage.py
- [[storage.py]] - code - d:\transformer\graphify\worked\example\raw\storage.py
- [[validate_batch()]] - code - d:\transformer\graphify\worked\example\raw\validator.py
- [[validate_document()]] - code - d:\transformer\graphify\worked\example\raw\validator.py
- [[validator.py]] - code - d:\transformer\graphify\worked\example\raw\validator.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Graphify_Worked_Example_API
SORT file.name ASC
```

## Connections to other communities
- 8 edges to [[_COMMUNITY_Graphify Analyze Module]]
- 7 edges to [[_COMMUNITY_Thesis Debug + Cross-File Analysis]]
- 3 edges to [[_COMMUNITY_Thesis Word Conversion + Frontend API]]
- 1 edge to [[_COMMUNITY_HTTPX Auth + Client]]
- 1 edge to [[_COMMUNITY_Sample Fixtures + Serve]]
- 1 edge to [[_COMMUNITY_Thesis Doc Analysis Scripts]]

## Top bridge nodes
- [[find_cross_references()]] - degree 7, connects to 3 communities
- [[handle_search()]] - degree 6, connects to 3 communities
- [[save_parsed()]] - degree 8, connects to 2 communities
- [[save_processed()]] - degree 8, connects to 2 communities
- [[extract_keywords()]] - degree 6, connects to 2 communities