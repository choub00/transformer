# -*- coding: utf-8 -*-
import zipfile
import xml.etree.ElementTree as ET
import re

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

def has_color(elem, target_color):
    """检查段落是否包含目标颜色"""
    for run in elem.iter(w('r')):
        color = get_run_color(run)
        if color.upper() == target_color.upper():
            return True
    return False

input_file = r'c:\Users\胡宠博\Downloads\基于transformer的股票预测系统_非黑色段落改写版.docx'
with zipfile.ZipFile(input_file, 'r') as zf:
    content = zf.read('word/document.xml').decode('utf-8')

root = ET.fromstring(content)
body = root.find(w('body'))

print('Orange (F39800) paragraphs:')
print('=' * 60)

count = 0
for para in body.iter(w('p')):
    text = get_all_text(para).strip()
    if len(text) > 20 and has_color(para, 'F39800'):
        count += 1
        print('')
        print('[' + str(count) + '] (' + str(len(text)) + ' chars)')
        print(text)
        print('-' * 40)

print('')
print('Total orange paragraphs: ' + str(count))
