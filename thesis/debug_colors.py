# -*- coding: utf-8 -*-
import zipfile
import xml.etree.ElementTree as ET
import re
from collections import Counter

W_NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'

def w(tag):
    return '{' + W_NS + '}' + tag

def get_all_text(elem):
    texts = []
    for t in elem.iter(w('t')):
        if t.text:
            texts.append(t.text)
    return ''.join(texts)

def get_run_color(run_elem):
    rPr = run_elem.find(w('rPr'))
    if rPr is not None:
        color_elem = rPr.find(w('color'))
        if color_elem is not None:
            val = color_elem.get(w('val'))
            if val:
                return val.upper()
    return '000000'

def is_black_color(color_val):
    if color_val is None:
        return True
    color_upper = color_val.upper().replace('#', '')
    if color_upper in ['000000', 'FF000000', 'AUTO']:
        return True
    return False

# Find all unique colors in the document
input_file = r'c:\Users\胡宠博\Downloads\基于transformer的股票预测系统_非黑色段落改写版.docx'
with zipfile.ZipFile(input_file, 'r') as zf:
    content = zf.read('word/document.xml').decode('utf-8')

root = ET.fromstring(content)
body = root.find(w('body'))

all_colors = Counter()
non_black_paras_by_color = {}

for para in body.iter(w('p')):
    text = get_all_text(para).strip()
    if len(text) > 10:
        para_colors = set()
        for run in para.iter(w('r')):
            color = get_run_color(run)
            all_colors[color] += 1
            if not is_black_color(color):
                para_colors.add(color)
        
        if para_colors:
            # Get first non-black color
            first_color = list(para_colors)[0]
            if first_color not in non_black_paras_by_color:
                non_black_paras_by_color[first_color] = []
            non_black_paras_by_color[first_color].append({
                'text': text[:100],
                'len': len(text)
            })

print('All colors found:')
for color, count in all_colors.most_common():
    print('  ' + str(color) + ': ' + str(count) + ' runs')

print('')
print('Non-black paragraphs by color:')
for color, paras in sorted(non_black_paras_by_color.items()):
    print('')
    print('Color ' + color + ' (' + str(len(paras)) + ' paragraphs):')
    for p in paras[:3]:
        print('  - [' + str(p['len']) + ' chars] ' + p['text'][:60])
    if len(paras) > 3:
        print('  ... and ' + str(len(paras) - 3) + ' more')
