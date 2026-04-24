# -*- coding: utf-8 -*-
"""找出剩余4个MISS的精确内容"""

from docx import Document

INPUT = r"D:/transformer/thesis/基于transformer的股票预测系统_润色版.docx"

doc = Document(INPUT)

# 4个MISS的关键字
for kw in ["预测值", "系统由哪些层组成", "嵌入 - 状态识别", "预测模型研究"]:
    print(f"\n=== 搜索: {kw}")
    for i, para in enumerate(doc.paragraphs):
        if kw in para.text:
            print(f"  [段落 {i}]")
            print(f"  TEXT: {repr(para.text)}")
