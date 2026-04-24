---
name: graphify
description: "any input (code, docs, papers, images) → knowledge graph → clustered communities → HTML + JSON + audit report"
trigger: /graphify
origin: https://github.com/safishamsi/graphify | adapted for Cursor on Windows
tags: [knowledge-graph, rag, code-understanding, research, documentation]
---

# /graphify — Knowledge Graph for Cursor

Build a persistent, queryable knowledge graph from any folder of code, docs, papers, or images. Works in the `D:/transformer` workspace. Outputs: interactive `graph.html`, `GRAPH_REPORT.md`, `graph.json`, and optional Obsidian vault.

## Usage

```
/graphify                                             # full pipeline on current directory
/graphify <path>                                      # full pipeline on specific path
/graphify <path> --mode deep                          # aggressive INFERRED edge extraction
/graphify <path> --update                             # incremental - re-extract only changed files
/graphify <path> --directed                           # directed graph (preserves edge direction)
/graphify <path> --cluster-only                       # rerun clustering on existing graph.json
/graphify <path> --no-viz                             # skip HTML/Obsidian, just report + JSON
/graphify <path> --svg                                # also export graph.svg
/graphify <path> --graphml                            # export graph.graphml (Gephi, yEd)
/graphify <path> --obsidian                           # generate Obsidian vault
/graphify <path> --wiki                               # build agent-crawlable wiki
/graphify <path> --watch                              # auto-rebuild on code changes (no LLM)
/graphify add <url>                                   # fetch URL → ./raw, then update graph
/graphify query "<question>"                          # BFS traversal of graph.json
/graphify query "<question>" --dfs                     # DFS - trace specific path
/graphify query "<question>" --budget N               # cap at N tokens (default 2000)
/graphify path "ConceptA" "ConceptB"                  # shortest path between two nodes
/graphify explain "NodeName"                           # plain-language explanation
graphify hook install                                  # post-commit auto-rebuild
```

## What graphify is for

Three things it does that AI alone cannot:
1. **Persistent graph** - `graphify-out/graph.json` survives across sessions; ask questions weeks later
2. **Honest audit trail** - every edge tagged EXTRACTED / INFERRED / AMBIGUOUS
3. **Cross-document surprise** - community detection finds connections across files you'd never ask about

## Interpreter Setup

**On every new session**, run this once to ensure graphify is available:

```python
import subprocess, sys
# Try system python first, fallback to d:\python
for python in ["python", "d:\\python\\python.exe", "D:\\python.exe"]:
    try:
        r = subprocess.run([python, "-c", "import graphify"], capture_output=True)
        if r.returncode == 0:
            print(f"graphify OK via: {python}")
            break
    except FileNotFoundError:
        continue
else:
    print("Installing graphifyy...")
    subprocess.run([sys.executable, "-m", "pip", "install", "graphifyy", "--quiet"])
```

Then write the interpreter path so subsequent steps use the same Python:

```python
import os
os.makedirs("d:/transformer/graphify-out", exist_ok=True)
with open("d:/transformer/graphify-out/.graphify_python", "w") as f:
    f.write(python)
print(f"Stored: {python}")
```

**For all Python blocks below, read `.graphify_python` first to get the interpreter path.** The stored path is `d:/transformer/graphify-out/.graphify_python`.

---

## Full Pipeline — Step by Step

### Step 1 — Detect files

```python
import json, subprocess, os

interp = open("d:/transformer/graphify-out/.graphify_python").read().strip()
input_path = "INPUT_PATH"  # replace with actual path

result = subprocess.run(
    [interp, "-c", f"""
import json
from graphify.detect import detect
from pathlib import Path
r = detect(Path({repr(input_path)}))
print(json.dumps(r))
"""],
    capture_output=True, text=True
)
detect_out = json.loads(result.stdout)
print(json.dumps(detect_out, indent=2))
```

Present a clean summary:
```
Corpus: X files · ~Y words
  code:   N files
  docs:   N files
  papers: N files
  images: N files
```

Rules:
- `total_files == 0` → stop: "No supported files found."
- `total_words > 2,000,000` OR `total_files > 200` → show top 5 subdirs, ask which subfolder to process.
- Video files → transcribe first (Step 2.5), then continue.
- Otherwise → proceed to Step 3.

Save detect output:
```python
with open("d:/transformer/graphify-out/.graphify_detect.json", "w") as f:
    json.dump(detect_out, f)
```

### Step 1.5 — Video transcription (only if video files exist)

Skip if no video files. Write Whisper prompt from god nodes, then:

