with open('d:/transformer/thesis/YZU-Thesis-Formatter/yzu_thesis_formatter.py', 'rb') as f:
    lines = f.read().split(b'\n')

for i, line in enumerate(lines, 1):
    if b'invalid character' in line or b'\xe3\x80\x82' in line:
        print('Line ' + str(i) + ': ' + repr(line))
        break

print('Line 298: ' + repr(lines[297] if len(lines) > 297 else b'not found'))