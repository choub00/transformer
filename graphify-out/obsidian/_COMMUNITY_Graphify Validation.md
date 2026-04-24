---
type: community
cohesion: 0.20
members: 17
---

# Graphify Validation

**Cohesion:** 0.20 - loosely connected
**Members:** 17 nodes

## Members
- [[Raise ValueError with all errors if extraction is invalid.]] - rationale - d:\transformer\graphify\graphify\validate.py
- [[Validate an extraction JSON dict against the graphify schema.     Returns a lis]] - rationale - d:\transformer\graphify\graphify\validate.py
- [[assert_valid()]] - code - d:\transformer\graphify\graphify\validate.py
- [[test_assert_valid_passes_silently()]] - code - d:\transformer\graphify\tests\test_validate.py
- [[test_assert_valid_raises_on_errors()]] - code - d:\transformer\graphify\tests\test_validate.py
- [[test_dangling_edge_source()]] - code - d:\transformer\graphify\tests\test_validate.py
- [[test_dangling_edge_target()]] - code - d:\transformer\graphify\tests\test_validate.py
- [[test_invalid_confidence()]] - code - d:\transformer\graphify\tests\test_validate.py
- [[test_invalid_file_type()]] - code - d:\transformer\graphify\tests\test_validate.py
- [[test_missing_edges_key()]] - code - d:\transformer\graphify\tests\test_validate.py
- [[test_missing_node_field()]] - code - d:\transformer\graphify\tests\test_validate.py
- [[test_missing_nodes_key()]] - code - d:\transformer\graphify\tests\test_validate.py
- [[test_not_a_dict()]] - code - d:\transformer\graphify\tests\test_validate.py
- [[test_valid_passes()]] - code - d:\transformer\graphify\tests\test_validate.py
- [[test_validate.py]] - code - d:\transformer\graphify\tests\test_validate.py
- [[validate.py]] - code - d:\transformer\graphify\graphify\validate.py
- [[validate_extraction()]] - code - d:\transformer\graphify\graphify\validate.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Graphify_Validation
SORT file.name ASC
```

## Connections to other communities
- 3 edges to [[_COMMUNITY_Graphify Analyze Module]]
- 1 edge to [[_COMMUNITY_Thesis Debug + Cross-File Analysis]]

## Top bridge nodes
- [[validate_extraction()]] - degree 14, connects to 2 communities
- [[test_validate.py]] - degree 12, connects to 1 community
- [[validate.py]] - degree 3, connects to 1 community