# -*- coding: utf-8 -*-
"""Debug which rewrite functions actually fired"""
import zipfile
import re
from lxml import etree

INPUT_FILE = r"c:\Users\胡宠博\Downloads\免费_Word标红版_查重报告_[基于transformer的股票预测系统].docx"

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
NAMESPACES = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

def get_paragraph_text(para):
    texts = []
    for run in para.findall(f'.//{W}r'):
        for t in run.findall(f'{W}t'):
            if t.text:
                texts.append(t.text)
    return ''.join(texts)

def is_black_color(color_hex):
    if color_hex is None:
        return True
    return color_hex.upper() in ('000000', 'AUTO', 'FF000000', '00000000', '')

def get_run_color(run_elem):
    rPr = run_elem.find(f'{W}rPr')
    if rPr is not None:
        color = rPr.find(f'{W}color')
        if color is not None:
            return color.get(f'{W}val')
    return None

with zipfile.ZipFile(INPUT_FILE, 'r') as zf:
    doc_xml = zf.read('word/document.xml')

parser = etree.XMLParser(remove_blank_text=False, encoding='utf-8')
tree = etree.fromstring(doc_xml, parser)
paragraphs = tree.findall(f'.//{W}p')

TARGET_IDXS = [18, 22, 33, 34, 65, 86, 106, 112, 115, 120, 124, 125, 154, 174, 220, 246, 270]

for idx, para in enumerate(paragraphs):
    if idx not in TARGET_IDXS:
        continue
    runs = para.findall(f'{W}r')
    if not runs:
        continue
    text = get_paragraph_text(para)
    if not text.strip():
        continue
    colors = [get_run_color(r) for r in runs]
    has_non_black = any(c is not None and not is_black_color(c) for c in colors)
    if has_non_black:
        print(f"\n===== 段落 {idx} =====")
        print(f"颜色: {colors}")
        print(f"文本:\n{text}")
        print(f"\n字符码:")
        # 显示特殊字符
        for i, ch in enumerate(text):
            if ord(ch) > 127:
                print(f"  [{i}] '{ch}' = U+{ord(ch):04X}")
