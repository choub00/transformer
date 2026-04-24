---
type: community
cohesion: 0.03
members: 117
---

# Graphify Ingest + Security

**Cohesion:** 0.03 - loosely connected
**Members:** 117 nodes

## Members
- [[.patch()_1]] - code - d:\transformer\graphify\worked\httpx\raw\client.py
- [[.redirect_request()]] - code - d:\transformer\graphify\graphify\security.py
- [[Build a domain hint for Whisper from god nodes extracted from the corpus.]] - rationale - d:\transformer\graphify\graphify\transcribe.py
- [[Classify the URL for targeted extraction.]] - rationale - d:\transformer\graphify\graphify\ingest.py
- [[Convert HTML to clean markdown. Uses html2text if available, else basic strip.]] - rationale - d:\transformer\graphify\graphify\ingest.py
- [[Download a binary file (PDF, image) directly.]] - rationale - d:\transformer\graphify\graphify\ingest.py
- [[Download audio-only stream from a URL using yt-dlp.      Returns the path to t]] - rationale - d:\transformer\graphify\graphify\transcribe.py
- [[Empty god_nodes returns fallback prompt.]] - rationale - d:\transformer\graphify\tests\test_transcribe.py
- [[Empty input returns empty list without error.]] - rationale - d:\transformer\graphify\tests\test_transcribe.py
- [[Escape a string for embedding in a YAML double-quoted scalar.]] - rationale - d:\transformer\graphify\graphify\ingest.py
- [[Fetch url and return decoded text (UTF-8, replacing bad bytes).      Wraps s]] - rationale - d:\transformer\graphify\graphify\security.py
- [[Fetch url and return raw bytes.      Protections applied     - URL scheme]] - rationale - d:\transformer\graphify\graphify\security.py
- [[Fetch a URL and save it into target_dir as a graphify-ready file.      Returns]] - rationale - d:\transformer\graphify\graphify\ingest.py
- [[Fetch a generic webpage and convert to markdown.]] - rationale - d:\transformer\graphify\graphify\ingest.py
- [[Fetch a tweet URL. Returns (content, filename).]] - rationale - d:\transformer\graphify\graphify\ingest.py
- [[Fetch arXiv abstract page.]] - rationale - d:\transformer\graphify\graphify\ingest.py
- [[GRAPHIFY_WHISPER_PROMPT env var short-circuits LLM call.]] - rationale - d:\transformer\graphify\tests\test_transcribe.py
- [[Graphify Security Module]] - code - d:\transformer\graphify\ARCHITECTURE.md
- [[If transcript already exists, transcribe() returns cached path without running W]] - rationale - d:\transformer\graphify\tests\test_transcribe.py
- [[ImportError propagates when faster_whisper is not installed.]] - rationale - d:\transformer\graphify\tests\test_transcribe.py
- [[Label Sanitization]] - code - d:\transformer\graphify\SECURITY.md
- [[Nodes missing 'label' keys are safely skipped.]] - rationale - d:\transformer\graphify\tests\test_transcribe.py
- [[Path Traversal Guard]] - code - d:\transformer\graphify\SECURITY.md
- [[Raise ValueError if url is not http or https, or targets a privateinternal IP]] - rationale - d:\transformer\graphify\graphify\security.py
- [[Redirect handler that re-validates every redirect target.      Prevents open-r]] - rationale - d:\transformer\graphify\graphify\security.py
- [[Resolve path and verify it stays inside base.      base defaults to the]] - rationale - d:\transformer\graphify\graphify\security.py
- [[Return True if the string looks like a URL rather than a file path.]] - rationale - d:\transformer\graphify\graphify\transcribe.py
- [[Returns a topic-based prompt from god node labels — no LLM call.]] - rationale - d:\transformer\graphify\tests\test_transcribe.py
- [[SSRF Mitigation]] - code - d:\transformer\graphify\SECURITY.md
- [[Safe URL Fetch with Size Cap]] - code - d:\transformer\graphify\SECURITY.md
- [[Save a Q&A result as markdown so it gets extracted into the graph on next --upda]] - rationale - d:\transformer\graphify\graphify\ingest.py
- [[Strip control characters and cap length.      Safe for embedding in JSON data]] - rationale - d:\transformer\graphify\graphify\security.py
- [[Tests for graphify.ingest.save_query_result]] - rationale - d:\transformer\graphify\tests\test_ingest.py
- [[Tests for graphify.transcribe — videoaudio transcription support.]] - rationale - d:\transformer\graphify\tests\test_transcribe.py
- [[Tests for graphifysecurity.py - URL validation, safe fetch, path guards, label]] - rationale - d:\transformer\graphify\tests\test_security.py
- [[Transcribe a list of videoaudio files or URLs, return paths to transcript .txt]] - rationale - d:\transformer\graphify\graphify\transcribe.py
- [[Transcribe a videoaudio file or URL to a .txt transcript.      If video_path]] - rationale - d:\transformer\graphify\graphify\transcribe.py
- [[Turn a URL into a safe filename.]] - rationale - d:\transformer\graphify\graphify\ingest.py
- [[URL Validation (HTTPHTTPS Only)]] - code - d:\transformer\graphify\SECURITY.md
- [[XSS Prevention in HTML Output]] - code - d:\transformer\graphify\SECURITY.md
- [[YAML Frontmatter Injection Prevention]] - code - d:\transformer\graphify\SECURITY.md
- [[_NoFileRedirectHandler]] - code - d:\transformer\graphify\graphify\security.py
- [[_build_opener()]] - code - d:\transformer\graphify\graphify\security.py
- [[_detect_url_type()]] - code - d:\transformer\graphify\graphify\ingest.py
- [[_download_binary()]] - code - d:\transformer\graphify\graphify\ingest.py
- [[_fetch_arxiv()]] - code - d:\transformer\graphify\graphify\ingest.py
- [[_fetch_html()]] - code - d:\transformer\graphify\graphify\ingest.py
- [[_fetch_tweet()]] - code - d:\transformer\graphify\graphify\ingest.py
- [[_fetch_webpage()]] - code - d:\transformer\graphify\graphify\ingest.py
- [[_get_whisper()]] - code - d:\transformer\graphify\graphify\transcribe.py
- [[_get_yt_dlp()]] - code - d:\transformer\graphify\graphify\transcribe.py
- [[_html_to_markdown()]] - code - d:\transformer\graphify\graphify\ingest.py
- [[_make_mock_response()]] - code - d:\transformer\graphify\tests\test_security.py
- [[_model_name()]] - code - d:\transformer\graphify\graphify\transcribe.py
- [[_safe_filename()]] - code - d:\transformer\graphify\graphify\ingest.py
- [[_yaml_str()]] - code - d:\transformer\graphify\graphify\ingest.py
- [[build_whisper_prompt()]] - code - d:\transformer\graphify\graphify\transcribe.py
- [[download_audio()]] - code - d:\transformer\graphify\graphify\transcribe.py
- [[force=True re-transcribes even when cache exists.]] - rationale - d:\transformer\graphify\tests\test_transcribe.py
- [[ingest()]] - code - d:\transformer\graphify\graphify\ingest.py
- [[ingest.py]] - code - d:\transformer\graphify\graphify\ingest.py
- [[is_url()]] - code - d:\transformer\graphify\graphify\transcribe.py
- [[safe_fetch()]] - code - d:\transformer\graphify\graphify\security.py
- [[safe_fetch_text()]] - code - d:\transformer\graphify\graphify\security.py
- [[sanitize_label()]] - code - d:\transformer\graphify\graphify\security.py
- [[save_query_result()]] - code - d:\transformer\graphify\graphify\ingest.py
- [[security.py]] - code - d:\transformer\graphify\graphify\security.py
- [[test_answer_in_body()]] - code - d:\transformer\graphify\tests\test_ingest.py
- [[test_build_whisper_prompt_env_override()]] - code - d:\transformer\graphify\tests\test_transcribe.py
- [[test_build_whisper_prompt_no_nodes()]] - code - d:\transformer\graphify\tests\test_transcribe.py
- [[test_build_whisper_prompt_nodes_without_labels()]] - code - d:\transformer\graphify\tests\test_transcribe.py
- [[test_build_whisper_prompt_returns_topic_string()]] - code - d:\transformer\graphify\tests\test_transcribe.py
- [[test_file_created()]] - code - d:\transformer\graphify\tests\test_ingest.py
- [[test_filename_format()]] - code - d:\transformer\graphify\tests\test_ingest.py
- [[test_frontmatter_question()]] - code - d:\transformer\graphify\tests\test_ingest.py
- [[test_frontmatter_type()]] - code - d:\transformer\graphify\tests\test_ingest.py
- [[test_ingest.py]] - code - d:\transformer\graphify\tests\test_ingest.py
- [[test_memory_dir_created()]] - code - d:\transformer\graphify\tests\test_ingest.py
- [[test_safe_fetch_raises_on_non_2xx()]] - code - d:\transformer\graphify\tests\test_security.py
- [[test_safe_fetch_raises_on_size_exceeded()]] - code - d:\transformer\graphify\tests\test_security.py
- [[test_safe_fetch_rejects_file_url()]] - code - d:\transformer\graphify\tests\test_security.py
- [[test_safe_fetch_rejects_ftp_url()]] - code - d:\transformer\graphify\tests\test_security.py
- [[test_safe_fetch_returns_bytes()]] - code - d:\transformer\graphify\tests\test_security.py
- [[test_safe_fetch_text_decodes_utf8()]] - code - d:\transformer\graphify\tests\test_security.py
- [[test_safe_fetch_text_replaces_bad_bytes()]] - code - d:\transformer\graphify\tests\test_security.py
- [[test_sanitize_label_caps_at_256()]] - code - d:\transformer\graphify\tests\test_security.py
- [[test_sanitize_label_passthrough_html_chars()]] - code - d:\transformer\graphify\tests\test_security.py
- [[test_sanitize_label_safe_passthrough()]] - code - d:\transformer\graphify\tests\test_security.py
- [[test_sanitize_label_strips_control_chars()]] - code - d:\transformer\graphify\tests\test_security.py
- [[test_security.py]] - code - d:\transformer\graphify\tests\test_security.py
- [[test_source_nodes_capped_at_10()]] - code - d:\transformer\graphify\tests\test_ingest.py
- [[test_source_nodes_included()]] - code - d:\transformer\graphify\tests\test_ingest.py
- [[test_transcribe.py]] - code - d:\transformer\graphify\tests\test_transcribe.py
- [[test_transcribe_all_empty()]] - code - d:\transformer\graphify\tests\test_transcribe.py
- [[test_transcribe_all_skips_failed()]] - code - d:\transformer\graphify\tests\test_transcribe.py
- [[test_transcribe_all_uses_cache()]] - code - d:\transformer\graphify\tests\test_transcribe.py
- [[test_transcribe_force_reruns()]] - code - d:\transformer\graphify\tests\test_transcribe.py
- [[test_transcribe_missing_faster_whisper()]] - code - d:\transformer\graphify\tests\test_transcribe.py
- [[test_transcribe_uses_cache()]] - code - d:\transformer\graphify\tests\test_transcribe.py
- [[test_validate_graph_path_allows_inside_base()]] - code - d:\transformer\graphify\tests\test_security.py
- [[test_validate_graph_path_blocks_traversal()]] - code - d:\transformer\graphify\tests\test_security.py
- [[test_validate_graph_path_raises_if_file_missing()]] - code - d:\transformer\graphify\tests\test_security.py
- [[test_validate_graph_path_requires_base_exists()]] - code - d:\transformer\graphify\tests\test_security.py
- [[test_validate_url_accepts_http()]] - code - d:\transformer\graphify\tests\test_security.py
- [[test_validate_url_accepts_https()]] - code - d:\transformer\graphify\tests\test_security.py
- [[test_validate_url_rejects_data()]] - code - d:\transformer\graphify\tests\test_security.py
- [[test_validate_url_rejects_empty_scheme()]] - code - d:\transformer\graphify\tests\test_security.py
- [[test_validate_url_rejects_file()]] - code - d:\transformer\graphify\tests\test_security.py
- [[test_validate_url_rejects_ftp()]] - code - d:\transformer\graphify\tests\test_security.py
- [[test_video_extensions_set()]] - code - d:\transformer\graphify\tests\test_transcribe.py
- [[transcribe()]] - code - d:\transformer\graphify\graphify\transcribe.py
- [[transcribe.py]] - code - d:\transformer\graphify\graphify\transcribe.py
- [[transcribe_all()]] - code - d:\transformer\graphify\graphify\transcribe.py
- [[transcribe_all() returns cached paths for already-transcribed files.]] - rationale - d:\transformer\graphify\tests\test_transcribe.py
- [[transcribe_all() warns and skips files that fail to transcribe.]] - rationale - d:\transformer\graphify\tests\test_transcribe.py
- [[validate_graph_path()]] - code - d:\transformer\graphify\graphify\security.py
- [[validate_url()]] - code - d:\transformer\graphify\graphify\security.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Graphify_Ingest_+_Security
SORT file.name ASC
```

## Connections to other communities
- 12 edges to [[_COMMUNITY_Graphify Analyze Module]]
- 4 edges to [[_COMMUNITY_Thesis Debug + Cross-File Analysis]]
- 4 edges to [[_COMMUNITY_HTTPX Auth + Client]]
- 2 edges to [[_COMMUNITY_Sample Fixtures + Serve]]
- 1 edge to [[_COMMUNITY_Thesis Doc Analysis Scripts]]
- 1 edge to [[_COMMUNITY_Graphify Hooks + Agents CLI]]

## Top bridge nodes
- [[.patch()_1]] - degree 12, connects to 3 communities
- [[safe_fetch()]] - degree 14, connects to 2 communities
- [[Graphify Security Module]] - degree 11, connects to 2 communities
- [[sanitize_label()]] - degree 8, connects to 2 communities
- [[download_audio()]] - degree 7, connects to 2 communities