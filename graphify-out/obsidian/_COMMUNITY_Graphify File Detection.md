---
type: community
cohesion: 0.05
members: 69
---

# Graphify File Detection

**Cohesion:** 0.05 - loosely connected
**Members:** 69 nodes

## Members
- [[A .graphifyignore at the git repo root is included when scanning a subdir.]] - rationale - d:\transformer\graphify\tests\test_detect.py
- [[A .graphifyignore in a parent directory applies to subdirectory scans.]] - rationale - d:\transformer\graphify\tests\test_detect.py
- [[A .md file with enough paper signals should classify as PAPER.]] - rationale - d:\transformer\graphify\tests\test_detect.py
- [[A plain .md file without paper signals should stay DOCUMENT.]] - rationale - d:\transformer\graphify\tests\test_detect.py
- [[Comment lines in .graphifyignore are not treated as patterns.]] - rationale - d:\transformer\graphify\tests\test_detect.py
- [[Convert a .docx file to markdown text using python-docx.]] - rationale - d:\transformer\graphify\graphify\detect.py
- [[Convert a .docx or .xlsx to a markdown sidecar in out_dir.      Returns the pa]] - rationale - d:\transformer\graphify\graphify\detect.py
- [[Convert an .xlsx file to markdown text using openpyxl.]] - rationale - d:\transformer\graphify\graphify\detect.py
- [[Extract plain text from a PDF file using pypdf.]] - rationale - d:\transformer\graphify\graphify\detect.py
- [[FileType]] - code - d:\transformer\graphify\graphify\detect.py
- [[Files matching .graphifyignore patterns are excluded from detect().]] - rationale - d:\transformer\graphify\tests\test_detect.py
- [[Heuristic does this text file read like an academic paper]] - rationale - d:\transformer\graphify\graphify\detect.py
- [[Like detect(), but returns only new or modified files since the last run.]] - rationale - d:\transformer\graphify\graphify\detect.py
- [[Load the file modification time manifest from a previous run.]] - rationale - d:\transformer\graphify\graphify\detect.py
- [[No .graphifyignore is not an error.]] - rationale - d:\transformer\graphify\tests\test_detect.py
- [[Return True if path matches any .graphifyignore pattern.]] - rationale - d:\transformer\graphify\graphify\detect.py
- [[Return True if this directory name looks like a venv, cache, or dep dir.]] - rationale - d:\transformer\graphify\graphify\detect.py
- [[Return True if this file likely contains secrets and should be skipped.]] - rationale - d:\transformer\graphify\graphify\detect.py
- [[Save current file mtimes so the next --update run can diff against them.]] - rationale - d:\transformer\graphify\graphify\detect.py
- [[The real attention paper file should be classified as PAPER.]] - rationale - d:\transformer\graphify\tests\test_detect.py
- [[Upward search stops at the git repo root (.git directory).]] - rationale - d:\transformer\graphify\tests\test_detect.py
- [[Video and audio file extensions should classify as VIDEO.]] - rationale - d:\transformer\graphify\tests\test_detect.py
- [[Video files do not contribute to total_words.]] - rationale - d:\transformer\graphify\tests\test_detect.py
- [[_is_ignored()]] - code - d:\transformer\graphify\graphify\detect.py
- [[_is_noise_dir()]] - code - d:\transformer\graphify\graphify\detect.py
- [[_is_sensitive()]] - code - d:\transformer\graphify\graphify\detect.py
- [[_looks_like_paper()]] - code - d:\transformer\graphify\graphify\detect.py
- [[classify_file()]] - code - d:\transformer\graphify\graphify\detect.py
- [[convert_office_file()]] - code - d:\transformer\graphify\graphify\detect.py
- [[count_words()]] - code - d:\transformer\graphify\graphify\detect.py
- [[detect()]] - code - d:\transformer\graphify\graphify\detect.py
- [[detect() correctly counts video files and does not add them to word count.]] - rationale - d:\transformer\graphify\tests\test_detect.py
- [[detect() result always includes a 'video' key even with no video files.]] - rationale - d:\transformer\graphify\tests\test_detect.py
- [[detect.py]] - code - d:\transformer\graphify\graphify\detect.py
- [[detect_incremental()]] - code - d:\transformer\graphify\graphify\detect.py
- [[docx_to_markdown()]] - code - d:\transformer\graphify\graphify\detect.py
- [[extract_pdf_text()]] - code - d:\transformer\graphify\graphify\detect.py
- [[load_manifest()]] - code - d:\transformer\graphify\graphify\detect.py
- [[save_manifest()]] - code - d:\transformer\graphify\graphify\detect.py
- [[test_classify_attention_paper()]] - code - d:\transformer\graphify\tests\test_detect.py
- [[test_classify_image()]] - code - d:\transformer\graphify\tests\test_detect.py
- [[test_classify_markdown()]] - code - d:\transformer\graphify\tests\test_detect.py
- [[test_classify_md_doc_without_signals()]] - code - d:\transformer\graphify\tests\test_detect.py
- [[test_classify_md_paper_by_signals()]] - code - d:\transformer\graphify\tests\test_detect.py
- [[test_classify_pdf()]] - code - d:\transformer\graphify\tests\test_detect.py
- [[test_classify_pdf_in_xcassets_root_skipped()]] - code - d:\transformer\graphify\tests\test_detect.py
- [[test_classify_pdf_in_xcassets_skipped()]] - code - d:\transformer\graphify\tests\test_detect.py
- [[test_classify_python()]] - code - d:\transformer\graphify\tests\test_detect.py
- [[test_classify_typescript()]] - code - d:\transformer\graphify\tests\test_detect.py
- [[test_classify_unknown_returns_none()]] - code - d:\transformer\graphify\tests\test_detect.py
- [[test_classify_video_extensions()]] - code - d:\transformer\graphify\tests\test_detect.py
- [[test_count_words_sample_md()]] - code - d:\transformer\graphify\tests\test_detect.py
- [[test_detect.py]] - code - d:\transformer\graphify\tests\test_detect.py
- [[test_detect_finds_fixtures()]] - code - d:\transformer\graphify\tests\test_detect.py
- [[test_detect_finds_video_files()]] - code - d:\transformer\graphify\tests\test_detect.py
- [[test_detect_follows_symlinked_directory()]] - code - d:\transformer\graphify\tests\test_detect.py
- [[test_detect_follows_symlinked_file()]] - code - d:\transformer\graphify\tests\test_detect.py
- [[test_detect_handles_circular_symlinks()]] - code - d:\transformer\graphify\tests\test_detect.py
- [[test_detect_includes_video_key()]] - code - d:\transformer\graphify\tests\test_detect.py
- [[test_detect_skips_dotfiles()]] - code - d:\transformer\graphify\tests\test_detect.py
- [[test_detect_video_not_in_words()]] - code - d:\transformer\graphify\tests\test_detect.py
- [[test_detect_warns_small_corpus()]] - code - d:\transformer\graphify\tests\test_detect.py
- [[test_graphifyignore_at_git_root_is_included()]] - code - d:\transformer\graphify\tests\test_detect.py
- [[test_graphifyignore_comments_ignored()]] - code - d:\transformer\graphify\tests\test_detect.py
- [[test_graphifyignore_discovered_from_parent()]] - code - d:\transformer\graphify\tests\test_detect.py
- [[test_graphifyignore_excludes_file()]] - code - d:\transformer\graphify\tests\test_detect.py
- [[test_graphifyignore_missing_is_fine()]] - code - d:\transformer\graphify\tests\test_detect.py
- [[test_graphifyignore_stops_at_git_boundary()]] - code - d:\transformer\graphify\tests\test_detect.py
- [[xlsx_to_markdown()]] - code - d:\transformer\graphify\graphify\detect.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Graphify_File_Detection
SORT file.name ASC
```

## Connections to other communities
- 14 edges to [[_COMMUNITY_Graphify Analyze Module]]
- 3 edges to [[_COMMUNITY_Thesis Debug + Cross-File Analysis]]
- 2 edges to [[_COMMUNITY_Stock Forecast API Predictor]]
- 2 edges to [[_COMMUNITY_Sample Fixtures + Serve]]
- 1 edge to [[_COMMUNITY_Thesis Word Conversion + Frontend API]]

## Top bridge nodes
- [[detect()]] - degree 31, connects to 4 communities
- [[detect.py]] - degree 17, connects to 2 communities
- [[FileType]] - degree 16, connects to 2 communities
- [[detect_incremental()]] - degree 6, connects to 2 communities
- [[test_detect.py]] - degree 29, connects to 1 community