```python
import json, subprocess, os

interp = open("d:/transformer/graphify-out/.graphify_python").read().strip()
detect_out = json.load(open("d:/transformer/graphify-out/.graphify_detect.json"))
video_files = detect_out.get("files", {}).get("video", [])
if not video_files:
    print("No video files - skipping transcription")
else:
    result = subprocess.run(
        [interp, "-c", f"""
import json, os
from pathlib import Path
from graphify.transcribe import transcribe_all
video = {json.dumps(video_files)}
prompt = os.environ.get("GRAPHIFY_WHISPER_PROMPT", "Use proper punctuation and paragraph breaks.")
paths = transcribe_all(video, initial_prompt=prompt)
print(json.dumps(paths))
"""],
        capture_output=True, text=True, env={**os.environ, "GRAPHIFY_WHISPER_MODEL": "base"}
    )
    print(result.stdout)
    print(result.stderr[:500] if result.stderr else "")
```

Print: `Transcribed N video file(s) → treating as docs`

### Step 2 — Extract entities and relationships

This has two parallel parts:
- **Part A: AST extraction** (code files, fast, deterministic, free)
- **Part B: Semantic extraction** (docs/papers/images, Claude API, costs tokens)

Start both in the same message — they run in parallel on different file types.

#### Part A — AST extraction (code files)

```python
import json, subprocess, os

interp = open("d:/transformer/graphify-out/.graphify_python").read().strip()
detect_out = json.load(open("d:/transformer/graphify-out/.graphify_detect.json"))
code_files = detect_out.get("files", {}).get("code", [])

if code_files:
    result = subprocess.run(
        [interp, "-c", f"""
import json
from graphify.extract import collect_files, extract
from pathlib import Path
files = {json.dumps(code_files)}
paths = [Path(f) for f in files]
result = extract(paths, cache_root=Path('.'))
Path('d:/transformer/graphify-out/.graphify_ast.json').write_text(json.dumps(result))
print(f"AST: {{len(result['nodes'])}} nodes, {{len(result['edges'])}} edges")
"""],
        capture_output=True, text=True, cwd="d:/transformer"
    )
    print(result.stdout)
    print(result.stderr[:500] if result.stderr else "")
else:
    print("No code files - skipping AST extraction")
    with open("d:/transformer/graphify-out/.graphify_ast.json", "w") as f:
        json.dump({"nodes": [], "edges": [], "input_tokens": 0, "output_tokens": 0}, f)
```

#### Part B — Semantic extraction (parallel subagents)

**MANDATORY: Use the Task tool with `subagent_type="general-purpose"` for this step.**

**Check cache first:**

```python
import json, subprocess

interp = open("d:/transformer/graphify-out/.graphify_python").read().strip()
result = subprocess.run(
    [interp, "-c", """
import json
from graphify.cache import check_semantic_cache
from pathlib import Path

detect = json.loads(Path('d:/transformer/graphify-out/.graphify_detect.json').read_text())
all_files = [f for files in detect['files'].values() for f in files]
cached_nodes, cached_edges, cached_hyperedges, uncached = check_semantic_cache(all_files)

if cached_nodes or cached_edges:
    Path('d:/transformer/graphify-out/.graphify_cached.json').write_text(
        json.dumps({'nodes': cached_nodes, 'edges': cached_edges, 'hyperedges': cached_hyperedges}))
Path('d:/transformer/graphify-out/.graphify_uncached.txt').write_text('\\n'.join(uncached))
print(f'Cache: {len(all_files)-len(uncached)} hit, {len(uncached)} need extraction')
"""],
    capture_output=True, text=True
)
print(result.stdout)
```

**If all files are cached → skip to Part C.**
**If code-only → still run AST (already done in Part A), then check if there are docs/papers/images to semantic-extract.**

**Estimate agents:** `ceil(len(uncached_files) / 22)` agents, ~45s per batch. Print estimate.

**Split uncached files into chunks of 20-25.** Each image gets its own chunk. Group files from same directory together.

**Dispatch ALL subagents in one message.** Each receives:

```
You are a graphify extraction subagent for Cursor. Read the listed files, extract a knowledge graph fragment.
Output ONLY valid JSON matching the schema — no explanation, no markdown fences.

Files (chunk N of TOTAL):
FILE_LIST

Rules:
- EXTRACTED: relationship explicit in source (import, call, citation)
- INFERRED: reasonable deduction (shared data, implied dependency)
- AMBIGUOUS: uncertain — flag for review
- Code files: focus on semantic edges AST cannot find
- Doc/paper files: extract concepts, citations, rationale (WHY decisions were made)
- Image files: use vision — UI screenshot, chart, diagram, tweet, research figure, whiteboard
- DEEP_MODE: be aggressive with INFERRED edges, mark uncertain as AMBIGUOUS
- Semantic similarity: add semantically_similar_to edges for non-obvious cross-cutting similarities (0.6-0.95 score)
- Hyperedges: groups of 3+ nodes in a shared pattern (max 3 per chunk)
- YAML frontmatter: copy source_url, captured_at, author, contributor to every node

Node ID format: lowercase `[a-z0-9_]`, `{stem}_{entity}` — must match AST extractor IDs.

Output schema:
{"nodes":[{"id":"...","label":"...","file_type":"code|document|paper|image","source_file":"...","source_location":null,"source_url":null,"captured_at":null,"author":null,"contributor":null}],"edges":[{"source":"...","target":"...","relation":"calls|implements|references|cites|conceptually_related_to|shares_data_with|semantically_similar_to|rationale_for","confidence":"EXTRACTED|INFERRED|AMBIGUOUS","confidence_score":1.0,"source_file":"...","source_location":null,"weight":1.0}],"hyperedges":[{"id":"...","label":"...","nodes":["..."],"relation":"participate_in|implement|form","confidence":"EXTRACTED|INFERRED","confidence_score":0.75,"source_file":"..."}],"input_tokens":0,"output_tokens":0}
```

