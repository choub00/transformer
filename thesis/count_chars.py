import sys
import re
sys.stdout.reconfigure(encoding='utf-8')
with open(r'd:/transformer/thesis/paper_rewritten.md', 'r', encoding='utf-8') as f:
    text = f.read()

chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
english_letters = len(re.findall(r'[a-zA-Z]', text))
english_words = len(re.findall(r'[a-zA-Z]+', text))
numbers = len(re.findall(r'\d+', text))
formula_chars = len(re.findall(r'\$.*?\$|\\\(.*?\\\)|\\\[.*?\\\]', text, re.DOTALL))

# Count by section
sections = ['第1章', '第2章', '第3章', '第4章', '第5章', '第6章', '第7章', '摘要']
section_counts = {}
current = 'Front'
section_counts[current] = 0
for line in text.split('\n'):
    found = False
    for sec in sections:
        if sec in line:
            found = True
            break
    if found:
        current = line.strip()
        section_counts[current] = 0
    else:
        section_counts[current] = section_counts.get(current, 0) + len([c for c in line if c.isalnum()])

total_chars = chinese_chars + english_letters
print(f'总字符数: {len(text)}')
print(f'中文字符数: {chinese_chars}')
print(f'英文字母数: {english_letters}')
print(f'英文单词数: {english_words}')
print(f'数字数量: {numbers}')
print(f'公式LaTeX片段数: {formula_chars}')
print(f'总计（汉字+英文字母）: {total_chars}')
print()
print('各章节字符数（汉字+英文字母）:')
for k, v in section_counts.items():
    print(f'  {k}: {v}')
