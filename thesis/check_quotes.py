# -*- coding: utf-8 -*-
"""检查4个未找到段落的精确字节"""

from docx import Document

# 从原始文件（润色版）读取
INPUT = r"D:/transformer/thesis/基于transformer的股票预测系统_润色版.docx"

doc = Document(INPUT)

targets = [67, 90, 105, 153]
for idx in targets:
    para = doc.paragraphs[idx]
    text = para.text
    print(f"\n段落 {idx}:")
    print(f"  FULL: {repr(text[:200])}")
    # 找引号字节
    for i, ch in enumerate(text):
        if ch in ('"', '"', '"', '"', '"', '"'):
            print(f"  pos {i}: char={repr(ch)} ord=0x{ord(ch):04x}")
