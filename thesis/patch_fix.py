# -*- coding: utf-8 -*-
"""补修：第103段AlphaTransformer句子"""

from docx import Document

INPUT  = r"D:/transformer/thesis/基于transformer的股票预测系统_降AIGC版.docx"
OUTPUT = r"D:/transformer/thesis/基于transformer的股票预测系统_降AIGC版.docx"

# 段落103: AlphaTransformer的版本迭代句
FIXES = [
    # 原句（有问题的版本，来自第一轮但改得不彻底）
    ("AlphaTransformer 这几个版本的迭代，不是往上面随便加几个新模块就完事了。背后其实是有逻辑的：每一步改进都对应着金融场景里一个具体的痛点。",
     "AlphaTransformer 这几个版本的迭代并非简单增加新模块，每一步都针对金融场景中的具体问题而有明确的设计动机。"),
]


def find_and_replace(doc, old_kw, new_text):
    for para in doc.paragraphs:
        if old_kw in para.text:
            updated = para.text.replace(old_kw, new_text, 1)
            _replace_para(para, updated)
            return True
    return False


def _replace_para(para, new_text):
    if not para.runs:
        para.add_run(new_text)
        return
    first_run = para.runs[0]
    first_run.text = new_text
    for r in para.runs[1:]:
        r.text = ""


def main():
    print("=" * 60)
    print("补修 AlphaTransformer 句子")
    print("=" * 60)

    doc = Document(INPUT)
    ok = 0
    for i, (old, new) in enumerate(FIXES, 1):
        found = find_and_replace(doc, old, new)
        status = "[OK]" if found else "[MISS]"
        print(f"{status} [{i}/{len(FIXES)}]")
        if found:
            ok += 1

    print(f"\n补修: {ok} / {len(FIXES)}")

    # 验证关键数据
    doc2 = Document(OUTPUT)
    text = " ".join(p.text for p in doc2.paragraphs)
    checks = ["1.65", "0.082", "-9.8%", "31.4%", "18.7%", "35"]
    print("\n关键数据:")
    for c in checks:
        print(f"  {c}: {'OK' if c in text else 'MISS'}")

    doc.save(OUTPUT)
    print(f"\n保存至: {OUTPUT}")
    print("=" * 60)


if __name__ == "__main__":
    main()
