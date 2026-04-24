# -*- coding: utf-8 -*-
"""查找4个MISS在当前文档中的实际内容"""

from docx import Document

INPUT = r"D:/transformer/thesis/基于transformer的股票预测系统_降AIGC版.docx"
doc = Document(INPUT)

targets = [
    ("不能一直光用", "第6项"),
    ("这一个东西不是简单", "第9项"),
    ("不是往上面加几个新模块", "第10项"),
    ("比如说训练和回测", "第12项"),
]

for kw, label in targets:
    print(f"\n=== {label}: {kw}")
    for i, para in enumerate(doc.paragraphs):
        if kw in para.text:
            print(f"  [段落 {i}] {para.text[:120]}")
            break
    else:
        # 尝试部分匹配
        for i, para in enumerate(doc.paragraphs):
            for word in kw.split()[:3]:
                if word in para.text:
                    print(f"  [段落 {i}] {para.text[:120]}")
                    break
            else:
                continue
            break
