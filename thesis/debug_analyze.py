# -*- coding: utf-8 -*-
import zipfile
import xml.etree.ElementTree as ET
import re
from collections import defaultdict

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

def has_non_black_run(elem):
    for run in elem.iter(w('r')):
        color = get_run_color(run)
        if not is_black_color(color):
            return True
    return False

def is_formula_paragraph(text):
    text = text.strip()
    if re.match(r'^\([0-9]+\)\s*$', text):
        return True
    math_symbols = re.findall(r'[∫∑∏∂∇∈∉⊂⊃∪∩±×÷√∞≈≡≠≤≥]', text)
    if len(math_symbols) > 5 and len(text) < 200:
        return True
    greek = re.findall(r'[αβγδεζηθικλμνξοπρστυφχψωΑ-Ω]', text)
    if len(greek) > 10 and len(text) < 300:
        return True
    return False

def is_reference_paragraph(text):
    text = text.strip()
    if re.match(r'^\[\d+\]', text):
        return True
    if re.match(r'^\d+\.\s', text) and len(text) > 50:
        return True
    return False

def is_title_paragraph(para_elem, text):
    pPr = para_elem.find(w('pPr'))
    if pPr is not None:
        pStyle = pPr.find(w('pStyle'))
        if pStyle is not None:
            style_val = pStyle.get(w('val'), '')
            if 'Heading' in style_val or 'Title' in style_val or 'Toc' in style_val:
                return True
    text = text.strip()
    if len(text) < 50 and len(text) > 0:
        if re.match(r'^[一二三四五六七八九十]+[、.．]', text):
            return True
        if re.match(r'^\d+[.．]\s', text):
            return True
        for run in para_elem.iter(w('r')):
            rPr = run.find(w('rPr'))
            if rPr is not None:
                b = rPr.find(w('b'))
                if b is not None:
                    return True
    return False

def is_pagenumber_paragraph(text):
    text = text.strip()
    if re.match(r'^\d+$', text) and len(text) <= 4:
        return True
    return False

input_file = r'c:\Users\胡宠博\Downloads\基于transformer的股票预测系统_非黑色段落改写版.docx'
with zipfile.ZipFile(input_file, 'r') as zf:
    content = zf.read('word/document.xml').decode('utf-8')

root = ET.fromstring(content)
body = root.find(w('body'))

analysis = {
    'total': 0,
    'non_black': 0,
    'black': 0,
    'formula': 0,
    'reference': 0,
    'title': 0,
    'empty': 0,
    'pagenumber': 0,
    'to_process': [],
    'to_skip': defaultdict(list)
}

para_index = 0
for elem in body.iter(w('p')):
    text = get_all_text(elem)
    analysis['total'] += 1

    is_empty = len(text.strip()) == 0

    if is_empty:
        analysis['empty'] += 1
        analysis['to_skip']['empty'].append({'index': para_index, 'text': text[:30]})
    elif is_pagenumber_paragraph(text):
        analysis['pagenumber'] += 1
        analysis['to_skip']['pagenumber'].append({'index': para_index, 'text': text})
    elif is_title_paragraph(elem, text):
        analysis['title'] += 1
        analysis['to_skip']['title'].append({'index': para_index, 'text': text[:50]})
    elif is_formula_paragraph(text):
        analysis['formula'] += 1
        analysis['to_skip']['formula'].append({'index': para_index, 'text': text[:50]})
    elif is_reference_paragraph(text):
        analysis['reference'] += 1
        analysis['to_skip']['reference'].append({'index': para_index, 'text': text[:50]})
    elif has_non_black_run(elem):
        analysis['non_black'] += 1
        colors = set()
        for run in elem.iter(w('r')):
            color = get_run_color(run)
            if not is_black_color(color):
                colors.add(color)
        analysis['to_process'].append({
            'index': para_index,
            'text': text,
            'char_count': len(text),
            'colors': list(colors)[:3]
        })
    else:
        analysis['black'] += 1
        analysis['to_skip']['black'].append({'index': para_index, 'text': text[:50]})

    para_index += 1

print('Total paragraphs:', analysis['total'])
print('Empty:', analysis['empty'])
print('PageNumber:', analysis['pagenumber'])
print('Title:', analysis['title'])
print('Formula:', analysis['formula'])
print('Reference:', analysis['reference'])
print('Non-black:', analysis['non_black'])
print('Black:', analysis['black'])
print('To process:', len(analysis['to_process']))
print()
print('First 5 to process:')
for i, p in enumerate(analysis['to_process'][:5]):
    print('  ' + str(i+1) + '. Index ' + str(p['index']) + ', colors=' + str(p['colors']))
    print('     text=' + p['text'][:80])
