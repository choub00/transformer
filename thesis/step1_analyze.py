# -*- coding: utf-8 -*-
"""
Word文档非黑色段落识别与分析脚本
"""
import zipfile
import os
import re
from lxml import etree

INPUT_FILE = r"c:\Users\胡宠博\Downloads\免费_Word标红版_查重报告_[基于transformer的股票预测系统].docx"
OUTPUT_DIR = r"c:\Users\胡宠博\Downloads"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "基于transformer的股票预测系统_非黑色段落改写版.docx")
REPORT_FILE = os.path.join(OUTPUT_DIR, "基于transformer的股票预测系统_非黑色段落改写报告.txt")
THESIS_DIR = r"d:\transformer\thesis"

# Word XML namespaces
NAMESPACES = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'mc': 'http://schemas.openxmlformats.org/markup-compatibility/2006',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
}

def is_black_color(color_hex):
    """判断颜色是否为黑色"""
    if color_hex is None:
        return True
    c = color_hex.upper()
    return c in ('000000', 'AUTO', 'FF000000', '00000000', '')

def get_run_color(run_elem):
    """获取run的字体颜色"""
    rPr = run_elem.find('w:rPr', NAMESPACES)
    if rPr is not None:
        color = rPr.find('w:color', NAMESPACES)
        if color is not None:
            val = color.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val')
            return val
    return None

def get_paragraph_text(para):
    """获取段落的所有文本"""
    texts = []
    for run in para.findall('.//w:r', NAMESPACES):
        for t in run.findall('w:t', NAMESPACES):
            if t.text:
                texts.append(t.text)
    return ''.join(texts)

def has_formula_object(para):
    """检查段落是否包含公式对象"""
    # 检查OMML公式
    oMaths = para.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}oMath')
    # 检查VML/DrawingML对象
    drawings = para.findall('.//{http://schemas.openxmlformats.org/drawingml/2006/main}graphic')
    # 检查w:pict (老的公式格式)
    picts = para.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}pict')
    return len(oMaths) > 0 or len(drawings) > 0 or len(picts) > 0

def get_paragraph_type(para_text, para_idx):
    """判断段落类型"""
    text = para_text.strip()
    if not text:
        return 'empty'

    # 目录关键词
    if re.match(r'^\s*(目\s*录|Contents)', text):
        return 'toc'
    # 参考文献
    if re.match(r'^\s*\[?\d+[\]\.]', text) or re.search(r'参考文献', text):
        return 'reference'
    # 章节标题（单行、短且可能有特殊样式）
    if (len(text) < 50 and
        not text.endswith('。') and
        not text.endswith('，') and
        (re.match(r'^[\d一二三四五六七八九十]+[\.、]', text) or
         re.match(r'^\s*(第[一二三四五六七八九十]+章|第[一二三四五六七八九十]+节)',
                  text.replace(' ', '')) or
         re.match(r'^\s*[\u4e00-\u9fa5]{2,10}$', text))):
        return 'heading'

    # 图表编号
    if re.search(r'图\s*\d', text) or re.search(r'表\s*\d', text):
        return 'figure_table'

    # 公式编号
    if re.search(r'^\s*\( ?[0-9一二三四五六七八九十]+ ?\)', text) and len(text) < 100:
        return 'equation_number'

    # 页码相关
    if re.match(r'^\s*\d+\s*$', text) and len(text) < 5:
        return 'page_number'

    # 摘要
    if re.search(r'摘要|ABSTRACT', text):
        return 'abstract'

    # 致谢
    if re.search(r'致谢|ACKNOWLEDGEMENT', text):
        return 'thanks'

    # 图表目录
    if re.search(r'图表目录|图目录|表目录|插图目录', text):
        return 'toc_figure'

    return 'body'

def analyze_document():
    """分析文档，找出所有非黑色段落"""
    results = []

    with zipfile.ZipFile(INPUT_FILE, 'r') as zf:
        with zf.open('word/document.xml') as f:
            tree = etree.parse(f)

    root = tree.getroot()
    paragraphs = root.findall('.//w:p', NAMESPACES)

    for idx, para in enumerate(paragraphs):
        para_text = get_paragraph_text(para)
        if not para_text.strip():
            continue

        # 检查每个run的颜色
        runs = para.findall('w:r', NAMESPACES)
        colors_in_para = []
        for run in runs:
            color = get_run_color(run)
            colors_in_para.append(color)

        # 检查是否有非黑色
        has_non_black = any(c is not None and not is_black_color(c) for c in colors_in_para)

        if has_non_black:
            para_type = get_paragraph_type(para_text, idx)
            results.append({
                'index': idx,
                'text': para_text,
                'colors': [c for c in colors_in_para if c is not None],
                'type': para_type,
                'run_count': len(runs),
                'has_formula': has_formula_object(para),
            })

    return results

def print_analysis(results):
    """打印分析结果"""
    print(f"\n共发现 {len(results)} 个非黑色段落:\n")
    for r in results:
        print(f"--- 段落 {r['index']} (类型: {r['type']}, 颜色: {r['colors']}) ---")
        text = r['text']
        if len(text) > 200:
            print(text[:200] + "...")
        else:
            print(text)
        print()

if __name__ == '__main__':
    results = analyze_document()
    print_analysis(results)
