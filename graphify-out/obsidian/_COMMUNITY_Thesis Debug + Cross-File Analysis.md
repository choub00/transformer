---
type: community
cohesion: 0.04
members: 90
---

# Thesis Debug + Cross-File Analysis

**Cohesion:** 0.04 - loosely connected
**Members:** 90 nodes

## Members
- [[NOTE must run before compile() or linker will fail]] - rationale - d:\transformer\graphify\tests\test_rationale.py
- [[.copy_with()]] - code - d:\transformer\graphify\worked\httpx\raw\models.py
- [[.get()_6]] - code - d:\transformer\graphify\worked\httpx\raw\models.py
- [[.get()_5]] - code - d:\transformer\graphify\worked\httpx\raw\models.py
- [[.json()]] - code - d:\transformer\graphify\worked\httpx\raw\models.py
- [[AST-resolved call edges are deterministic and should be EXTRACTED1.0.]] - rationale - d:\transformer\graphify\tests\test_extract.py
- [[After merging multiple files, no internal edges should be dangling.]] - rationale - d:\transformer\graphify\tests\test_extract.py
- [[All edge sources must reference a known node (targets may be external imports).]] - rationale - d:\transformer\graphify\tests\test_extract.py
- [[Analyzer.process() calls run_analysis() - cross class→function calls edge.]] - rationale - d:\transformer\graphify\tests\test_extract.py
- [[Call-graph pass must produce INFERRED calls edges.]] - rationale - d:\transformer\graphify\tests\test_extract.py
- [[Cross-File Call Resolution]] - code - d:\transformer\graphify\CHANGELOG.md
- [[Extract classes, functions, and imports from a .py file via tree-sitter AST.]] - rationale - d:\transformer\graphify\graphify\extract.py
- [[Graphify Extract Module]] - code - d:\transformer\graphify\ARCHITECTURE.md
- [[Multi-Language AST Extraction]] - code - d:\transformer\graphify\CHANGELOG.md
- [[Read .graphifyignore from root and ancestor directories.      Returns a li]] - rationale - d:\transformer\graphify\graphify\detect.py
- [[Same caller→callee pair must appear only once even if called multiple times.]] - rationale - d:\transformer\graphify\tests\test_extract.py
- [[Same input always produces same output.]] - rationale - d:\transformer\graphify\tests\test_extract.py
- [[Semantic Extraction via LLM]] - code - d:\transformer\graphify\CHANGELOG.md
- [[Tests for rationaledocstring extraction in extract.py.]] - rationale - d:\transformer\graphify\tests\test_rationale.py
- [[Tree-Sitter AST Parsing]] - code - d:\transformer\graphify\ARCHITECTURE.md
- [[Trivial docstrings under 20 chars should not become rationale nodes.]] - rationale - d:\transformer\graphify\tests\test_rationale.py
- [[_fetch_stooq()]] - code - d:\transformer\Stock Forecast\utils\download_yahoo.py
- [[_fetch_yahoo_chart()]] - code - d:\transformer\Stock Forecast\utils\download_yahoo.py
- [[_get_verify()]] - code - d:\transformer\Stock Forecast\utils\download_yahoo.py
- [[_load_graphifyignore()]] - code - d:\transformer\graphify\graphify\detect.py
- [[_period_to_start()]] - code - d:\transformer\Stock Forecast\utils\download_yahoo.py
- [[_to_stooq_symbol()]] - code - d:\transformer\Stock Forecast\utils\download_yahoo.py
- [[_write_py()]] - code - d:\transformer\graphify\tests\test_rationale.py
- [[academic_rewrite()]] - code - d:\transformer\thesis\debug_full.py
- [[academic_rewrite()_3]] - code - d:\transformer\thesis\debug_templates.py
- [[collect_files()]] - code - d:\transformer\graphify\graphify\extract.py
- [[contains  method  inherits  imports edges must always be EXTRACTED.]] - rationale - d:\transformer\graphify\tests\test_extract.py
- [[debug_analyze.py]] - code - d:\transformer\thesis\debug_analyze.py
- [[debug_full.py]] - code - d:\transformer\thesis\debug_full.py
- [[debug_templates.py]] - code - d:\transformer\thesis\debug_templates.py
- [[download_data()]] - code - d:\transformer\Stock Forecast\utils\download_yahoo.py
- [[download_yahoo.py]] - code - d:\transformer\Stock Forecast\utils\download_yahoo.py
- [[extract_python()]] - code - d:\transformer\graphify\graphify\extract.py
- [[get_all_text()]] - code - d:\transformer\thesis\debug_analyze.py
- [[get_all_text()_2]] - code - d:\transformer\thesis\debug_full.py
- [[get_all_text()_7]] - code - d:\transformer\thesis\debug_templates.py
- [[get_run_color()_1]] - code - d:\transformer\thesis\debug_analyze.py
- [[get_run_color()_4]] - code - d:\transformer\thesis\debug_full.py
- [[get_run_color()_8]] - code - d:\transformer\thesis\debug_templates.py
- [[has_non_black_run()]] - code - d:\transformer\thesis\debug_analyze.py
- [[has_non_black_run()_1]] - code - d:\transformer\thesis\debug_full.py
- [[has_non_black_run()_3]] - code - d:\transformer\thesis\debug_templates.py
- [[is_black_color()]] - code - d:\transformer\thesis\debug_analyze.py
- [[is_black_color()_3]] - code - d:\transformer\thesis\debug_full.py
- [[is_black_color()_7]] - code - d:\transformer\thesis\debug_templates.py
- [[is_formula_paragraph()]] - code - d:\transformer\thesis\debug_analyze.py
- [[is_formula_paragraph()_2]] - code - d:\transformer\thesis\debug_templates.py
- [[is_pagenumber_paragraph()]] - code - d:\transformer\thesis\debug_analyze.py
- [[is_pagenumber_paragraph()_2]] - code - d:\transformer\thesis\debug_templates.py
- [[is_reference_paragraph()]] - code - d:\transformer\thesis\debug_analyze.py
- [[is_reference_paragraph()_2]] - code - d:\transformer\thesis\debug_templates.py
- [[is_title_paragraph()]] - code - d:\transformer\thesis\debug_analyze.py
- [[is_title_paragraph()_2]] - code - d:\transformer\thesis\debug_templates.py
- [[run_analysis() calls compute_score() - must appear as a calls edge.]] - rationale - d:\transformer\graphify\tests\test_extract.py
- [[test_calls_deduplication()]] - code - d:\transformer\graphify\tests\test_extract.py
- [[test_calls_edges_are_extracted()]] - code - d:\transformer\graphify\tests\test_extract.py
- [[test_calls_edges_emitted()]] - code - d:\transformer\graphify\tests\test_extract.py
- [[test_calls_no_self_loops()]] - code - d:\transformer\graphify\tests\test_extract.py
- [[test_class_docstring_extracted()]] - code - d:\transformer\graphify\tests\test_rationale.py
- [[test_collect_files_follows_symlinked_directory()]] - code - d:\transformer\graphify\tests\test_extract.py
- [[test_collect_files_from_dir()]] - code - d:\transformer\graphify\tests\test_extract.py
- [[test_collect_files_handles_circular_symlinks()]] - code - d:\transformer\graphify\tests\test_extract.py
- [[test_collect_files_skips_hidden()]] - code - d:\transformer\graphify\tests\test_extract.py
- [[test_extract.py]] - code - d:\transformer\graphify\tests\test_extract.py
- [[test_extract_python_finds_class()]] - code - d:\transformer\graphify\tests\test_extract.py
- [[test_extract_python_finds_methods()]] - code - d:\transformer\graphify\tests\test_extract.py
- [[test_extract_python_no_dangling_edges()]] - code - d:\transformer\graphify\tests\test_extract.py
- [[test_function_docstring_extracted()]] - code - d:\transformer\graphify\tests\test_rationale.py
- [[test_make_id_consistent()]] - code - d:\transformer\graphify\tests\test_extract.py
- [[test_make_id_no_leading_trailing_underscores()]] - code - d:\transformer\graphify\tests\test_extract.py
- [[test_make_id_strips_dots_and_underscores()]] - code - d:\transformer\graphify\tests\test_extract.py
- [[test_method_calls_module_function()]] - code - d:\transformer\graphify\tests\test_extract.py
- [[test_module_docstring_extracted()]] - code - d:\transformer\graphify\tests\test_rationale.py
- [[test_no_dangling_edges_on_extract()]] - code - d:\transformer\graphify\tests\test_extract.py
- [[test_rationale.py]] - code - d:\transformer\graphify\tests\test_rationale.py
- [[test_rationale_comment_extracted()]] - code - d:\transformer\graphify\tests\test_rationale.py
- [[test_rationale_confidence_is_extracted()]] - code - d:\transformer\graphify\tests\test_rationale.py
- [[test_rationale_for_edges_present()]] - code - d:\transformer\graphify\tests\test_rationale.py
- [[test_run_analysis_calls_compute_score()]] - code - d:\transformer\graphify\tests\test_extract.py
- [[test_run_analysis_calls_normalize()]] - code - d:\transformer\graphify\tests\test_extract.py
- [[test_short_docstring_ignored()]] - code - d:\transformer\graphify\tests\test_rationale.py
- [[test_structural_edges_are_extracted()]] - code - d:\transformer\graphify\tests\test_extract.py
- [[w()]] - code - d:\transformer\thesis\debug_analyze.py
- [[w()_2]] - code - d:\transformer\thesis\debug_full.py
- [[w()_7]] - code - d:\transformer\thesis\debug_templates.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Thesis_Debug_+_Cross-File_Analysis
SORT file.name ASC
```

## Connections to other communities
- 42 edges to [[_COMMUNITY_Graphify Analyze Module]]
- 29 edges to [[_COMMUNITY_Thesis Doc Analysis Scripts]]
- 25 edges to [[_COMMUNITY_Graphify Extract  Multi-Language Parsers]]
- 10 edges to [[_COMMUNITY_Graphify Hooks + Agents CLI]]
- 10 edges to [[_COMMUNITY_Stock Forecast API Predictor]]
- 8 edges to [[_COMMUNITY_Trading Account Manager + Auto]]
- 7 edges to [[_COMMUNITY_Graphify Worked Example API]]
- 7 edges to [[_COMMUNITY_HTTPX Auth + Client]]
- 6 edges to [[_COMMUNITY_Sample Fixtures + Serve]]
- 5 edges to [[_COMMUNITY_Thesis Word Conversion + Frontend API]]
- 5 edges to [[_COMMUNITY_Graphify Wiki Generator]]
- 4 edges to [[_COMMUNITY_Graphify Ingest + Security]]
- 3 edges to [[_COMMUNITY_Graphify Cache Management]]
- 3 edges to [[_COMMUNITY_Graphify File Detection]]
- 2 edges to [[_COMMUNITY_Community 30]]
- 2 edges to [[_COMMUNITY_Thesis Step-3 Rewrite Scripts]]
- 2 edges to [[_COMMUNITY_Thesis Step-4 Final Rewrite]]
- 2 edges to [[_COMMUNITY_Thesis Step-5 Final Rewrite]]
- 2 edges to [[_COMMUNITY_Thesis Step-6 Natural Rewrite]]
- 2 edges to [[_COMMUNITY_AlphaTransformer Core Models]]
- 2 edges to [[_COMMUNITY_Stock Forecast Data + Training Pipeline]]
- 1 edge to [[_COMMUNITY_Graphify Benchmark Module]]
- 1 edge to [[_COMMUNITY_Graphify Validation]]
- 1 edge to [[_COMMUNITY_AlphaTransformer 2026 Adaptive Layers]]
- 1 edge to [[_COMMUNITY_Community 39]]
- 1 edge to [[_COMMUNITY_Community 38]]
- 1 edge to [[_COMMUNITY_Community 37]]
- 1 edge to [[_COMMUNITY_Community 40]]

## Top bridge nodes
- [[.get()_6]] - degree 171, connects to 27 communities
- [[download_data()]] - degree 10, connects to 3 communities
- [[Graphify Extract Module]] - degree 10, connects to 2 communities
- [[collect_files()]] - degree 7, connects to 2 communities
- [[.json()]] - degree 3, connects to 2 communities