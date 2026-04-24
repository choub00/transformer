---
source_file: "d:\transformer\graphify\graphify\detect.py"
type: "code"
community: "Graphify File Detection"
location: "L11"
tags:
  - graphify/code
  - graphify/INFERRED
  - community/Graphify_File_Detection
---

# FileType

## Connections
- [[A .graphifyignore at the git repo root is included when scanning a subdir.]] - `uses` [INFERRED]
- [[A .graphifyignore in a parent directory applies to subdirectory scans.]] - `uses` [INFERRED]
- [[A .md file with enough paper signals should classify as PAPER.]] - `uses` [INFERRED]
- [[A plain .md file without paper signals should stay DOCUMENT.]] - `uses` [INFERRED]
- [[Comment lines in .graphifyignore are not treated as patterns.]] - `uses` [INFERRED]
- [[Enum]] - `inherits` [EXTRACTED]
- [[Files matching .graphifyignore patterns are excluded from detect().]] - `uses` [INFERRED]
- [[No .graphifyignore is not an error.]] - `uses` [INFERRED]
- [[The real attention paper file should be classified as PAPER.]] - `uses` [INFERRED]
- [[Upward search stops at the git repo root (.git directory).]] - `uses` [INFERRED]
- [[Video and audio file extensions should classify as VIDEO.]] - `uses` [INFERRED]
- [[Video files do not contribute to total_words.]] - `uses` [INFERRED]
- [[detect() correctly counts video files and does not add them to word count.]] - `uses` [INFERRED]
- [[detect() result always includes a 'video' key even with no video files.]] - `uses` [INFERRED]
- [[detect.py]] - `contains` [EXTRACTED]
- [[str]] - `inherits` [EXTRACTED]

#graphify/code #graphify/INFERRED #community/Graphify_File_Detection