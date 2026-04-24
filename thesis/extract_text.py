# -*- coding: utf-8 -*-
"""Generate exact replacement script from docx text"""
import zipfile, re
from lxml import etree

INPUT_FILE = r"c:\Users\胡宠博\Downloads\免费_Word标红版_查重报告_[基于transformer的股票预测系统].docx"
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'

def get_para_text(para):
    return ''.join(t.text or '' for run in para.findall(f'.//{W}r') for t in run.findall(f'{W}t'))

with zipfile.ZipFile(INPUT_FILE, 'r') as zf:
    tree = etree.fromstring(zf.read('word/document.xml'))

paras = tree.findall(f'.//{W}p')

# Extract exact text for each paragraph
results = {}
for idx in [106, 112, 115, 120, 124, 125, 154, 174, 220, 246, 270]:
    text = get_para_text(paras[idx])
    results[idx] = text
    print(f'=== Para {idx} ===')
    print(repr(text))
    print()

# Now generate the rewrite script
print('\n\n=== GENERATED CODE ===\n')

for idx, text in results.items():
    print(f'# Para {idx}')
    print(f'old_{idx} = {repr(text)}')
    print()
