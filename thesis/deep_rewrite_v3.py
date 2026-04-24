# -*- coding: utf-8 -*-
"""
Improved deep rewrite script with proper English/Chinese handling.
"""
import os
import shutil
import re
from docx import Document
from docx.oxml.ns import qn

SOURCE = r"C:/Users/胡宠博/Downloads/免费_Word标红版_AIGC检测报告_[基于transformer的股票预测系统] (1).docx"
OUTPUT = r"D:/transformer/thesis/基于transformer的股票预测系统_润色版.docx"
REPORT = r"D:/transformer/thesis/润色报告_非黑色段落.txt"

def is_non_black_color(run):
    """Check if a run has non-black color"""
    try:
        rPr = run._element.find(qn('w:rPr'))
        if rPr is None:
            return False
        color = rPr.find(qn('w:color'))
        if color is None:
            return False
        val = color.get(qn('w:val'))
        if val is None:
            return False
        val_upper = val.upper()
        if val_upper in ('000000', 'AUTO', 'FFFFFF', 'BLACK'):
            return False
        return True
    except:
        return False

def is_english(text):
    """Check if text is predominantly English"""
    english_chars = sum(1 for c in text if c.isascii())
    return english_chars / len(text) > 0.5 if text else False

def get_paragraph_type(text):
    """Classify paragraph type"""
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
    if re.match(r'^Keywords:', text.strip()):
        return 'keywords'
    keywords = ['第', '章', '摘要', '目录', '参考文献', '致谢', '结论', '引言', '绪论', '附录', '1.1', '1.2', '2.1', '2.2', '3.1', '3.2', '4.1', '4.2', '4.3', '4.4', '4.5', '4.6', '5.1', '5.2', '5.3', '5.4', '6.1', '6.2', '6.3', '7.1', '7.2']
    for kw in keywords:
        if text.strip().startswith(kw) and len(text.strip()) < 30:
            return 'heading'
    return 'body'

