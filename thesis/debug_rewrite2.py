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
    for run in elem.iter(w('r')):
        color = get_run_color(run)
        if color.upper() == target_color.upper():
            return True
    return False

def academic_rewrite_v2(text):
    """更激进的学术润色重写"""
    if not text or len(text.strip()) < 20:
        return text

    result = text.strip()

    # 1. 模板化表达替换
    replacements = {
        # 降低重要性的夸张表达
        '具有重要意义': '值得研究',
        '有效提升': '有所改善',
        '系统化实现': '整体完成',
        '进一步说明': '具体来说',
        '由此可见': '从这点看',
        '至关重要': '很关键',
        '不可或缺': '不可缺少',
        '不可否认': '确实',
        '旨在': '目的是',
        '深入探讨': '详细分析',
        '综上所述': '总的来说',
        '总而言之': '简言之',
        '不容忽视': '必须关注',
        '举足轻重': '影响较大',
        '发挥着关键作用': '起到重要作用',
        
        # 过渡词简化
        '值得注意的是': '需要指出',
        '不仅如此': '另外',
        '与此同时': '同时',
        '在当今社会': '当前',
        '通过分析可以看出': '分析表明',
        '研究表明': '研究显示',
        '经过实验验证': '实验结果表明',
        '取得了良好的效果': '取得了一定效果',
        '得到了验证': '获得验证',
        '大量实验表明': '实验结果显示',
        '可以发现': '观察发现',
        '可以看出': '从结果看',
        '因此': '所以',
        '然而': '但',
        '此外': '另外',
        '基于此': '在此基础上',
        
        # 减少"的"的过度使用
        '这一': '这',
        '这些': '这些',
        '该': '这',
        
        # 简化开头
        '实际上，': '',
        '事实上，': '',
        '首先，': '',
        '其次，': '',
        '最后，': '',
    }

    for old, new in replacements.items():
        result = result.replace(old, new)

    # 2. 删除句首的过渡词
    lead_phrases = ['值得注意的是，', '总的来看，', '综合来看，', '从整体上看，', 
                   '从上述分析可以看出，', '本文通过', '本文首先', '实际上，', '事实上，']
    for phrase in lead_phrases:
        if result.startswith(phrase):
            result = result[len(phrase):]

    # 3. 如果结果没有变化，尝试拆分长句
    if result == text.strip() and len(result) > 80:
        # 找分号拆句
        parts = result.split('；')
        if len(parts) > 1:
            # 重组句子顺序
            new_parts = parts[1:] + parts[:1]
            result = '。'.join([p.strip() for p in new_parts if p.strip()]) + '。'

    # 4. 清理标点和空格
    result = re.sub(r'\s+', ' ', result)
    result = re.sub(r'\s*，\s*', '，', result)
    result = re.sub(r'\s*。\s*', '。', result)

    return result

# 测试橙色段落
input_file = r'c:\Users\胡宠博\Downloads\基于transformer的股票预测系统_非黑色段落改写版.docx'
with zipfile.ZipFile(input_file, 'r') as zf:
    content = zf.read('word/document.xml').decode('utf-8')

root = ET.fromstring(content)
body = root.find(w('body'))

print('Testing rewrite on orange (F39800) paragraphs:')
print('=' * 60)

count = 0
for para in body.iter(w('p')):
    text = get_all_text(para).strip()
    if len(text) > 30 and has_color(para, 'F39800'):
        count += 1
        new_text = academic_rewrite_v2(text)
        changed = text != new_text
        
        print('')
        print('[' + str(count) + '] Changed: ' + str(changed))
        print('Original (' + str(len(text)) + '): ' + text[:80])
        print('Rewritten (' + str(len(new_text)) + '): ' + new_text[:80])
        if changed:
            print('DIFF: ' + text[:60] + ' -> ' + new_text[:60])

print('')
print('Total orange paragraphs: ' + str(count))