Each subagent writes its result to `d:/transformer/graphify-out/.graphify_chunk_NN.json` where NN is its chunk number (01, 02, ...).

**Collect and merge results:**

```python
import json, subprocess, os

interp = open("d:/transformer/graphify-out/.graphify_python").read().strip()
result = subprocess.run(
    [interp, "-c", """
import json
from pathlib import Path

# Collect all chunk files
merged = {"nodes": [], "edges": [], "hyperedges": [], "input_tokens": 0, "output_tokens": 0}
for i in range(1, 999):
    chunk_file = Path(f'd:/transformer/graphify-out/.graphify_chunk_{i:02d}.json')
    if chunk_file.exists():
        try:
            chunk = json.loads(chunk_file.read_text())
            merged["nodes"].extend(chunk.get("nodes", []))
            merged["edges"].extend(chunk.get("edges", []))
            merged["hyperedges"].extend(chunk.get("hyperedges", []))
            merged["input_tokens"] += chunk.get("input_tokens", 0)
            merged["output_tokens"] += chunk.get("output_tokens", 0)
        except Exception as e:
            print(f"Chunk {i} error: {e}")

# Deduplicate nodes
seen = set()
deduped = []
for n in merged["nodes"]:
    if n["id"] not in seen:
        seen.add(n["id"])
        deduped.append(n)

merged["nodes"] = deduped
print(f"Merged: {len(deduped)} nodes, {len(merged['edges'])} edges")
Path('d:/transformer/graphify-out/.graphify_semantic_new.json').write_text(json.dumps(merged))
"""],
    capture_output=True, text=True
)
print(result.stdout)
print(result.stderr[:300] if result.stderr else "")
```

**Cache new results and merge with cached:**

```python
import json, subprocess

interp = open("d:/transformer/graphify-out/.graphify_python").read().strip()
result = subprocess.run(
    [interp, "-c", """
import json
from graphify.cache import save_semantic_cache
from pathlib import Path

new = json.loads(Path('d:/transformer/graphify-out/.graphify_semantic_new.json').read_text())
saved = save_semantic_cache(new.get('nodes', []), new.get('edges', []), new.get('hyperedges', []))
print(f'Cached {saved} files')

# Merge cached + new
cached = json.loads(Path('d:/transformer/graphify-out/.graphify_cached.json').read_text()) \\
    if Path('d:/transformer/graphify-out/.graphify_cached.json').exists() \\
    else {'nodes': [], 'edges': [], 'hyperedges': []}

all_nodes = cached['nodes'] + new.get('nodes', [])
all_edges = cached['edges'] + new.get('edges', [])
all_hyper = cached.get('hyperedges', []) + new.get('hyperedges', [])

seen = set()
deduped = []
for n in all_nodes:
    if n['id'] not in seen:
        seen.add(n['id'])
        deduped.append(n)

merged = {
    'nodes': deduped,
    'edges': all_edges,
    'hyperedges': all_hyper,
    'input_tokens': new.get('input_tokens', 0),
    'output_tokens': new.get('output_tokens', 0),
}
Path('d:/transformer/graphify-out/.graphify_semantic.json').write_text(json.dumps(merged))
print(f'Extraction: {len(deduped)} nodes, {len(all_edges)} edges ({len(cached["nodes"])} cached + {len(new.get("nodes",[]))} new)')
"""],
    capture_output=True, text=True
)
print(result.stdout)
print(result.stderr[:300] if result.stderr else "")
```

#### Part C — Merge AST + semantic

