# -*- coding: utf-8 -*-
import zipfile
import xml.etree.ElementTree as ET
import re
import os
import shutil

SOURCE = r"C:/Users/胡宠博/Downloads/免费_Word标红版_AIGC检测报告_[基于transformer的股票预测系统] (1).docx"
OUTPUT = r"D:/transformer/thesis/基于transformer的股票预测系统_润色版.docx"
REPORT = r"D:/transformer/thesis/润色报告_非黑色段落.txt"
os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)

NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
NS_URI = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'

def get_run_color(run_elem):
    rPr = run_elem.find('w:rPr', NS)
    if rPr is None:
        return None
    c = rPr.find('w:color', NS)
    if c is None:
        return None
    return c.get(f'{{{NS_URI}}}val')

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
        sv = pStyle.get(f'{{{NS_URI}}}val','')
        if 'Heading' in sv or 'Title' in sv:
            return 'heading'
    kw = ['第', '章', '摘要', '目录', '参考文献', '致谢', '结论', '引言', '绪论', '附录']
    if any(text.strip().startswith(k) for k in kw):
        return 'heading'
    if para.find('w:pPr/w:numPr', NS) is not None:
        return 'list_item'
    return 'body'

# Expanded rewrite rules - more comprehensive patterns
REWRITE_RULES = [
    # AI-sounding connectors and transitions
    (r'研究表明', '结果显示'),
    (r'研究表明，', '结果显示，'),
    (r'研究显示', '结果显示'),
    (r'研究表明', '结果显示'),
    
    # Avoid "上述" overuse - vary expression
    (r'上述内容表明', '这些内容说明'),
    (r'上述结果表明', '这些结果表明'),
    (r'上述分析可见', '这些分析说明'),
    (r'上述', '这些'),
    
    # Avoid "主要是" overuse
    (r'主要是', '核心在于'),
    (r'主要特点', '核心特点'),
    
    # Avoid "一方面...另一方面" pattern
    (r'一方面，', '从一方面看，'),
    (r'另一方面，', '从另一方面看，'),
    
    # Avoid "第一/第二/第三" as connectors
    (r'第一点，', '首先，'),
    (r'第二点，', '其次，'),
    (r'第三点，', '再次，'),
    (r'第一，', '首先，'),
    (r'第二，', '其次，'),
    (r'第三，', '再次，'),
    
    # Avoid "从而" at sentence start
    (r'^从而，', '', 1),
    
    # Avoid "可以看出"
    (r'可以看出', '可以看到'),
    
    # Avoid "值得注意"
    (r'值得注意', '值得关注'),
    (r'值得注意的是', '需要指出的是'),
    
    # Avoid "说明" overuse
    (r'说明', '表明'),
    
    # Avoid "意味着"
    (r'意味着', '意味着'),
    
    # Avoid "可以" at sentence start
    (r'^可以', '', 1),
    
    # Avoid "通过" at sentence start
    (r'^通过', '', 1),
    
    # Avoid "本文" at start
    (r'^本课题', '本研究'),
    (r'^本论文', '本研究'),
    
    # Avoid "因此" 
    (r'因此，', '所以，'),
    (r'因此', '所以'),
    
    # Avoid "然而" 
    (r'然而，', '但，'),
    (r'然而', '但'),
    
    # Avoid "此外"
    (r'此外，', '另外，'),
    (r'此外', '另外'),
    
    # Avoid "综上所述"
    (r'综上所述', '整体来看'),
    
    # Avoid "总而言之"
    (r'总而言之', '整体而言'),
    
    # Avoid "换言之"
    (r'换言之', '也就是说'),
    
    # Avoid "也就是说"
    (r'也就是说', '即'),
    
    # Avoid "不得不"
    (r'不得不', '必须'),
    
    # Avoid "具有重要意义"
    (r'具有重要意义', '意义重大'),
    
    # Avoid "至关重要"
    (r'至关重要', '十分关键'),
    
    # Avoid "不可否认"
    (r'不可否认', '确实'),
    
    # Avoid "深入探讨/深入研究"
    (r'深入探讨', '详细讨论'),
    (r'深入研究', '系统研究'),
    
    # Avoid "旨在"
    (r'旨在', '目的是'),
    
    # Avoid "有效提升"
    (r'有效提升', '显著改善'),
    
    # Avoid "进一步" starters
    (r'进一步说明', '具体说明'),
    (r'进一步分析', '深入分析'),
    (r'进一步探讨', '详细讨论'),
    
    # Avoid "不容忽视"
    (r'不容忽视', '不可小觑'),
    
    # Avoid "举足轻重"
    (r'举足轻重', '影响很大'),
    
    # Avoid "从...角度看" pattern
    (r'从.*?角度看', ''),
    
    # Avoid "对于...而言"
    (r'而言', ''),
]

def rewrite_text(text):
    """Apply rewrite rules to make text more natural"""
    original = text
    
    for rule in REWRITE_RULES:
        pattern = rule[0]
        replacement = rule[1]
        if len(rule) > 2:
            count = rule[2]
        else:
            count = 0
        
        if count == 1:
            text = re.sub(pattern, replacement, text, count=1)
        else:
            text = re.sub(pattern, replacement, text)
    
    # Clean up
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\s+，', '，', text)
    text = re.sub(r'\s+。', '。', text)
    text = re.sub(r'，，', '，', text)
    text = re.sub(r'。。', '。', text)
    text = re.sub(r'^，', '', text)
    text = re.sub(r'^。', '', text)
    
    return text.strip()

