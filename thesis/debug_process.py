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

def academic_rewrite(text):
    if not text or len(text.strip()) < 15:
        return text

    result = text

    template_replacements = {
        '具有重要意义': '值得重视',
        '有效提升': '带来改善',
        '系统化实现': '整体完成',
        '进一步说明': '具体来看',
        '由此可见': '从这点看',
        '至关重要': '非常关键',
        '不可或缺': '不可缺少',
        '不可否认': '确实',
        '旨在': '目的是',
        '深入探讨': '详细分析',
        '综上所述': '总的来看',
        '总而言之': '简言之',
        '不容忽视': '必须关注',
        '举足轻重': '影响很大',
        '发挥着关键作用': '起到重要作用',
        '值得注意的是': '需要指出',
        '不仅如此': '另外',
        '与此同时': '同时',
        '在当今社会': '当前',
        '通过分析可以看出': '分析表明',
        '研究表明': '研究显示',
        '经过实验验证': '实验结果表明',
        '取得了良好的效果': '得到了不错的效果',
        '得到了验证': '获得验证',
        '大量实验表明': '实验结果显示',
        '可以发现': '观察发现',
        '可以看出': '从结果看',
        '因此': '所以',
        '然而': '但',
        '此外': '另外',
        '基于此': '在此基础上',
        '针对此问题': '针对这一问题',
        '为了解决': '为了处理',
        '通过大量的研究': '经过研究',
        '首先': '一',
        '其次': '二',
        '最后': '三',
    }

    for old, new in template_replacements.items():
        result = result.replace(old, new)

    result = re.sub(r'(的){2,}', lambda m: '的' * (len(m.group(0)) // 2), result)

    transition_phrases = [
        '值得注意的是，',
        '总的来看，',
        '综合来看，',
        '从整体上看，',
        '从上述分析可以看出，',
        '本文通过',
        '本文首先',
        '实际上，',
        '事实上，',
    ]
    for phrase in transition_phrases:
        if result.startswith(phrase):
            result = result[len(phrase):]

    result = re.sub(r'\s+', ' ', result)
    result = re.sub(r'\s*，\s*', '，', result)
    result = re.sub(r'\s*。\s*', '。', result)

    return result.strip()

# Reproduce the exact same logic as process_thesis_v4
input_file = r'c:\Users\胡宠博\Downloads\基于transformer的股票预测系统_非黑色段落改写版.docx'

with zipfile.ZipFile(input_file, 'r') as zf:
    all_files = zf.namelist()
    file_contents = {}
    for fname in all_files:
        file_contents[fname] = zf.read(fname)

content = file_contents['word/document.xml'].decode('utf-8')
root = ET.fromstring(content)
body = root.find(w('body'))

# Build to_process list (same as analyze_docx)
to_process = []
para_index = 0
for elem in body.iter(w('p')):
    text = get_all_text(elem)
    is_empty = len(text.strip()) == 0

    if not is_empty and not is_pagenumber_paragraph(text) and not is_title_paragraph(elem, text) and not is_formula_paragraph(text) and not is_reference_paragraph(text) and has_non_black_run(elem):
        colors = set()
        for run in elem.iter(w('r')):
            color = get_run_color(run)
            if not is_black_color(color):
                colors.add(color)
        to_process.append({
            'index': para_index,
            'text': text,
            'colors': list(colors)[:3]
        })

    para_index += 1

print('Found ' + str(len(to_process)) + ' paragraphs to process')
print('')

# Build para_list
para_list = list(body.iter(w('p')))
print('Total paragraphs in para_list: ' + str(len(para_list)))
print('')

# Process each paragraph
rewrite_results = []
processed_count = 0

for target in to_process:
    para_index = target['index']
    
    # Check bounds
    if para_index >= len(para_list):
        print('OUT OF BOUNDS: para_index ' + str(para_index) + ' >= ' + str(len(para_list)))
        continue
    
    para_elem = para_list[para_index]
    original_text = get_all_text(para_elem)
    
    if original_text and len(original_text) >= 10:
        new_text = academic_rewrite(original_text)
        
        if new_text != original_text:
            print('Para ' + str(para_index) + ': DIFFERENT')
            print('  Original (' + str(len(original_text)) + '): ' + original_text[:60])
            print('  Rewritten (' + str(len(new_text)) + '): ' + new_text[:60])
            
            # Collect text elements
            text_elements = []
            for t in para_elem.iter(w('t')):
                text_elements.append(t)

            if text_elements:
                text_elements[0].text = new_text
                for t in text_elements[1:]:
                    t.text = ''

                rewrite_results.append({
                    'index': para_index,
                    'original': original_text,
                    'new': new_text,
                })
                processed_count += 1
        else:
            print('Para ' + str(para_index) + ': SAME (no rewrite)')
            print('  Text: ' + original_text[:60])

print('')
print('Total processed: ' + str(processed_count))
