import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open(r'd:/transformer/thesis/paper_final_refs.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix: Replace 'Zeng 等（2023）' bare citation in 1.2 section
# Need to find the exact line and fix it
lines = content.split('\n')
fixed = False
for i, line in enumerate(lines):
    if 'Zeng 等（2023）' in line:
        # This is the bare citation in 1.2 - replace with proper bracketed form
        # Original context: "Zeng 等（2023）指出..." -> "Zeng 等[1]指出..."
        line = line.replace('Zeng 等（2023）', 'Zeng 等[1]')
        lines[i] = line
        fixed = True
        print(f"Fixed line {i+1}: {line[:100]}")

if not fixed:
    print("WARNING: 'Zeng 等（2023）' not found - may already be fixed or text differs")

# Rebuild
content = '\n'.join(lines)

# Also check for any remaining (Author, Year) that escaped replacement
remaining_author_year = re.findall(r'[A-Z][a-z]+ [A-Z][a-z]+ et al\., \d{4}|[A-Z][a-z]+ & [A-Z][a-z]+, \d{4}|[A-Z][a-z]+, \d{4}', content)
if remaining_author_year:
    print(f"\nWARNING: Remaining (Author, Year) patterns: {set(remaining_author_year)}")
else:
    print("No remaining bare (Author, Year) patterns!")

# Verify: count all [n] brackets in body (before references section)
refs_start = content.find('## 参考文献')
body = content[:refs_start] if refs_start > 0 else content
bracket_refs = re.findall(r'\[(\d+)\]', body)
from collections import Counter
cnt = Counter(bracket_refs)
print(f"\nBody citations ({len(bracket_refs)} total):")
for k in sorted(cnt.keys(), key=lambda x: int(x)):
    print(f"  [{k}]: {cnt[k]}×")

# Check for old refs [1]-[16] in body
old_in_body = [r for r in bracket_refs if int(r) <= 16]
if old_in_body:
    print(f"\nWARNING: Old refs still in body: {set(old_in_body)}")
else:
    print("No old [1]-[16] in body - clean!")

# Count Chinese vs English in references section
refs_section = content[refs_start:] if refs_start > 0 else ''
chinese_refs = re.findall(r'[\u4e00-\u9fff]', refs_section)
english_refs = re.findall(r'[A-Z][a-z]+', refs_section)
print(f"\nReferences section: {len(chinese_refs)} Chinese chars, {len(english_refs)} English words")
cn_count = len(chinese_refs)
en_count = len([e for e in english_refs if e[0].isupper() and e[0] != 'I'])  # exclude Roman nums
print(f"  Chinese refs (estimate): {cn_count}")
print(f"  English refs (estimate): {en_count}")

with open(r'd:/transformer/thesis/paper_final_refs.md', 'w', encoding='utf-8') as f:
    f.write(content)

print("\nSaved!")
