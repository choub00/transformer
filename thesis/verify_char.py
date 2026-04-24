# Verify exact character at position 4895 in step4_final.py
with open('thesis/step4_final.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Check position 4895
ch = content[4895]
print(f'Char at 4895: {ch!r} = U+{ord(ch):04X}')

# Check 4890-4905
print('\nChars 4890-4905:')
for i in range(4890, 4905):
    ch = content[i]
    print(f'  [{i}] U+{ord(ch):04X} = {ch!r}')

# Find position of rw_p120 replacement string
# Look for the pattern that starts with 围绕
idx = content.find('围绕前述目标')
print(f'\nPosition of "围绕前述目标": {idx}')
if idx >= 0:
    print('\nReplacement string chars:')
    for i in range(idx, min(idx + 100, len(content))):
        ch = content[i]
        if ord(ch) > 127 or ch == '，' or ch == '。':
            print(f'  [{i}] U+{ord(ch):04X} = {ch!r}')
