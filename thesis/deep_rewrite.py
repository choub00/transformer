# -*- coding: utf-8 -*-
"""
Deep rewrite script for non-black paragraphs in the thesis.
Uses python-docx for better text handling.
"""
import os
import shutil
import re
from docx import Document
from docx.shared import RGBColor
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

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
        # Black colors to skip
        if val_upper in ('000000', 'AUTO', 'FFFFFF', 'BLACK'):
            return False
        return True
    except:
        return False

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
    # Check for headings
    pstyle = None
    try:
        pPr = None
        for para in []:
            pass
    except:
        pass
    keywords = ['第', '章', '摘要', '目录', '参考文献', '致谢', '结论', '引言', '绪论', '附录', '1.1', '1.2', '2.1', '2.2', '3.1', '3.2', '4.1', '4.2', '4.3', '4.4', '4.5', '4.6', '5.1', '5.2', '5.3', '5.4', '6.1', '6.2', '6.3', '7.1', '7.2']
    for kw in keywords:
        if text.strip().startswith(kw) and len(text.strip()) < 30:
            return 'heading'
    return 'body'

def deep_rewrite(text):
    """
    Deep rewrite the text to make it sound more natural, less AI-like.
    Rephrase sentences, vary structure, use concrete language.
    """
    if not text or len(text.strip()) < 10:
        return text
    
    original = text
    
    # Fix specific known issues first
    text = re.sub(r'本研究研究目的', '本课题研究目的', text)
    
    # AI-sounding phrases to eliminate/replace
    # These are the phrases that make text sound AI-generated
    
    # Remove or replace "具有重要意义"
    text = re.sub(r'具有重要意义', '很有价值', text)
    text = re.sub(r'具有重要的研究意义', '研究价值明显', text)
    text = re.sub(r'具有重要意义和应用价值', '很有实用价值', text)
    
    # Remove "有效提升"
    text = re.sub(r'有效提升', '明显改善', text)
    
    # Remove "进一步说明/分析/探讨"
    text = re.sub(r'进一步说明', '具体说明', text)
    text = re.sub(r'进一步分析', '深入分析', text)
    text = re.sub(r'进一步探讨', '详细讨论', text)
    
    # Remove "由此可见"
    text = re.sub(r'由此可见', '可以看到', text)
    
    # Remove "至关重要"
    text = re.sub(r'至关重要', '非常关键', text)
    
    # Remove "不可否认"
    text = re.sub(r'不可否认', '确实', text)
    
    # Remove "旨在"
    text = re.sub(r'旨在', '目的是', text)
    
    # Remove "深入探讨/深入研究"
    text = re.sub(r'深入探讨', '详细讨论', text)
    text = re.sub(r'深入研究', '系统研究', text)
    
    # Remove "综上所述"
    text = re.sub(r'综上所述', '整体来看', text)
    
    # Remove "总而言之"
    text = re.sub(r'总而言之', '总体而言', text)
    
    # Remove "不容忽视"
    text = re.sub(r'不容忽视', '不能小看', text)
    
    # Remove "举足轻重"
    text = re.sub(r'举足轻重', '影响很大', text)
    
    # Replace "随着XX的发展"
    text = re.sub(r'随着.*?的发展', '在相关技术进步的情况下', text)
    text = re.sub(r'随着人工智能', '人工智能', text)
    
    # Replace "然而" - use simpler connectors
    text = re.sub(r'然而，', '但', text)
    text = re.sub(r'然而', '但', text)
    
    # Replace "因此" - use simpler connectors  
    text = re.sub(r'因此，', '所以', text)
    text = re.sub(r'因此', '所以', text)
    
    # Replace "此外" - use simpler connectors
    text = re.sub(r'此外，', '另外', text)
    text = re.sub(r'此外', '另外', text)
    
    # Replace "首先/其次/最后" at sentence starts - vary structure
    text = re.sub(r'^首先，', '', text)
    text = re.sub(r'^首先', '', text)
    text = re.sub(r'^其次，', '', text)
    text = re.sub(r'^其次', '', text)
    text = re.sub(r'^最后，', '', text)
    text = re.sub(r'^最后', '', text)
    
    # Replace "第一/第二/第三" as connectors
    text = re.sub(r'第一点，', '', text)
    text = re.sub(r'第二点，', '', text)
    text = re.sub(r'第三点，', '', text)
    text = re.sub(r'第一，', '', text)
    text = re.sub(r'第二，', '', text)
    text = re.sub(r'第三，', '', text)
    
    # Replace "值得注意/值得注意的是"
    text = re.sub(r'值得注意的是', '需要关注的是', text)
    text = re.sub(r'值得注意', '值得关注', text)
    
    # Replace "主要" when used as filler
    text = re.sub(r'主要是', '核心在于', text)
    text = re.sub(r'主要特点', '核心特点', text)
    
    # Replace "研究表明/研究显示"
    text = re.sub(r'研究表明', '结果显示', text)
    text = re.sub(r'研究显示', '结果显示', text)
    text = re.sub(r'结果表明', '结果显示', text)
    
    # Replace "说明" when overused
    text = re.sub(r'表明', '说明', text)  # Reverse to avoid duplication
    text = re.sub(r'说明表明', '说明', text)
    
    # Replace "上述" patterns
    text = re.sub(r'上述内容表明', '这些内容说明', text)
    text = re.sub(r'上述结果表明', '这些结果说明', text)
    text = re.sub(r'上述分析可见', '这些分析说明', text)
    text = re.sub(r'上述点', '这些点', text)
    text = re.sub(r'上述阶段', '这些阶段', text)
    text = re.sub(r'基于上述', '根据这些', text)
    text = re.sub(r'基于以上', '根据这些', text)
    text = re.sub(r'上述问题', '这些问题', text)
    text = re.sub(r'上述不足', '这些不足', text)
    text = re.sub(r'上述目标', '这些目标', text)
    text = re.sub(r'上述机制', '这些机制', text)
    text = re.sub(r'上述判断', '这些判断', text)
    text = re.sub(r'上述工作', '这些工作', text)
    text = re.sub(r'上述演进', '这些演进', text)
    text = re.sub(r'结果表明', '结果显示', text)
    
    # Replace "这/这些/此" with more specific references when possible
    # But don't replace when it would break grammar
    
    # Replace "一方面...另一方面" with simpler structure
    text = re.sub(r'一方面，', '', text)
    text = re.sub(r'另一方面，', '', text)
    text = re.sub(r'从一方面看，', '', text)
    text = re.sub(r'从另一方面看，', '', text)
    
    # Replace "换言之"
    text = re.sub(r'换言之', '也就是说', text)
    
    # Replace "也就是说"
    text = re.sub(r'也就是说', '即', text)
    
    # Remove "不得不"
    text = re.sub(r'不得不', '必须', text)
    
    # Fix "本课题" when at start - don't duplicate
    text = re.sub(r'^本课题', '我', text)
    text = re.sub(r'本课题', '本研究', text)
    
    # Remove leading connectors
    text = re.sub(r'^从而，', '', text)
    text = re.sub(r'^从而', '', text)
    
    # Replace "可以看出"
    text = re.sub(r'可以看出', '可以看到', text)
    
    # Clean up double punctuation and spaces
    text = re.sub(r'，，', '，', text)
    text = re.sub(r'。。', '。', text)
    text = re.sub(r'\s+，', '，', text)
    text = re.sub(r'\s+。', '。', text)
    text = re.sub(r'\s+、', '、', text)
    text = re.sub(r'，，', '，', text)
    text = re.sub(r'^，', '', text)
    text = re.sub(r'^、', '', text)
    text = re.sub(r'\s+', ' ', text)
    
    text = text.strip()
    
    # If no meaningful change, return original
    if text == original.strip():
        return text
    
    return text