def deep_rewrite_chinese(text):
    """
    Deep rewrite Chinese text - comprehensive restructuring.
    """
    if not text or len(text.strip()) < 10:
        return text
    
    original = text
    
    # Track if we made any changes
    changed = False
    
    # ============================================
    # PHASE 1: Complete phrase replacements
    # ============================================
    
    # AI-sounding phrases - replace completely
    phrase_replacements = [
        # Remove "具有重要意义" patterns
        (r'具有重要意义', '很有意义', 1),
        (r'具有重要的研究意义', '研究价值明显', 1),
        (r'具有重要意义和应用价值', '很有实用价值', 1),
        
        # Remove "有效提升"
        (r'有效提升', '明显改善', 1),
        (r'有效地提升', '明显改善', 1),
        
        # Remove "进一步" patterns
        (r'进一步说明', '具体说明', 1),
        (r'进一步分析', '深入分析', 1),
        (r'进一步探讨', '详细讨论', 1),
        
        # Remove "由此可见"
        (r'由此可见', '可以看出', 1),
        
        # Remove "至关重要"
        (r'至关重要', '非常关键', 1),
        
        # Remove "不可否认"
        (r'不可否认', '确实', 1),
        
        # Remove "旨在"
        (r'旨在', '目的是', 1),
        (r'本文旨在', '本论文目的是', 1),
        
        # Remove "深入探讨/深入研究"
        (r'深入探讨', '详细讨论', 1),
        (r'深入研究', '系统研究', 1),
        
        # Remove "综上所述/总而言之"
        (r'综上所述', '整体来看', 1),
        (r'总而言之', '总体而言', 1),
        
        # Remove "不容忽视"
        (r'不容忽视', '不能忽视', 1),
        
        # Remove "举足轻重"
        (r'举足轻重', '影响很大', 1),
        
        # Remove "随着XX的发展"
        (r'随着.*?的发展', '在技术进步的背景下', 1),
        
        # Remove "研究表明/研究显示"
        (r'研究表明', '结果显示', 1),
        (r'研究显示', '结果显示', 1),
        (r'实验数据显示', '实验结果显示', 1),
        (r'实验数据也显示', '实验结果也显示', 1),
        
        # Remove "值得注意"
        (r'值得注意的是', '需要注意的是', 1),
        (r'值得注意', '值得关注', 1),
        
        # Remove "表明" at end of sentence - replace with "说明"
        (r'，表明', '，说明', 1),
        (r'表明', '说明', 0),  # Global
        
        # Remove "主要" when filler
        (r'主要是', '重点是', 1),
        (r'主要特点', '核心特点', 1),
        
        # Remove "第一/第二/第三" connectors at start
        (r'^第一点，', '', 1),
        (r'^第二点，', '', 1),
        (r'^第三点，', '', 1),
        (r'^第一，', '', 1),
        (r'^第二，', '', 1),
        (r'^第三，', '', 1),
        (r'第一点，', '', 1),
        (r'第二点，', '', 1),
        (r'第三点，', '', 1),
        (r'第一，', '', 1),
        (r'第二，', '', 1),
        (r'第三，', '', 1),
        
        # Remove "首先/其次/最后"
        (r'^首先，', '', 1),
        (r'^其次，', '', 1),
        (r'^最后，', '', 1),
        (r'首先，', '', 1),
        (r'其次，', '', 1),
        (r'最后，', '', 1),
        
        # Remove "上述/以上" patterns
        (r'上述内容表明', '这些内容说明', 1),
        (r'上述内容', '这些内容', 1),
        (r'上述表明', '这些说明', 1),
        (r'上述结果', '这些结果', 1),
        (r'上述问题', '这些问题', 1),
        (r'上述不足', '这些不足', 1),
        (r'上述目标', '这些目标', 1),
        (r'上述阶段', '这些阶段', 1),
        (r'上述机制', '这些机制', 1),
        (r'上述判断', '这些判断', 1),
        (r'上述工作', '这些工作', 1),
        (r'上述演进', '这些演进', 1),
        (r'基于上述', '根据这些', 1),
        (r'基于以上', '根据这些', 1),
        (r'借助上述方法', '借助这些方法', 1),
        (r'借助以上方法', '借助这些方法', 1),
        (r'以上不足', '这些不足', 1),
        (r'以上结果', '这些结果', 1),
        
        # Remove "一方面/另一方面"
        (r'一方面，', '', 1),
        (r'另一方面，', '', 1),
        (r'从一方面看，', '', 1),
        (r'从另一方面看，', '', 1),
        
        # Simplify connectors
        (r'然而，', '但', 1),
        (r'然而', '但', 1),
        (r'因此，', '所以', 1),
        (r'因此', '所以', 1),
        (r'此外，', '另外', 1),
        (r'此外', '另外', 1),
        (r'换言之', '也就是说', 1),
        
        # Remove "不得不"
        (r'不得不', '必须', 1),
        
        # "本课题/本文" standardization
        (r'^本课题', '本研究', 1),
        (r'本课题', '本研究', 0),
        (r'^本文', '本论文', 1),
        
        # "不过" simplification
        (r'不过', '但', 0),
        
        # "从而" removal at start
        (r'^从而，', '', 1),
        (r'^从而', '', 1),
        
        # "可以/能够" at start
        (r'^可以', '', 1),
        (r'^能够', '', 1),
        
        # "通过" at start
        (r'^通过', '', 1),
        
        # "对于...而言"
        (r'而言', '', 0),
        
        # "关键在于"
        (r'关键在于', '核心在于', 1),
        
        # "主要用于"
        (r'主要用于', '主要用于', 0),
        
        # "从而"
        (r'从而', '这样', 0),
        
        # "主要因为"
        (r'主要因为', '因为', 0),
    ]
    
    for pattern, replacement, count in phrase_replacements:
        new_text = re.sub(pattern, replacement, text, count=count)
        if new_text != text:
            text = new_text
            changed = True
    
    # ============================================
    # PHASE 2: Clean up
    # ============================================
    
    # Remove double punctuation
    text = re.sub(r'，，+', '，', text)
    text = re.sub(r'。。+', '。', text)
    
    # Remove space before punctuation
    text = re.sub(r'\s+，', '，', text)
    text = re.sub(r'\s+。', '。', text)
    
    # Remove leading punctuation
    text = re.sub(r'^，', '', text)
    text = re.sub(r'^、', '', text)
    
    # Clean spaces
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    # Fix double words
    text = re.sub(r'本研究研究', '本研究', text)
    text = re.sub(r'这些这些', '这些', text)
    
    return text

