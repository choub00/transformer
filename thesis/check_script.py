# Check script for remaining problematic punctuation
with open('thesis/step4_final.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find rw_p120
start = content.find('def rw_p120(')
end = content.find('def rw_p', start+10)
section = content[start:end]

print(f'Para 120 section length: {len(section)}')
print(f'Fullwidth semicolons: {section.count(chr(0xFF1B))}')
print(f'Fullwidth colons: {section.count(chr(0xFF1A))}')

# Show all characters that are NOT ASCII in the section
print('\nAll non-ASCII chars in replacement strings (first 100 chars each):')
for i, ch in enumerate(section):
    if ord(ch) > 127 and ch not in ' \n\r\t(),.：；':
        ctx = section[max(0,i-5):i+20]
        print(f'  pos {i} U+{ord(ch):04X}: {repr(ch)} ... context: {repr(ctx)}')
    if i > 5000:
        break
