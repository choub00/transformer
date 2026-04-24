# -*- coding: utf-8 -*-
"""修复 JSON 文件中的中文引号问题"""

import json

with open("D:/transformer/thesis/rewrite_pairs.json", "r", encoding="utf-8") as f:
    content = f.read()

# 在 JSON 字符串值内部的双引号需要转义或替换
# 替换中文引号混淆ASCII引号的情况
# 这些是原文里用中文引号括起来的词，在JSON里会导致解析错误
replacements = [
    ('\u201c\u9884\u6d4b\u503c\u201d', "\u300c\u9884\u6d4b\u503c\u300d"),
    ('\u201c\u4ea4\u6613\u4fe1\u53f7\u201d', "\u300c\u4ea4\u6613\u4fe1\u53f7\u300d"),
    ('\u201c\u600e\u4e48\u8bc4\u4ef7\u201d', "\u300c\u600e\u4e48\u8bc4\u4ef7\u300d"),
    ('\u201c\u6ca1\u4ec0\u4e48\u8d8b\u52bf\u201d', "\u300c\u6ca1\u4ec0\u4e48\u8d8b\u52bf\u300d"),
]

# 查找所有内嵌的ASCII双引号模式（在JSON字符串值内部）
# 简单策略：把 "xxx" 形式的中文词替换掉
import re

# 找到所有 JSON 值字符串中的中文词被ASCII双引号包裹的情况
# 模式: 前面是中文/标点，后面是中文，中间是ASCII双引号对
lines = content.split('\n')
fixed_lines = []

for line in lines:
    # 替换 "预测值" 等中文引号包裹的词
    # \u201c = " \u201d = " (中文引号)
    # 把 JSON string value 内孤立的双引号对替换
    # 在 line 中搜索 \u201cPrediction\u201d 模式
    line = line.replace('"预测值"', '"预测值"')  # 中文双引号
    line = line.replace('"交易信号"', '"交易信号"')
    line = line.replace('"怎么评价"', '"怎么评价"')
    line = line.replace('"没什么趋势"', '"没什么趋势"')
    fixed_lines.append(line)

fixed = '\n'.join(fixed_lines)

# 验证
try:
    data = json.loads(fixed)
    print(f"Parse OK: {len(data)} items")
    with open("D:/transformer/thesis/rewrite_pairs_fixed.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print("Written to rewrite_pairs_fixed.json")
except Exception as e:
    print(f"Error: {e}")
    # 打印问题区域
    lines = fixed.split('\n')
    for i, l in enumerate(lines[25:40], 26):
        print(f"L{i}: {repr(l[:100])}")
