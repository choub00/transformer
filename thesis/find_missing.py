# -*- coding: utf-8 -*-
"""查找MISS的原文在文档中的实际内容"""

from docx import Document

INPUT = r"D:/transformer/thesis/基于transformer的股票预测系统_润色版.docx"

# 搜索关键词来找到MISS的段落
MISS_KEYWORDS = [
    "本研究目的可概括为两点",
    "预测值",
    "金融市场不是相同",
    "这些需求不是来自抽象",
    "系统由哪些层组成",
    "顺着上述模块划分",
    "嵌入 - 状态识别",
    "这样做原因很直接",
    "看似保守，其实是金融研究中最基本的因果约束",
    "预测模型研究",
    "核心在于它没有把震荡市",
]

doc = Document(INPUT)

for kw in MISS_KEYWORDS:
    print(f"\n搜索: {kw[:30]}...")
    for i, para in enumerate(doc.paragraphs):
        if kw in para.text:
            print(f"  [段落 {i}] {para.text[:120]}")
