# -*- coding: utf-8 -*-
"""修复最后4个MISS - 使用Word文档中的实际字符"""

from docx import Document

INPUT  = r"D:/transformer/thesis/基于transformer的股票预测系统_降AIGC版.docx"
OUTPUT = r"D:/transformer/thesis/基于transformer/股票预测系统_降AIGC版.docx"
ORIG   = r"D:/transformer/thesis/基于transformer的股票预测系统_润色版.docx"

# 先从原始文档读取引号字符
doc_orig = Document(ORIG)
# 段落67: "预测值" 与 "交易信号"
para67_text = doc_orig.paragraphs[67].text
# 找到引号字符
for ch in para67_text:
    if ch in ('"', '"', '"', '"', chr(0x22)):
        print(f"Quote char: {repr(ch)} ord=0x{ord(ch):04x}")

# 段落90
para90_text = doc_orig.paragraphs[90].text
for ch in para90_text:
    if ch in ('"', '"', '"', '"', chr(0x22)):
        print(f"Quote char90: {repr(ch)} ord=0x{ord(ch):04x}")

# 段落105
para105_text = doc_orig.paragraphs[105].text
for ch in para105_text:
    if ch in ('"', '"', '"', '"', chr(0x22)):
        print(f"Quote char105: {repr(ch)} ord=0x{ord(ch):04x}")

# 段落153
para153_text = doc_orig.paragraphs[153].text
for ch in para153_text:
    if ch in ('"', '"', '"', '"', chr(0x22)):
        print(f"Quote char153: {repr(ch)} ord=0x{ord(ch):04x}")

print("\nFull para 67:", repr(para67_text[:100]))
print("Full para 90:", repr(para90_text[:100]))
print("Full para 105:", repr(para105_text[:80]))
print("Full para 153:", repr(para153_text[:100]))
