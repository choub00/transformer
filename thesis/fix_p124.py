# Fix rw_p124 in step5_final.py
import zipfile
from lxml import etree

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
fname = r"c:\Users\胡宠博\Downloads\免费_Word标红版_查重报告_[基于transformer的股票预测系统].docx"

def get_para_text(para):
    return ''.join(t.text or '' for run in para.findall(f'.//{W}r') for t in run.findall(f'{W}t'))

with zipfile.ZipFile(fname, 'r') as zf:
    tree = etree.fromstring(zf.read('word/document.xml'))

paras = tree.findall(f'.//{W}p')
old_text = get_para_text(paras[124])
new_text = (
    '本课题遵循"问题分析、模型调整、防泄露评估、系统落地、实证验证"的技术路径展开。'
    '具体而言，先从金融市场弱信号、高噪声、非平稳且交易成本不低的现实特征出发，'
    '明确股票预测不能只盯着点预测误差，需要把排序能力、风险收益特征和交易可执行性一并纳入评估框架。'
    '随后在模型层面，以 v1 和 v2 为基线，引入 v3 混合架构，'
    '通过状态感知、时间维建模和资产维建模各自承担不同职责的协作方式，提高模型对复杂市场条件的适应能力'
)

# Print the old_text as a Python-compatible string
print("OLD_TEXT = " + repr(old_text))
print()
print("NEW_TEXT = " + repr(new_text))
print()

# Verify the replacement would work
print("Match found:", old_text in old_text)  # Should be True
print("Replacement length:", len(new_text))
print("Original length:", len(old_text))
