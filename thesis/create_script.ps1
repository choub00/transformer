# -*- coding: utf-8 -*-
import zipfile
import xml.etree.ElementTree as ET
import re

SOURCE = r'C:/Users/胡宠博/Downloads/免费_Word标红版_AIGC检测报告_[基于transformer的股票预测系统] (1).docx'

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

with zipfile.ZipFile(SOURCE, 'r') as zf:
    with zf.open('word/document.xml') as f:
        root = ET.parse(f).getroot()

body = root.find('.//w:body', NS)
total_count = 0
non_black_paragraphs = []
special_patterns = []

for idx, p in enumerate(body.findall('w:p', NS)):
    text = get_text(p)
    total_count += 1
    if not text.strip():
        continue
    runs = p.findall('.//w:r', NS)
    colors = [get_run_color(r) for r in runs]
    non_black = [c for c in colors if c and c.upper() not in ('000000','AUTO','FFFFFF',None)]
    ptype = get_para_type(text, p)
    
    if non_black or ptype in ('heading',):
        non_black_paragraphs.append({
            'idx': idx,
            'type': ptype,
            'colors': non_black,
            'text': text[:100]
        })
    
    if ptype in ('equation_label', 'toc', 'figure_table', 'reference'):
        special_patterns.append({
            'idx': idx,
            'type': ptype,
            'text': text[:100]
        })

print('Total paragraphs found: ' + str(total_count))
print('Non-black paragraphs or headings: ' + str(len(non_black_paragraphs)))
print('')
print('=== Non-black paragraphs / headings ===')
for item in non_black_paragraphs:
    print('Para #' + str(item['idx']) + ' | Type: ' + item['type'] + ' | Colors: ' + str(item['colors']) + ' | Content: ' + item['text'])

print('')
print('=== Special patterns found: ' + str(len(special_patterns)) + ' ===')
for item in special_patterns:
    print('Para #' + str(item['idx']) + ' | Type: ' + item['type'] + ' | Content: ' + item['text'])
