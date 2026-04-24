# -*- coding: utf-8 -*-
import zipfile
import xml.etree.ElementTree as ET
import re

W_NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'

def w(tag):
    return '{' + W_NS + '}' + tag

def get_all_text(elem):
    texts = []
    for t in elem.iter(w('t')):
        if t.text:
            texts.append(t.text)
    return ''.join(texts)

def academic_rewrite(text):
    """对文本进行学术润色重写"""
    if not text or len(text.strip()) < 10:
        return text

    result = text

    # 1. 替换模板化表达
    template_replacements = {
        '具有重要意义': '值得重视',
        '有效提升': '带来改善',
        '系统化实现': '整体完成',
        '进一步说明': '具体来看',
        '由此可见': '从这点看',
        '至关重要': '非常关键',
        '不可或缺': '不可缺少',
        '不可否认': '确实',
        '旨在': '目的是',
        '深入探讨': '详细分析',
        '综上所述': '总的来看',
        '总而言之': '简言之',
        '不容忽视': '必须关注',
        '举足轻重': '影响很大',
        '发挥着关键作用': '起到重要作用',
        '值得注意的是': '需要指出',
        '不仅如此': '另外',
        '与此同时': '同时',
        '在当今社会': '当前',
        '通过分析可以看出': '分析表明',
        '研究表明': '研究显示',
        '经过实验验证': '实验结果表明',
        '取得了良好的效果': '得到了不错的效果',
        '得到了验证': '获得验证',
        '大量实验表明': '实验结果显示',
        '可以发现': '观察发现',
        '可以看出': '从结果看',
        '因此': '所以',
        '然而': '但',
        '此外': '另外',
        '基于此': '在此基础上',
    }

    for old, new in template_replacements.items():
        result = result.replace(old, new)

    # 2. 删除某些过渡词开头
    transition_phrases = [
        '值得注意的是，',
        '总的来看，',
        '综合来看，',
        '从整体上看，',
        '从上述分析可以看出，',
        '本文通过',
        '本文首先',
    ]
    for phrase in transition_phrases:
        if result.startswith(phrase):
            result = result[len(phrase):]

    # 3. 清理多余空格
    result = re.sub(r'\s+', ' ', result)
    result = re.sub(r'\s*，\s*', '，', result)
    result = re.sub(r'\s*。\s*', '。', result)

    return result.strip()

# Test on sample text
test_text = "本文通过分析可以看出，股票价格预测在投资研究和学术研究中具有重要意义。"
print("Original:", test_text)
print("Rewritten:", academic_rewrite(test_text))
print()

# Test another
test_text2 = "研究表明，该方法在预测精度上有效提升，具有重要意义。"
print("Original:", test_text2)
print("Rewritten:", academic_rewrite(test_text2))