```python
import json, subprocess

interp = open("d:/transformer/graphify-out/.graphify_python").read().strip()
result = subprocess.run(
    [interp, "-c", """
import json
from pathlib import Path

ast = json.loads(Path('d:/transformer/graphify-out/.graphify_ast.json').read_text())
sem = json.loads(Path('d:/transformer/graphify-out/.graphify_semantic.json').read_text())

seen = {n['id'] for n in ast['nodes']}
merged_nodes = list(ast['nodes'])
for n in sem['nodes']:
    if n['id'] not in seen:
        merged_nodes.append(n)
        seen.add(n['id'])

merged_edges = ast['edges'] + sem['edges']
merged_hyperedges = sem.get('hyperedges', [])

merged = {
    'nodes': merged_nodes,
    'edges': merged_edges,
    'hyperedges': merged_hyperedges,
    'input_tokens': sem.get('input_tokens', 0),
    'output_tokens': sem.get('output_tokens', 0),
}
Path('d:/transformer/graphify-out/.graphify_extract.json').write_text(json.dumps(merged, indent=2))
print(f'Merged: {len(merged_nodes)} nodes, {len(merged_edges)} edges ({len(ast["nodes"])} AST + {len(sem["nodes"])} semantic)')
"""],
    capture_output=True, text=True
)
print(result.stdout)
print(result.stderr[:300] if result.stderr else "")
```

### Step 3 — Build graph, cluster, analyze

```python
import json, subprocess

interp = open("d:/transformer/graphify-out/.graphify_python").read().strip()
input_path = "INPUT_PATH"
directed = False  # set True if --directed flag was given

code = f"""
import json
from graphify.build import build_from_json
from graphify.cluster import cluster, score_all
from graphify.analyze import god_nodes, surprising_connections, suggest_questions
from graphify.report import generate
from graphify.export import to_json
from pathlib import Path

extraction = json.loads(Path('d:/transformer/graphify-out/.graphify_extract.json').read_text())
detection  = json.loads(Path('d:/transformer/graphify-out/.graphify_detect.json').read_text())

G = build_from_json(extraction, directed={directed})
communities = cluster(G)
cohesion = score_all(G, communities)
tokens = {{'input': extraction.get('input_tokens', 0), 'output': extraction.get('output_tokens', 0)}}
gods = god_nodes(G)
surprises = surprising_connections(G, communities)
labels = {{cid: 'Community ' + str(cid) for cid in communities}}
questions = suggest_questions(G, communities, labels)

report = generate(G, communities, cohesion, labels, gods, surprises, detection, tokens, {repr(input_path)}, suggested_questions=questions)
Path('d:/transformer/graphify-out/GRAPH_REPORT.md').write_text(report)
to_json(G, communities, 'd:/transformer/graphify-out/graph.json')

analysis = {{
    'communities': {{str(k): v for k, v in communities.items()}},
    'cohesion': {{str(k): v for k, v in cohesion.items()}},
    'gods': gods,
    'surprises': surprises,
    'questions': questions,
}}
Path('d:/transformer/graphify-out/.graphify_analysis.json').write_text(json.dumps(analysis, indent=2))

if G.number_of_nodes() == 0:
    print('ERROR: Graph is empty')
    raise SystemExit(1)
print(f'Graph: {{G.number_of_nodes()}} nodes, {{G.number_of_edges()}} edges, {{len(communities)}} communities')
"""

result = subprocess.run([interp, "-c", code], capture_output=True, text=True, cwd="d:/transformer")
print(result.stdout)
print(result.stderr[:500] if result.stderr else "")
```

### Step 4 — Label communities

Read `d:/transformer/graphify-out/.graphify_analysis.json`, look at each community's node labels, write 2-5 word names.

Then regenerate the report:

```python
import json, subprocess

interp = open("d:/transformer/graphify-out/.graphify_python").read().strip()
input_path = "INPUT_PATH"
# LABELS_DICT example: {0: "Attention Mechanism", 1: "Training Pipeline"}
labels_dict = {}  # replace with your labels

code = f"""
import json
from graphify.build import build_from_json
from graphify.cluster import score_all
from graphify.analyze import god_nodes, surprising_connections, suggest_questions
from graphify.report import generate
from pathlib import Path

extraction = json.loads(Path('d:/transformer/graphify-out/.graphify_extract.json').read_text())
detection  = json.loads(Path('d:/transformer/graphify-out/.graphify_detect.json').read_text())
analysis   = json.loads(Path('d:/transformer/graphify-out/.graphify_analysis.json').read_text())

G = build_from_json(extraction)
communities = {{int(k): v for k, v in analysis['communities'].items()}}
cohesion = {{int(k): v for k, v in analysis['cohesion'].items()}}
tokens = {{'input': extraction.get('input_tokens', 0), 'output': extraction.get('output_tokens', 0)}}

labels = {json.dumps({str(k): v for k, v in labels_dict.items()})}
questions = suggest_questions(G, communities, labels)

report = generate(G, communities, cohesion, labels, analysis['gods'], analysis['surprises'], detection, tokens, {repr(input_path)}, suggested_questions=questions)
Path('d:/transformer/graphify-out/GRAPH_REPORT.md').write_text(report)
Path('d:/transformer/graphify-out/.graphify_labels.json').write_text(json.dumps({{str(k): v for k, v in labels_dict.items()}}))
print('Report updated with community labels')
"""

result = subprocess.run([interp, "-c", code], capture_output=True, text=True, cwd="d:/transformer")
print(result.stdout)
```

