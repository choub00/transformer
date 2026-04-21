# -*- coding: utf-8 -*-
"""
河北金融学院论文格式转换脚本
将论文重写稿按照学校格式规范进行调整
"""

import re
from pathlib import Path

# 文件路径
SOURCE_FILE = r"C:\Users\胡宠博\Desktop\论文\论文重写稿.md"
OUTPUT_FILE = r"C:\Users\胡宠博\Desktop\论文\论文重写稿_河北金融学院格式.md"


def convert_format(content: str) -> str:
    """
    执行格式转换 - 按照河北金融学院格式规范

    格式规范：
    - 一级标题: ## 第X章 标题 (中文数字)
    - 二级标题: ### X. 标题 (阿拉伯数字点号)
    - 三级标题: #### X. 标题 (阿拉伯数字点号)
    """

    # 转换二级标题: ### （一） -> ### 1.
    chinese_nums = {
        '一': '1', '二': '2', '三': '3', '四': '4', '五': '5',
        '六': '6', '七': '7', '八': '8', '九': '9', '十': '10'
    }

    # 匹配并替换中文括号序号为阿拉伯数字
    for cn, ar in chinese_nums.items():
        # 二级标题
        content = re.sub(f'### （{cn}）', f'### {ar}.', content)
        # 三级标题
        content = re.sub(f'#### （{cn}）', f'#### {ar}.', content)

    # 规范化章节分隔线
    # 确保章节标题后有分隔线
    pattern_chapter = r'(## 第[一二三四五六七八九十]+章 .+)\n(?!---)'
    content = re.sub(pattern_chapter, r'\1\n\n---\n\n', content)

    # 添加论文封面信息（在标题后）
    cover_info = """

**姓名**：胡宠博　**学号**：20221216032013　**院系**：金融科技学院
**专业**：人工智能　**指导教师**：刘冲　**日期**：二〇二六年五月三十日

---

"""
    # 在标题后添加封面信息
    content = re.sub(r'(# 基于 Transformer 的股票预测系统)\n', r'\1\n' + cover_info, content)

    # 将参考文献改为一级标题
    content = re.sub(r'^## 参考文献', '## 参考文献', content, flags=re.MULTILINE)

    return content


def main():
    # 读取源文件
    with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # 执行格式转换
    converted = convert_format(content)

    # 写入目标文件
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(converted)

    print(f"格式转换完成！")
    print(f"输出文件: {OUTPUT_FILE}")


if __name__ == '__main__':
    main()