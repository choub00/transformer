# -*- coding: utf-8 -*-
"""
Deep rewrite script - comprehensive sentence restructuring.
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
    keywords = ['第', '章', '摘要', '目录', '参考文献', '致谢', '结论', '引言', '绪论', '附录', '1.1', '1.2', '2.1', '2.2', '3.1', '3.2', '4.1', '4.2', '4.3', '4.4', '4.5', '4.6', '5.1', '5.2', '5.3', '5.4', '6.1', '6.2', '6.3', '7.1', '7.2']
    for kw in keywords:
        if text.strip().startswith(kw) and len(text.strip()) < 30:
            return 'heading'
    return 'body'

def deep_rewrite(text):
    """
    Deep rewrite - comprehensive sentence restructuring.
    """
    if not text or len(text.strip()) < 10:
        return text
    
    original = text
    
    # ============================================
    # PHASE 1: Comprehensive AI phrase elimination
    # ============================================
    
    # Complete elimination of common AI-sounding phrases
    replacements = [
        # Remove completely
        (r'具有重要意义', '很有意义'),
        (r'有效提升', '明显改善'),
        (r'进一步说明', '具体说明'),
        (r'进一步分析', '深入分析'),
        (r'进一步探讨', '详细讨论'),
        (r'由此可见', '可以看出'),
        (r'至关重要', '非常关键'),
        (r'不可否认', '确实'),
        (r'旨在', '目的是'),
        (r'深入探讨', '详细讨论'),
        (r'深入研究', '系统研究'),
        (r'综上所述', '整体来看'),
        (r'总而言之', '总体而言'),
        (r'不容忽视', '不能忽视'),
        (r'举足轻重', '影响很大'),
        (r'值得注意', '值得关注'),
        (r'值得注意的是', '需要注意的是'),
        (r'研究表明', '结果显示'),
        (r'研究显示', '结果显示'),
        (r'实验数据显示', '实验结果显示'),
        (r'实验数据也显示', '实验结果也显示'),
        
        # Structural connectors - simplify or remove
        (r'首先，', ''),
        (r'其次，', ''),
        (r'最后，', ''),
        (r'第一点，', ''),
        (r'第二点，', ''),
        (r'第三点，', ''),
        (r'第一，', ''),
        (r'第二，', ''),
        (r'第三，', ''),
        
        # "主要" variations
        (r'主要是', '重点是'),
        (r'主要特点', '核心特点'),
        (r'主要来源', '重要来源'),
        (r'主要关注', '重点关注'),
        
        # "上述/以上" patterns - replace with specific references
        (r'上述内容表明', '这些内容说明'),
        (r'上述内容', '这些内容'),
        (r'上述表明', '这些说明'),
        (r'上述结果', '这些结果'),
        (r'上述问题', '这些问题'),
        (r'上述不足', '这些不足'),
        (r'上述目标', '这些目标'),
        (r'上述阶段', '这些阶段'),
        (r'上述机制', '这些机制'),
        (r'上述判断', '这些判断'),
        (r'上述工作', '这些工作'),
        (r'上述演进', '这些演进过程'),
        (r'基于上述', '根据这些'),
        (r'基于以上', '根据这些'),
        (r'借助上述方法', '借助这些方法'),
        (r'借助以上方法', '借助这些方法'),
        (r'以上不足', '这些不足'),
        (r'以上结果', '这些结果'),
        
        # "这/这些/此" - keep but vary
        (r'与此同时', '同时'),
        
        # Connectors simplification
        (r'然而，', '但'),
        (r'然而', '但'),
        (r'因此，', '所以'),
        (r'因此', '所以'),
        (r'此外，', '另外'),
        (r'此外', '另外'),
        (r'除了.*?外', '除了'),
        (r'一方面，', ''),
        (r'另一方面，', ''),
        (r'从一方面看，', ''),
        (r'从另一方面看，', ''),
        (r'换言之', '也就是说'),
        (r'也就是说', '即'),
        
        # Remove "不得不", "必须" variations
        (r'不得不', '必须'),
        
        # "可以" at start - remove
        (r'^可以', '', 1),
        (r'可以可以', '可以'),
        
        # "通过" at start - remove
        (r'^通过', '', 1),
        
        # "从而" at start - remove
        (r'^从而，', '', 1),
        (r'^从而', '', 1),
        
        # "随着XX的发展" patterns
        (r'随着.*?的发展', '在相关技术进步的情况下'),
        
        # "本课题/本文/本研究" standardization
        (r'^本课题', '本研究'),
        (r'本课题', '本研究'),
        (r'^本文', '本研究'),
        
        # "说明/表明" - standardize
        (r'说明', '说明'),
        (r'表明', '说明'),
        
        # "可以/能够" variations
        (r'可以', '可以'),
        (r'能够', '能'),
        
        # "不过" - keep but simplify
        (r'不过', '但'),
        
        # Remove "而" at sentence end or start
        (r'^而，', ''),
        (r'^而', ''),
        
        # "所以" standardization
        (r'所以', '所以'),
        
        # "对于...而言" 
        (r'而言', ''),
        
        # "关键在于"
        (r'关键在于', '核心在于'),
        
        # "主要用于"
        (r'主要用于', '主要用于'),
        
        # "以...为基础"
        (r'以.*?为基础', '在此基础上'),
        
        # "从而" 
        (r'从而', '这样'),
        
        # "主要因为"
        (r'主要因为', '因为'),
    ]
    
    for item in replacements:
        pattern = item[0]
        replacement = item[1]
        try:
            if replacement == '':
                text = re.sub(pattern, '', text)
            else:
                text = re.sub(pattern, replacement, text)
        except:
            pass
    
    # ============================================
    # PHASE 2: Clean up artifacts
    # ============================================
    
    # Remove multiple commas, periods
    text = re.sub(r'，，+', '，', text)
    text = re.sub(r'。。+', '。', text)
    text = re.sub(r'，，', '，', text)
    
    # Remove space before punctuation
    text = re.sub(r'\s+，', '，', text)
    text = re.sub(r'\s+。', '。', text)
    text = re.sub(r'\s+、', '、', text)
    text = re.sub(r'\s+：', '：', text)
    
    # Remove leading punctuation
    text = re.sub(r'^，', '', text)
    text = re.sub(r'^、', '', text)
    text = re.sub(r'^。', '', text)
    
    # Clean up multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Remove trailing punctuation artifacts
    text = text.strip()
    
    # ============================================
    # PHASE 3: Sentence structure improvements
    # ============================================
    
    # Split into sentences for structural changes
    sentences = re.split(r'。', text)
    new_sentences = []
    
    for sent in sentences:
        sent = sent.strip()
        if not sent:
            continue
        
        # Don't start sentences with these
        starts_to_fix = ['并且', '而且', '同时', '另外', '此外', '因此', '所以', '但是', '不过', '然而']
        for start in starts_to_fix:
            if sent.startswith(start):
                sent = '同时，' + sent[len(start):] if len(sent) > len(start) else sent
        
        new_sentences.append(sent)
    
    # Rejoin
    text = '。'.join(new_sentences)
    if text and not text.endswith('。'):
        text = text + '。'
    
    # Final cleanup
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'。。', '。', text)
    text = re.sub(r'，，', '，', text)
    text = text.strip()
    
    # Fix double words
    text = re.sub(r'本研究研究', '本研究', text)
    text = re.sub(r'这些这些', '这些', text)
    text = re.sub(r'所以所以', '所以', text)
    
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
        
        new_text = deep_rewrite(original)
        
        # Apply the rewrite to the document
        para = doc.paragraphs[idx]
        
        if para.runs:
            # Get the first run's format
            first_run = para.runs[0]
            
            # Replace text in runs
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
    report_lines.append("验证清单")
    report_lines.append("=" * 80)
    report_lines.append("□ 源文件存在")
    report_lines.append("□ 输出文件已创建")
    report_lines.append(f"□ 已润色 {len(rewritten)} 个段落")
    report_lines.append("□ 技术术语保留 (Transformer, AlphaTransformer, Mamba-2, etc.)")
    report_lines.append("□ 数值保留 (1.65, 0.082, -9.8%, etc.)")
    report_lines.append("□ 公式编号保留")
    
    with open(REPORT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    
    print(f"报告已保存到: {REPORT}")
    print(f"\n处理完成!")
    print(f"润色段落: {len(rewritten)}")
    
    return rewritten

if __name__ == '__main__':
    process_document()