### Step 5 — Generate outputs

**HTML (always, unless --no-viz):**

```python
import json, subprocess

interp = open("d:/transformer/graphify-out/.graphify_python").read().strip()
result = subprocess.run(
    [interp, "-c", """
import json
from graphify.build import build_from_json
from graphify.export import to_html
from pathlib import Path

extraction = json.loads(Path('d:/transformer/graphify-out/.graphify_extract.json').read_text())
analysis   = json.loads(Path('d:/transformer/graphify-out/.graphify_analysis.json').read_text())
labels_raw = json.loads(Path('d:/transformer/graphify-out/.graphify_labels.json').read_text()) \\
    if Path('d:/transformer/graphify-out/.graphify_labels.json').exists() else {}

G = build_from_json(extraction)
communities = {int(k): v for k, v in analysis['communities'].items()}
labels = {int(k): v for k, v in labels_raw.items()}

if G.number_of_nodes() > 5000:
    print(f'Graph has {G.number_of_nodes()} nodes - too large for HTML viz. Use Obsidian vault.')
else:
    to_html(G, communities, 'd:/transformer/graphify-out/graph.html', community_labels=labels or None)
    print('graph.html written - open in any browser')
"""],
    capture_output=True, text=True, cwd="d:/transformer"
)
print(result.stdout)
print(result.stderr[:300] if result.stderr else "")
```

**Obsidian vault (only if --obsidian):**

```python
import json, subprocess

interp = open("d:/transformer/graphify-out/.graphify_python").read().strip()
result = subprocess.run(
    [interp, "-c", """
import json
from graphify.build import build_from_json
from graphify.export import to_obsidian, to_canvas
from pathlib import Path

extraction = json.loads(Path('d:/transformer/graphify-out/.graphify_extract.json').read_text())
analysis   = json.loads(Path('d:/transformer/graphify-out/.graphify_analysis.json').read_text())
labels_raw = json.loads(Path('d:/transformer/graphify-out/.graphify_labels.json').read_text()) \\
    if Path('d:/transformer/graphify-out/.graphify_labels.json').exists() else {}

G = build_from_json(extraction)
communities = {int(k): v for k, v in analysis['communities'].items()}
cohesion = {int(k): v for k, v in analysis['cohesion'].items()}
labels = {int(k): v for k, v in labels_raw.items()}

obsidian_dir = 'd:/transformer/graphify-out/obsidian'
n = to_obsidian(G, communities, obsidian_dir, community_labels=labels or None, cohesion=cohesion)
print(f'Obsidian vault: {n} notes in {obsidian_dir}/')
to_canvas(G, communities, f'{obsidian_dir}/graph.canvas', community_labels=labels or None)
print(f'Canvas: {obsidian_dir}/graph.canvas')
"""],
    capture_output=True, text=True, cwd="d:/transformer"
)
print(result.stdout)
```

**Wiki (only if --wiki):**

```python
import json, subprocess

interp = open("d:/transformer/graphify-out/.graphify_python").read().strip()
result = subprocess.run(
    [interp, "-c", """
import json
from graphify.build import build_from_json
from graphify.wiki import to_wiki
from graphify.analyze import god_nodes
from pathlib import Path

extraction = json.loads(Path('d:/transformer/graphify-out/.graphify_extract.json').read_text())
analysis   = json.loads(Path('d:/transformer/graphify-out/.graphify_analysis.json').read_text())
labels_raw = json.loads(Path('d:/transformer/graphify-out/.graphify_labels.json').read_text()) \\
    if Path('d:/transformer/graphify-out/.graphify_labels.json').exists() else {}

G = build_from_json(extraction)
communities = {int(k): v for k, v in analysis['communities'].items()}
cohesion = {int(k): v for k, v in analysis['cohesion'].items()}
labels = {int(k): v for k, v in labels_raw.items()}
gods = god_nodes(G)

n = to_wiki(G, communities, 'd:/transformer/graphify-out/wiki', community_labels=labels or None, cohesion=cohesion, god_nodes_data=gods)
print(f'Wiki: {n} articles in graphify-out/wiki/')
"""],
    capture_output=True, text=True, cwd="d:/transformer"
)
print(result.stdout)
```

**SVG (only if --svg):**