def process_document():
    """Main function to process the document"""
    print("开始深度润色...")
    
    # Copy source to output
    shutil.copy2(SOURCE, OUTPUT)
    print(f"已复制源文件到: {OUTPUT}")
    
    # Load document
    doc = Document(OUTPUT)
    
    # Collect paragraphs that need rewriting
    paragraphs_to_process = []
    
    for idx, para in enumerate(doc.paragraphs):
        full_text = para.text.strip()
        if not full_text:
            continue
        
        ptype = get_paragraph_type(full_text)
        
        # Check if paragraph has non-black runs
        has_non_black = False
        for run in para.runs:
            if is_non_black_color(run):
                has_non_black = True
                break
        
        if has_non_black and ptype in ('body',):
            paragraphs_to_process.append({
                'idx': idx,
                'type': ptype,
                'original': full_text
            })
    
    print(f"发现 {len(paragraphs_to_process)} 个需要润色的段落")
    
    # Process each paragraph
    rewritten = []
    skipped = []
    
    for item in paragraphs_to_process:
        idx = item['idx']
        original = item['original']
        
        # Skip English paragraphs
        if is_english(original):
            skipped.append({
                'idx': idx,
                'reason': '英文段落，跳过',
                'text': original[:80] + '...' if len(original) > 80 else original
            })
            continue
        
        # Skip very short paragraphs
        if len(original) < 30:
            skipped.append({
                'idx': idx,
                'reason': '段落过短，跳过',
                'text': original
            })
            continue
        
        new_text = deep_rewrite_chinese(original)
        
        # If no change, skip
        if new_text == original:
            skipped.append({
                'idx': idx,
                'reason': '润色后无变化',
                'text': original[:80] + '...' if len(original) > 80 else original
            })
            continue
        
        # Apply the rewrite to the document
        para = doc.paragraphs[idx]
        
        if para.runs:
            first_run = para.runs[0]
            first_run.text = new_text
            for run in para.runs[1:]:
                run.text = ''
        
        rewritten.append({
            'idx': idx,
            'original': original,
            'rewritten': new_text,
            'orig_len': len(original),
            'new_len': len(new_text)
        })
    
    # Save document
    doc.save(OUTPUT)
    print(f"文档已保存到: {OUTPUT}")
    
    # Generate report
    report_lines = []
    report_lines.append("=" * 80)
    report_lines.append("润色报告 - 非黑色段落深度润色")
    report_lines.append("=" * 80)
    report_lines.append(f"源文件: {SOURCE}")
    report_lines.append(f"输出文件: {OUTPUT}")
    report_lines.append(f"总非黑色段落数: {len(paragraphs_to_process)}")
    report_lines.append(f"实际润色数: {len(rewritten)}")
    report_lines.append(f"跳过数: {len(skipped)}")
    report_lines.append("")
    
    report_lines.append("=" * 80)
    report_lines.append("润色详情")
    report_lines.append("=" * 80)
    
    for item in rewritten:
        report_lines.append(f"\n段落#{item['idx']}")
        report_lines.append("-" * 60)
        report_lines.append(f"【原文】({item['orig_len']}字符)")
        report_lines.append(item['original'])
        report_lines.append("")
        report_lines.append(f"【润色后】({item['new_len']}字符)")
        report_lines.append(item['rewritten'])
        report_lines.append("")
    
    if skipped:
        report_lines.append("=" * 80)
        report_lines.append("跳过段落")
        report_lines.append("=" * 80)
        for item in skipped:
            report_lines.append(f"\n段落#{item['idx']}")
            report_lines.append(f"原因: {item['reason']}")
            report_lines.append(f"内容: {item['text']}")
    
    report_lines.append("")
    report_lines.append("=" * 80)
    report_lines.append("验证清单")
    report_lines.append("=" * 80)
    report_lines.append("□ 源文件存在")
    report_lines.append("□ 输出文件已创建")
    report_lines.append(f"□ 已润色 {len(rewritten)} 个段落")
    report_lines.append(f"□ 已跳过 {len(skipped)} 个段落")
    report_lines.append("□ 技术术语保留 (Transformer, AlphaTransformer, Mamba-2, etc.)")
    report_lines.append("□ 数值保留 (1.65, 0.082, -9.8%, etc.)")
    report_lines.append("□ 公式编号保留")
    report_lines.append("□ 英文段落保留")
    
    with open(REPORT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    
    print(f"报告已保存到: {REPORT}")
    print(f"\n处理完成!")
    print(f"润色段落: {len(rewritten)}")
    print(f"跳过段落: {len(skipped)}")
    
    return rewritten, skipped

if __name__ == '__main__':
    process_document()
