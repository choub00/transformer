import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open(r'd:/transformer/thesis/paper_final.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Mapping: old -> new
# [1] Zeng et al. 2023 (AAAI) -> [1]
# [2] Nie et al. 2023 (PatchTST) -> [2]
# [3] Liu et al. 2024 (iTransformer) -> [3]
# [4] Zeng Z et al. 2023 (CNN+TF) -> [8]
# [5] Ma et al. 2024 (Stockformer) -> [5]
# [6] Qian 2025 (IL-ETransformer) -> [11]
# [7] Vaswani 2017 -> [12]
# [8] Ridhawi 2026 (Regime-Aware) -> [7]
# [9] Ridhawi 2026 (BERT) -> [10]
# [10] Li & Cheng 2026 (WaveLSFormer) -> [5] (merged with 黄志远)
# [11] Box et al. 2015 -> [18]
# [12] Hochreiter 1997 -> [13]
# [13] Gu & Dao 2023 -> [16]
# [14] Dao & Gu 2024 -> [17]
# [15] Hamilton 1989 -> [19]
# [16] Fama & French 1993 -> [20]

# Order matters: replace longer/complex patterns first to avoid conflicts

# 1. Replace [15] (Hamilton 1989) before [1], [5]
# Actually, all are single-digit so just do simple replacements
# The patterns like "[1][4][15]" need to be handled

# Strategy: first scan for all occurrences, then do replacements
# Count all citation occurrences before replacement
all_old_refs = re.findall(r'\[(\d+(?:\]\[|\]))+\]|\[\d+\]', content)
print("Old references found:", all_old_refs[:50])

# Simple direct replacements for single citations
replacements = [
    # Simple single-ref replacements
    (r'\[15\](?=hamilton)', '[19]'),  # context: Hamilton 1989
    (r'\[16\](?=fama)', '[20]'),      # context: Fama & French
    (r'\[12\](?=hochreiter)', '[13]'),  # LSTM
    (r'\[7\](?=vaswani)', '[12]'),      # Vaswani
    # Now do context-free replacements carefully
    # Vaswani 2017 appears as [7] in text
    (r'Vaswani et al\., 2017', '【REF_7_PLACEHOLDER】'),
    # Hochreiter 1997 appears as [12] in text
    (r'Hochreiter & Schmidhuber, 1997', '【REF_12_PLACEHOLDER】'),
    # Box et al. 2015 appears as [11]
    (r'Box et al\., 2015', '【REF_11_PLACEHOLDER】'),
    # Hamilton 1989 appears as [15]
    (r'Hamilton, 1989', '【REF_15_PLACEHOLDER】'),
    # Fama & French 1993 appears as [16]
    (r'Fama & French, 1993', '【REF_16_PLACEHOLDER】'),
    # Gu & Dao 2023 appears as [13]
    (r'Gu & Dao, 2023', '【REF_13_PLACEHOLDER】'),
    # Dao & Gu 2024 appears as [14]
    (r'Dao & Gu, 2024', '【REF_14_PLACEHOLDER】'),
]

# Apply context-aware replacements
for old, new in replacements:
    count = len(re.findall(old.replace('【REF_', r'\[').replace('】', r'\]'), content)) if '【REF' in new else 0
    content_new = re.sub(old, new, content)
    if content_new != content:
        print(f"Replaced pattern '{old[:40]}...' -> '{new[:40]}...'")
    content = content_new

# Now do numeric citation replacements (in brackets)
# These must be done carefully - sort by old number descending to avoid e.g. [10] -> [5] messing up [1]
numeric_map = {
    16: 20,  # Fama & French 1993 -> [20] (done via context above)
    15: 19,  # Hamilton 1989 -> [19] (done via context above)
    14: 17,  # Dao & Gu 2024 -> [17]
    13: 16,  # Gu & Dao 2023 -> [16]
    12: 13,  # Hochreiter 1997 -> [13]
    11: 18,  # Box et al. 2015 -> [18]
    10: 10,   # Li & Cheng 2026 -> [5] (same as [5], handled specially)
    9: 10,   # Ridhawi 2026 BERT -> [10]
    8: 7,    # Ridhawi 2026 Regime -> [7]
    7: 12,   # Vaswani 2017 -> [12]
    6: 11,   # Qian 2025 -> [11]
    5: 5,    # Ma et al. 2024 -> [5] (stays as 5)
    4: 8,    # Zeng Z et al. 2023 CNN -> [8]
    3: 3,    # Liu et al. 2024 -> [3]
    2: 2,    # Nie et al. 2023 -> [2]
    1: 1,    # Zeng et al. 2023 -> [1]
}

# [10] is used both as Li & Cheng 2026 AND in [1][4][15] patterns
# Let me check what [10] appears as in text - it's "Li & Cheng, 2026" which is in WaveLSFormer context
# In the text, citations are like:
# [1] - Zeng et al. 2023 (financial time series characteristics)
# [2] - Ma et al. 2024 (quantitative practice)
# [3] - RNN/LSTM/CNN (Hochreiter)
# [4] - Vaswani
# [5] - Nie et al. 2023 (PatchTST)
# [6] - Liu et al. 2024 (iTransformer)
# [7] - Gu & Dao 2023 (Mamba)
# [8] - Dao & Gu 2024 (Mamba-2)
# [9] - Box et al. 2015
# [10] - Fama & French 1993
# [11] - Hamilton 1989
# [12] - Hochreiter 1997
# [13] - Ma et al. 2024 (Stockformer)
# [14] - Qian 2025 (IL-ETransformer)
# [15] - Li & Cheng 2026 (WaveLSFormer)
# [16] - Zeng Z et al. 2023 (CNN+TF)
# But wait - looking at the actual text citations, they're like:
# (Zeng et al., 2023) -> [1]
# (Ma et al., 2024) -> [2]
# (Vaswani et al., 2017) -> [4]
# etc.

# Let me look at the actual patterns in the text more carefully

# From the text I read:
# - (Zeng et al., 2023) appears multiple times - could be [1] or [16]
# - (Ma et al., 2024) appears multiple times - could be [2] or [5]
# - (Vaswani et al., 2017) -> [7]
# - (Nie et al., 2023) -> [2]
# - (Liu et al., 2024) -> [3]
# - (Gu & Dao, 2023) -> [13]
# - (Dao & Gu, 2024) -> [14]
# - (Hochreiter & Schmidhuber, 1997) -> [12]
# - (Box et al., 2015) -> [11]
# - (Hamilton, 1989) -> [15]
# - (Fama & French, 1993) -> [16]
# - (Qian, 2025) -> [6]
# - (Li & Cheng, 2026) -> [10]
# - (Ridhawi et al., 2026) -> [8]

# Wait, I need to re-read the text more carefully to see what exact citation keys are used
# The text uses the short form in parentheses, not the bracket numbers
# The bracket numbers are at the END of sentences

# Let me check: looking at line 22:
# "金融时间序列具有高噪声...等典型特征（Zeng et al., 2023）。"
# "在量化实践中...（Ma et al., 2024）。"
# Line 24: "(Hochreiter & Schmidhuber, 1997)" -> [12]
# "(Vaswani et al., 2017)" -> [7]
# "(Nie et al., 2023)" -> [2]
# "(Liu et al., 2024)" -> [3]
# "(Gu & Dao, 2023; Dao & Gu, 2024)" -> [13][14]
# Line 26: "(Ma et al., 2024; Qian, 2025)" -> [2][6]
# Line 30: more citations
# Line 31: "(Zeng et al., 2023)" -> [1]
# "(Ma et al., 2024)" -> [5]
# "(Qian, 2025)" -> [6]
# "(Li & Cheng, 2026)" -> [10]
# "(Ridhawi et al., 2026)" -> [8]
# "(Box et al., 2015)" -> [11]
# Line 108: "(Nie et al., 2023)" -> [2]
# Line 118: "(Liu et al., 2024)" -> [3]
# Line 122: "(Gu & Dao, 2023; Dao & Gu, 2024)" -> [13][14]
# Line 140: "(Fama & French, 1993; Hamilton, 1989)" -> [16][15]

# And the bracket numbers at end of sentences:
# Line 22: "...特征（Zeng et al., 2023）" - this is a reference, no [n] marker
# Actually, looking again at the text - the citations are in the form (Author, Year)
# NOT in the form [n]

# Wait, I see now. Looking at the text:
# - Line 22: (Zeng et al., 2023) - no [n]
# - But then I see patterns like "[1]" in the text

# Let me search for actual [digit] patterns in the text
brackets = re.findall(r'\[\d+\]', content)
print("\nBracket patterns found:")
from collections import Counter
print(Counter(brackets))
print("Total:", len(brackets))