```python
import json, subprocess

interp = open("d:/transformer/graphify-out/.graphify_python").read().strip()
result = subprocess.run(
    [interp, "-c", """
import json
from graphify.build import build_from_json
from graphify.export import to_svg
from pathlib import Path

extraction = json.loads(Path('d:/transformer/graphify-out/.graphify_extract.json').read_text())
analysis   = json.loads(Path('d:/transformer/graphify-out/.graphify_analysis.json').read_text())
labels_raw = json.loads(Path('d:/transformer/graphify-out/.graphify_labels.json').read_text()) \\
    if Path('d:/transformer/graphify-out/.graphify_labels.json').exists() else {}

G = build_from_json(extraction)
communities = {int(k): v for k, v in analysis['communities'].items()}
labels = {int(k): v for k, v in labels_raw.items()}
to_svg(G, communities, 'd:/transformer/graphify-out/graph.svg', community_labels=labels or None)
print('graph.svg written')
"""],
    capture_output=True, text=True, cwd="d:/transformer"
)
print(result.stdout)
```

**Benchmark (only if total_words > 5000):**

```python
import json, subprocess

interp = open("d:/transformer/graphify-out/.graphify_python").read().strip()
result = subprocess.run(
    [interp, "-c", """
import json
from graphify.benchmark import run_benchmark, print_benchmark
from pathlib import Path

detection = json.loads(Path('d:/transformer/graphify-out/.graphify_detect.json').read_text())
result = run_benchmark('d:/transformer/graphify-out/graph.json', corpus_words=detection['total_words'])
print_benchmark(result)
"""],
    capture_output=True, text=True, cwd="d:/transformer"
)
print(result.stdout)
```

### Step 6 — Save manifest, cost tracker, clean up

```python
import json, subprocess
from datetime import datetime, timezone

interp = open("d:/transformer/graphify-out/.graphify_python").read().strip()
result = subprocess.run(
    [interp, "-c", """
import json
from pathlib import Path
from datetime import datetime, timezone
from graphify.detect import save_manifest

detect = json.loads(Path('d:/transformer/graphify-out/.graphify_detect.json').read_text())
save_manifest(detect['files'])

extract = json.loads(Path('d:/transformer/graphify-out/.graphify_extract.json').read_text())
input_tok = extract.get('input_tokens', 0)
output_tok = extract.get('output_tokens', 0)

cost_path = Path('d:/transformer/graphify-out/cost.json')
if cost_path.exists():
    cost = json.loads(cost_path.read_text())
else:
    cost = {'runs': [], 'total_input_tokens': 0, 'total_output_tokens': 0}

cost['runs'].append({
    'date': datetime.now(timezone.utc).isoformat(),
    'input_tokens': input_tok,
    'output_tokens': output_tok,
    'files': detect.get('total_files', 0),
})
cost['total_input_tokens'] += input_tok
cost['total_output_tokens'] += output_tok
cost_path.write_text(json.dumps(cost, indent=2))

print(f'This run: {input_tok:,} input, {output_tok:,} output tokens')
print(f'All time: {cost["total_input_tokens"]:,} input, {cost["total_output_tokens"]:,} output ({len(cost["runs"])} runs)')
"""],
    capture_output=True, text=True, cwd="d:/transformer"
)
print(result.stdout)
```

**Clean up temp files:**

```python
import os
temp_files = [
    "d:/transformer/graphify-out/.graphify_detect.json",
    "d:/transformer/graphify-out/.graphify_extract.json",
    "d:/transformer/graphify-out/.graphify_ast.json",
    "d:/transformer/graphify-out/.graphify_semantic.json",
    "d:/transformer/graphify-out/.graphify_semantic_new.json",
    "d:/transformer/graphify-out/.graphify_analysis.json",
    "d:/transformer/graphify-out/.graphify_labels.json",
    "d:/transformer/graphify-out/.graphify_cached.json",
    "d:/transformer/graphify-out/.graphify_uncached.txt",
    "d:/transformer/graphify-out/.graphify_incremental.json",
]
for f in temp_files:
    if os.path.exists(f):
        os.remove(f)
print("Temp files cleaned")
```

### Final report

Tell the user:
```
Graph complete. Outputs in PATH/graphify-out/
  graph.html        - interactive graph, open in browser
  GRAPH_REPORT.md   - audit report
  graph.json        - raw graph data
  obsidian/         - Obsidian vault (if --obsidian)
  wiki/             - agent-crawlable wiki (if --wiki)
```

Then paste these three sections from `d:/transformer/graphify-out/GRAPH_REPORT.md`:
- **God Nodes**
- **Surprising Connections**
- **Suggested Questions**

Offer to explore: pick the most interesting suggested question (crosses most community boundaries), ask: "The most interesting question this graph can answer: **[question]**. Want me to trace it?"

---

## /graphify query

Check graph exists first:

```python
import os
if not os.path.exists("d:/transformer/graphify-out/graph.json"):
    print("ERROR: No graph found. Run /graphify <path> first.")
```

Then run BFS/DFS traversal:

```python
import json, subprocess

interp = open("d:/transformer/graphify-out/.graphify_python").read().strip()
question = "QUESTION_TEXT"
mode = "bfs"  # or "dfs"
budget = 2000

code = f"""
import json, sys
from networkx.readwrite import json_graph
from pathlib import Path

data = json.loads(Path('d:/transformer/graphify-out/graph.json').read_text())
G = json_graph.node_link_graph(data, edges='links')

question = {repr(question)}
mode = {repr(mode)}
budget = {budget}
terms = [t.lower() for t in question.split() if len(t) > 3]

scored = []
for nid, ndata in G.nodes(data=True):
    label = ndata.get('label', '').lower()
    score = sum(1 for t in terms if t in label)
    if score > 0:
        scored.append((score, nid))
scored.sort(reverse=True)
start_nodes = [nid for _, nid in scored[:3]]

if not start_nodes:
    print('No matching nodes for:', terms)
    sys.exit(0)

subgraph_nodes = set()
subgraph_edges = []

if mode == 'dfs':
    visited = set()
    stack = [(n, 0) for n in reversed(start_nodes)]
    while stack:
        node, depth = stack.pop()
        if node in visited or depth > 6:
            continue
        visited.add(node)
        subgraph_nodes.add(node)
        for neighbor in G.neighbors(node):
            if neighbor not in visited:
                stack.append((neighbor, depth + 1))
                subgraph_edges.append((node, neighbor))
else:
    frontier = set(start_nodes)
    subgraph_nodes = set(start_nodes)
    for _ in range(3):
        next_frontier = set()
        for n in frontier:
            for neighbor in G.neighbors(n):
                if neighbor not in subgraph_nodes:
                    next_frontier.add(neighbor)
                    subgraph_edges.append((n, neighbor))
        subgraph_nodes.update(next_frontier)
        frontier = next_frontier

char_budget = budget * 4

def relevance(nid):
    return sum(1 for t in terms if t in G.nodes[nid].get('label','').lower())

ranked = sorted(subgraph_nodes, key=relevance, reverse=True)
lines = [f'Traversal: {mode.upper()} | {len(subgraph_nodes)} nodes']
for nid in ranked:
    d = G.nodes[nid]
    lines.append(f'  NODE {d.get("label", nid)} [src={d.get("source_file","")}]')
for u, v in subgraph_edges:
    if u in subgraph_nodes and v in subgraph_nodes:
        e = G.edges[u, v]
        lines.append(f'  {G.nodes[u].get("label",u)} --{e.get("relation","")} [{e.get("confidence","")}]--> {G.nodes[v].get("label",v)}')

output = '\\n'.join(lines)
if len(output) > char_budget:
    output = output[:char_budget] + f'\\n... (truncated at ~{budget} token budget)'
print(output)
"""

result = subprocess.run([interp, "-c", code], capture_output=True, text=True, cwd="d:/transformer")
print(result.stdout)
```

Then answer using the graph data. Quote `source_location` when citing facts.

---

## /graphify path

```python
import json, subprocess

interp = open("d:/transformer/graphify-out/.graphify_python").read().strip()
node_a = "NODE_A_NAME"
node_b = "NODE_B_NAME"

code = f"""
import json, sys, networkx as nx
from networkx.readwrite import json_graph
from pathlib import Path

data = json.loads(Path('d:/transformer/graphify-out/graph.json').read_text())
G = json_graph.node_link_graph(data, edges='links')

def find_node(term):
    term = term.lower()
    scored = sorted(
        [(sum(1 for w in term.split() if w in G.nodes[n].get('label','').lower()) or
          sum(1 for c in term if c in G.nodes[n].get('label','')), n)
         for n in G.nodes()],
        reverse=True
    )
    return scored[0][1] if scored and scored[0][0] > 0 else None

src = find_node({repr(node_a)})
tgt = find_node({repr(node_b)})
if not src or not tgt:
    print(f'Could not find: {repr(node_a)} or {repr(node_b)}')
    sys.exit(0)

try:
    path = nx.shortest_path(G, src, tgt)
    print(f'Shortest path ({len(path)-1} hops):')
    for i, nid in enumerate(path):
        label = G.nodes[nid].get('label', nid)
        if i < len(path) - 1:
            edge = G.edges[nid, path[i+1]]
            print(f'  {{label}} --{{edge.get("relation","")}}--> [{{edge.get("confidence","")}}]')
        else:
            print(f'  {{label}}')
except nx.NetworkXNoPath:
    print(f'No path between {repr(node_a)} and {repr(node_b)}')
"""

result = subprocess.run([interp, "-c", code], capture_output=True, text=True, cwd="d:/transformer")
print(result.stdout)
print(result.stderr[:300] if result.stderr else "")
```

Explain the path in plain language, then offer deeper exploration.

---

## /graphify explain