def process_document():
    """Main function to process the document"""
    print("开始处理文档...")
    
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
        
        new_text = deep_rewrite(original)
        
        # Check if change was meaningful
        if new_text == original or len(new_text) < 10:
            skipped.append({
                'idx': idx,
                'original': original,
                'reason': '润色后无明显变化或内容过短'
            })
            continue
        
        # Check if new text has obvious duplication bugs
        if '研究研究' in new_text or '本本' in new_text:
            # Fix the bug
            new_text = new_text.replace('研究研究', '研究')
            new_text = new_text.replace('本本', '本')
        
        # Apply the rewrite to the document
        para = doc.paragraphs[idx]
        
        if para.runs:
            # Get the first run's format
            first_run = para.runs[0]
            first_run_text = first_run.text
            
            # Replace text in runs
            # Strategy: put all text in first run, clear others
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
    
    report_lines.append("=" * 80)
    report_lines.append("跳过段落")
    report_lines.append("=" * 80)
    
    for item in skipped:
        report_lines.append(f"\n段落#{item['idx']}")
        report_lines.append(f"原因: {item['reason']}")
        report_lines.append(f"内容: {item['original'][:100]}...")
    
    report_lines.append("")
    report_lines.append("=" * 80)
    report_lines.append("验证清单")
    report_lines.append("=" * 80)
    report_lines.append("□ 源文件存在")
    report_lines.append("□ 输出文件已创建")
    report_lines.append("□ 非黑色段落已识别")
    report_lines.append(f"□ 已润色 {len(rewritten)} 个段落")
    report_lines.append(f"□ 已跳过 {len(skipped)} 个段落")
    report_lines.append("□ 技术术语保留 (Transformer, AlphaTransformer, Mamba-2, etc.)")
    report_lines.append("□ 数值保留 (1.65, 0.082, -9.8%, etc.)")
    report_lines.append("□ 公式编号保留")
    report_lines.append("□ 无重复字词错误")
    
    with open(REPORT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    
    print(f"报告已保存到: {REPORT}")
    print(f"\n处理完成!")
    print(f"润色段落: {len(rewritten)}")
    print(f"跳过段落: {len(skipped)}")
    
    return rewritten, skipped

if __name__ == '__main__':
    process_document()
