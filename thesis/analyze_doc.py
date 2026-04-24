# -*- coding: utf-8 -*-
import zipfile
import xml.etree.ElementTree as ET
import re
import os

SOURCE = r"C:/Users/胡宠博/Downloads/免费_Word标红版_AIGC检测报告_[基于transformer的股票预测系统] (1).docx"
OUT_DIR = r"D:/transformer/thesis"
os.makedirs(OUT_DIR, exist_ok=True)

NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

def get_run_color(run_elem):
    rPr = run_elem.find('w:rPr', NS)
    if rPr is None:
        return None
    c = rPr.find('w:color', NS)
    if c is None:
        return None
    return c.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val')

def get_text(para):
    return ''.join(t.text or '' for t in para.findall('.//w:t', NS))

def get_para_type(text, para):
    if not text.strip():
        return 'empty'
    if re.match(r'^\s*\([0-9IVXivx]+\)\s*$', text.strip()):
        return 'equation_label'
    if '...' in text:
        return 'toc'
    if re.match(r'^(图|表)\s*[0-9]+', text.strip()):
        return 'figure_table'
    if re.match(r'^\[[0-9]+\]', text.strip()):
        return 'reference'
    pStyle = para.find('w:pPr/w:pStyle', NS)
    if pStyle is not None:
        sv = pStyle.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val','')
        if 'Heading' in sv or 'Title' in sv:
            return 'heading'
    kw = ['第', '章', '摘要', '目录', '参考文献', '致谢', '结论', '引言', '绪论', '附录']
    if any(text.strip().startswith(k) for k in kw):
        return 'heading'
    if para.find('w:pPr/w:numPr', NS) is not None:
        return 'list_item'
    return 'body'

results = []
with zipfile.ZipFile(SOURCE, 'r') as zf:
    with zf.open('word/document.xml') as f:
        root = ET.parse(f).getroot()

body = root.find('.//w:body', NS)
for idx, p in enumerate(body.findall('w:p', NS)):
    text = get_text(p)
    if not text.strip():
        continue
    runs = p.findall('.//w:r', NS)
    colors = [get_run_color(r) for r in runs]
    non_black = [c for c in colors if c and c.upper() not in ('000000','AUTO','FFFFFF')]
    ptype = get_para_type(text, p)
    
    if non_black:
        results.append({
            'idx': idx,
            'type': ptype,
            'colors': non_black,
            'text': text,
            'chars': len(text)
        })
        print(f"Para#{idx}|type={ptype}|colors={non_black}|chars={len(text)}")
        print(f"  TEXT: {text[:150]}")
        print()

print(f"\nTOTAL non-black paragraphs: {len(results)}")