```python
import json, subprocess

interp = open("d:/transformer/graphify-out/.graphify_python").read().strip()
node_name = "NODE_NAME"

code = f"""
import json, sys
from networkx.readwrite import json_graph
from pathlib import Path

data = json.loads(Path('d:/transformer/graphify-out/graph.json').read_text())
G = json_graph.node_link_graph(data, edges='links')

term = {repr(node_name)}
term_lower = term.lower()

scored = sorted(
    [(sum(1 for w in term_lower.split() if w in G.nodes[n].get('label','').lower()) or
      sum(1 for c in term if c in G.nodes[n].get('label','')), n)
     for n in G.nodes()],
    reverse=True
)
if not scored or scored[0][0] == 0:
    print(f'No node matching {{term!r}}')
    sys.exit(0)

nid = scored[0][1]
dn = G.nodes[nid]
print(f'NODE: {{dn.get("label", nid)}}')
print(f'  source: {{dn.get("source_file","unknown")}}')
print(f'  type: {{dn.get("file_type","unknown")}}')
print(f'  degree: {{G.degree(nid)}}')
print()
print('CONNECTIONS:')
for neighbor in G.neighbors(nid):
    edge = G.edges[nid, neighbor]
    nl = G.nodes[neighbor].get('label', neighbor)
    sf = G.nodes[neighbor].get('source_file', '')
    print(f'  --{{edge.get("relation","")}}--> {{nl}} [{{edge.get("confidence","")}}] ({{sf}})')
"""

result = subprocess.run([interp, "-c", code], capture_output=True, text=True, cwd="d:/transformer")
print(result.stdout)
```

Write a 3-5 sentence explanation of what this node is, what it connects to, and why those connections matter.

---

## /graphify add

```python
import json, subprocess

interp = open("d:/transformer/graphify-out/.graphify_python").read().strip()
url = "URL"
author = None  # or "Name"
contributor = None

code = f"""
from graphify.ingest import ingest
from pathlib import Path
try:
    out = ingest({repr(url)}, Path('d:/transformer/raw'), author={repr(author)}, contributor={repr(contributor)})
    print(f'Saved to {{out}}')
except Exception as e:
    print(f'error: {{e}}')
    raise SystemExit(1)
"""

result = subprocess.run([interp, "-c", code], capture_output=True, text=True, cwd="d:/transformer")
print(result.stdout)
print(result.stderr[:300] if result.stderr else "")
```

After saving, run `/graphify d:/transformer/raw --update` to merge the new file.

---

## --watch (background monitor)

```python
import subprocess
interp = open("d:/transformer/graphify-out/.graphify_python").read().strip()
input_path = "INPUT_PATH"

print("Starting graphify watch (background)...")
proc = subprocess.Popen(
    [interp, "-m", "graphify.watch", input_path, "--debounce", "3"],
    cwd="d:/transformer",
    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
)
print(f"Watch PID: {proc.pid}")
print("Press Ctrl+C to stop.")
```

Behavior:
- Code file changes → instant AST rebuild, no LLM needed
- Doc/image changes → prints notification to run `/graphify --update`

---

## --cluster-only

Skip Steps 1-2. Load existing graph, re-cluster:

```python
import json, subprocess

interp = open("d:/transformer/graphify-out/.graphify_python").read().strip()
result = subprocess.run(
    [interp, "-c", """
import json
from graphify.cluster import cluster, score_all
from graphify.analyze import god_nodes, surprising_connections, suggest_questions
from graphify.report import generate
from graphify.export import to_json
from networkx.readwrite import json_graph
from pathlib import Path

data = json.loads(Path('d:/transformer/graphify-out/graph.json').read_text())
G = json_graph.node_link_graph(data, edges='links')

communities = cluster(G)
cohesion = score_all(G, communities)
gods = god_nodes(G)
surprises = surprising_connections(G, communities)
labels = {cid: 'Community ' + str(cid) for cid in communities}

detection = {'total_files': 0, 'total_words': 99999, 'needs_graph': True, 'warning': None,
             'files': {'code': [], 'document': [], 'paper': []}}
tokens = {'input': 0, 'output': 0}

report = generate(G, communities, cohesion, labels, gods, surprises, detection, tokens, '.')
Path('d:/transformer/graphify-out/GRAPH_REPORT.md').write_text(report)
to_json(G, communities, 'd:/transformer/graphify-out/graph.json')

analysis = {
    'communities': {str(k): v for k, v in communities.items()},
    'cohesion': {str(k): v for k, v in cohesion.items()},
    'gods': gods,
    'surprises': surprises,
}
Path('d:/transformer/graphify-out/.graphify_analysis.json').write_text(json.dumps(analysis, indent=2))
print(f'Re-clustered: {len(communities)} communities')
"""],
    capture_output=True, text=True, cwd="d:/transformer"
)
print(result.stdout)
```

Then go to Step 4 (label communities) and Step 5 (generate outputs).

---

## Honesty Rules

- Never invent an edge. If unsure → AMBIGUOUS.
- Never skip the corpus size warning.
- Always show token cost in the report.
- Never hide cohesion scores — show the raw number.
- Never generate HTML viz on graphs > 5,000 nodes without warning.
