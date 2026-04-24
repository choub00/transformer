---
type: community
cohesion: 0.06
members: 48
---

# Graphify Cache Management

**Cohesion:** 0.06 - loosely connected
**Members:** 48 nodes

## Members
- [[A .md file with no frontmatter is hashed by its full content.]] - rationale - d:\transformer\graphify\tests\test_cache.py
- [[After file content changes, load_cached returns None.]] - rationale - d:\transformer\graphify\tests\test_cache.py
- [[Changing only frontmatter fields in a .md file does not change the hash.]] - rationale - d:\transformer\graphify\tests\test_cache.py
- [[Changing the body of a .md file produces a different hash.]] - rationale - d:\transformer\graphify\tests\test_cache.py
- [[Check semantic extraction cache for a list of absolute file paths.      Return]] - rationale - d:\transformer\graphify\graphify\cache.py
- [[Delete all graphify-outcache.json files.]] - rationale - d:\transformer\graphify\graphify\cache.py
- [[Different file contents give different hashes.]] - rationale - d:\transformer\graphify\tests\test_cache.py
- [[Graphify Semantic Cache]] - code - d:\transformer\graphify\ARCHITECTURE.md
- [[Non-.md files are still hashed by their full content.]] - rationale - d:\transformer\graphify\tests\test_cache.py
- [[Return cached extraction for this file if hash matches, else None.      Cache]] - rationale - d:\transformer\graphify\graphify\cache.py
- [[Return set of file paths that have a valid cache entry (hash still matches).]] - rationale - d:\transformer\graphify\graphify\cache.py
- [[Returns graphify-outcache - creates it if needed.]] - rationale - d:\transformer\graphify\graphify\cache.py
- [[SHA256 of file contents + path relative to root.      Using a relative path (n]] - rationale - d:\transformer\graphify\graphify\cache.py
- [[Same file gives same hash on repeated calls.]] - rationale - d:\transformer\graphify\tests\test_cache.py
- [[Save extraction result for this file.      Stores as graphify-outcache{hash}]] - rationale - d:\transformer\graphify\graphify\cache.py
- [[Save semantic extraction results to cache, keyed by source_file.      Groups n]] - rationale - d:\transformer\graphify\graphify\cache.py
- [[Save then load returns the same result dict.]] - rationale - d:\transformer\graphify\tests\test_cache.py
- [[Strip YAML frontmatter from Markdown content, returning only the body.]] - rationale - d:\transformer\graphify\graphify\cache.py
- [[Tests for graphifycache.py.]] - rationale - d:\transformer\graphify\tests\test_cache.py
- [[_body_content correctly strips YAML frontmatter.]] - rationale - d:\transformer\graphify\tests\test_cache.py
- [[_body_content returns content unchanged when no frontmatter present.]] - rationale - d:\transformer\graphify\tests\test_cache.py
- [[_body_content()]] - code - d:\transformer\graphify\graphify\cache.py
- [[cache.py]] - code - d:\transformer\graphify\graphify\cache.py
- [[cache_dir()]] - code - d:\transformer\graphify\graphify\cache.py
- [[cache_root()]] - code - d:\transformer\graphify\tests\test_cache.py
- [[cached_files returns the set of cached hashes.]] - rationale - d:\transformer\graphify\tests\test_cache.py
- [[cached_files()]] - code - d:\transformer\graphify\graphify\cache.py
- [[check_semantic_cache()]] - code - d:\transformer\graphify\graphify\cache.py
- [[clear_cache removes all .json files from graphify-outcache.]] - rationale - d:\transformer\graphify\tests\test_cache.py
- [[clear_cache()]] - code - d:\transformer\graphify\graphify\cache.py
- [[file_hash()]] - code - d:\transformer\graphify\graphify\cache.py
- [[load_cached()]] - code - d:\transformer\graphify\graphify\cache.py
- [[save_cached()]] - code - d:\transformer\graphify\graphify\cache.py
- [[save_semantic_cache()]] - code - d:\transformer\graphify\graphify\cache.py
- [[test_body_content_no_frontmatter()]] - code - d:\transformer\graphify\tests\test_cache.py
- [[test_body_content_strips_frontmatter()]] - code - d:\transformer\graphify\tests\test_cache.py
- [[test_cache.py]] - code - d:\transformer\graphify\tests\test_cache.py
- [[test_cache_miss_on_change()]] - code - d:\transformer\graphify\tests\test_cache.py
- [[test_cache_roundtrip()]] - code - d:\transformer\graphify\tests\test_cache.py
- [[test_cached_files()]] - code - d:\transformer\graphify\tests\test_cache.py
- [[test_clear_cache()]] - code - d:\transformer\graphify\tests\test_cache.py
- [[test_file_hash_changes()]] - code - d:\transformer\graphify\tests\test_cache.py
- [[test_file_hash_consistent()]] - code - d:\transformer\graphify\tests\test_cache.py
- [[test_md_body_change_different_hash()]] - code - d:\transformer\graphify\tests\test_cache.py
- [[test_md_frontmatter_only_change_same_hash()]] - code - d:\transformer\graphify\tests\test_cache.py
- [[test_md_no_frontmatter_hashed_normally()]] - code - d:\transformer\graphify\tests\test_cache.py
- [[test_non_md_file_hashed_fully()]] - code - d:\transformer\graphify\tests\test_cache.py
- [[tmp_file()]] - code - d:\transformer\graphify\tests\test_cache.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Graphify_Cache_Management
SORT file.name ASC
```

## Connections to other communities
- 3 edges to [[_COMMUNITY_Graphify Extract  Multi-Language Parsers]]
- 3 edges to [[_COMMUNITY_Thesis Debug + Cross-File Analysis]]
- 2 edges to [[_COMMUNITY_Graphify Analyze Module]]
- 1 edge to [[_COMMUNITY_Thesis Doc Analysis Scripts]]

## Top bridge nodes
- [[save_semantic_cache()]] - degree 5, connects to 2 communities
- [[file_hash()]] - degree 13, connects to 1 community
- [[save_cached()]] - degree 10, connects to 1 community
- [[cache.py]] - degree 10, connects to 1 community
- [[load_cached()]] - degree 8, connects to 1 community