def analyze_document():
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
    
    return results

def update_paragraph_text(para_elem, new_text):
    """Update all w:t elements in a paragraph with new text"""
    t_elements = para_elem.findall('.//w:t', NS)
    if t_elements:
        t_elements[0].text = new_text
        for t in t_elements[1:]:
            t.text = ''

def rewrite_document():
    """Main function to rewrite the document"""
    # Copy source to output
    shutil.copy2(SOURCE, OUTPUT)
    
    # Analyze first
    paragraphs = analyze_document()
    
    rewritten = []
    skipped = []
    report_lines = []
    
    report_lines.append("=" * 80)
    report_lines.append("润色报告 - 非黑色段落改写")
    report_lines.append("=" * 80)
    report_lines.append(f"源文件: {SOURCE}")
    report_lines.append(f"输出文件: {OUTPUT}")
    report_lines.append(f"总非黑色段落数: {len(paragraphs)}")
    report_lines.append("")
    
    # Read document.xml
    with zipfile.ZipFile(OUTPUT, 'r') as zf:
        xml_content = zf.read('word/document.xml')
    
    root = ET.fromstring(xml_content)
    body = root.find('.//w:body', NS)
    para_elements = body.findall('w:p', NS)
    
    # Process each paragraph
    for para_info in paragraphs:
        idx = para_info['idx']
        ptype = para_info['type']
        original_text = para_info['text']
        
        # Skip non-content paragraphs
        if ptype in ('heading', 'reference', 'figure_table', 'equation_label', 'empty', 'toc'):
            skipped.append({
                'idx': idx,
                'type': ptype,
                'reason': f'类型为{ptype}，跳过',
                'text': original_text[:80] + '...' if len(original_text) > 80 else original_text
            })
            continue
        
        # For body and list_item paragraphs, attempt rewrite
        if ptype in ('body', 'list_item'):
            new_text = rewrite_text(original_text)
            
            if new_text == original_text or len(new_text) < 10:
                skipped.append({
                    'idx': idx,
                    'type': ptype,
                    'reason': '未检测到需要改写的AI用语',
                    'text': original_text[:80] + '...' if len(original_text) > 80 else original_text
                })
                continue
            
            # Replace text in XML
            para_elem = para_elements[idx]
            update_paragraph_text(para_elem, new_text)
            
            rewritten.append({
                'idx': idx,
                'type': ptype,
                'original': original_text,
                'rewritten': new_text
            })
    
    # Write modified XML back
    modified_xml = ET.tostring(root, encoding='unicode')
    
    # Update the zip file
    temp_path = OUTPUT + '.tmp'
    with zipfile.ZipFile(OUTPUT, 'r') as zin:
        with zipfile.ZipFile(temp_path, 'w', zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                if item.filename == 'word/document.xml':
                    zout.writestr(item, modified_xml.encode('utf-8'))
                else:
                    zout.writestr(item, zin.read(item.filename))
    
    os.replace(temp_path, OUTPUT)
    
    # Generate report
    report_lines.append("=" * 80)
    report_lines.append("改写统计")
    report_lines.append("=" * 80)
    report_lines.append(f"实际改写段落数: {len(rewritten)}")
    report_lines.append(f"跳过段落数: {len(skipped)}")
    report_lines.append("")
    
    report_lines.append("=" * 80)
    report_lines.append("改写详情")
    report_lines.append("=" * 80)
    
    for item in rewritten:
        report_lines.append(f"\n段落#{item['idx']} (类型: {item['type']})")
        report_lines.append("-" * 40)
        report_lines.append("【原文】")
        report_lines.append(item['original'])
        report_lines.append("")
        report_lines.append("【改写后】")
        report_lines.append(item['rewritten'])
        report_lines.append("")
    
    report_lines.append("=" * 80)
    report_lines.append("跳过段落")
    report_lines.append("=" * 80)
    
    for item in skipped:
        report_lines.append(f"\n段落#{item['idx']} (类型: {item['type']})")
        report_lines.append(f"跳过原因: {item['reason']}")
        report_lines.append(f"内容: {item['text']}")
    
    report_lines.append("")
    report_lines.append("=" * 80)
    report_lines.append("验证清单")
    report_lines.append("=" * 80)
    report_lines.append("□ 源文件存在")
    report_lines.append("□ 输出文件已创建")
    report_lines.append("□ 非黑色段落已识别")
    report_lines.append(f"□ 已改写 {len(rewritten)} 个段落")
    report_lines.append(f"□ 已跳过 {len(skipped)} 个段落")
    report_lines.append("□ 标点符号保留")
    report_lines.append("□ 技术术语保留 (Transformer, AlphaTransformer, Mamba-2, etc.)")
    report_lines.append("□ 数值保留 (1.65, 0.082, -9.8%, etc.)")
    report_lines.append("□ 公式编号保留")
    
    # Write report
    with open(REPORT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    
    print(f"处理完成!")
    print(f"改写段落: {len(rewritten)}")
    print(f"跳过段落: {len(skipped)}")
    print(f"输出文件: {OUTPUT}")
    print(f"报告文件: {REPORT}")
    
    return rewritten, skipped

if __name__ == '__main__':
    rewrite_document()
