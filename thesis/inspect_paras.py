# -*- coding: utf-8 -*-
"""直接从docx提取段落文本，构建精确的替换"""

from docx import Document

INPUT = r"D:/transformer/thesis/基于transformer的股票预测系统_降AIGC版.docx"

doc = Document(INPUT)

# 直接从文档提取段落
targets = {
    67: ("现象说明", "说明"),
    90: ("系统由哪些层组成", "分层结构"),
    105: ("嵌入 - 状态识别", "嵌入"),
    153: ("正是这套指标结构", "指标结构"),
}

for idx, (kw, tag) in targets.items():
    para = doc.paragraphs[idx]
    print(f"\n段落 {idx} [{tag}]:")
    print(f"  LEN: {len(para.text)}")
    print(f"  TEXT[0:120]: {para.text[:120]}")

    # 检查引号字符
    for i, ch in enumerate(para.text):
        if ord(ch) > 127 and ch not in '，。、；：？！""''（）【】《》—…·':
            if i < 5 or i > len(para.text)-5:
                continue
        if ch in '""«»「」『』':
            print(f"  QUOTE pos={i} char={repr(ch)} U+{ord(ch):04X}")
