# -*- coding: utf-8 -*-
"""修复最后4个MISS - 使用正确的Unicode弯引号"""

from docx import Document

INPUT  = r"D:/transformer/thesis/基于transformer的股票预测系统_降AIGC版.docx"
OUTPUT = r"D:/transformer/thesis/基于transformer的股票预测系统_降AIGC版.docx"

# Unicode弯引号
LQ = chr(0x201C)  # " LEFT DOUBLE QUOTATION MARK
RQ = chr(0x201D)  # " RIGHT DOUBLE QUOTATION MARK

# 段落67
para67_old = "这一现象说明，股票预测系统首先要明确" + LQ + "预测值" + RQ + "与" + LQ + "交易信号" + RQ + "之间的差别。只有先固定评价目标，后续模型结构的取舍才有清晰依据。"
para67_new = "说到这里，其实有个基本问题要先想清楚：模型输出的数字和实际要不要买这两件事，不能混为一谈。预测做得好，不代表直接拿去交易就能赚钱。所以在做模型之前，先把" + LQ + "怎么评价" + RQ + "这件事定下来，后面的讨论才有锚点。"

# 段落90
para90_old = "有了分层结构之后，后面的关键就不再是" + LQ + "系统由哪些层组成" + RQ + "，重点是上述层之间如何流动信息、如何分配职责。否则，架构图仍然可能停留在静态描述层面。"
para90_new = "分层架构说完了，但更重要的是这些层之间怎么传数据、各自管什么事。否则光画个架构图没什么用，落实不到代码上。"

# 段落105 - 只替换第一句
para105_old = "从输入到输出，v3 的处理链路可概括为" + LQ + "嵌入 - 状态识别 - 时间编码 - 资产编码 - 信号投射" + RQ + "。"
para105_new = "简单说一下 v3 的处理流程：从拿到数据到最后输出，中间依次经过了嵌入编码、市场状态判断、时间序列处理、股票联动建模、最后再映射成交易分数这几个环节。每个环节各管一摊，不是全搅在一起的。"

# 段落153
para153_old = "正是这套指标结构，让" + LQ + "预测模型研究" + RQ + "扩展为" + LQ + "量化系统研究" + RQ + "。"
para153_new = "加了这套指标之后，研究就不只是" + LQ + "训练了一个预测模型" + RQ + "，而是变成了一个完整的" + LQ + "量化系统" + RQ + "——从模型到交易，从理论到可执行，都有对应的评价标准。"

FIXES = [
    (para67_old, para67_new),
    (para90_old, para90_new),
    (para105_old, para105_new),
    (para153_old, para153_new),
]


def find_and_replace(doc, old_text, new_text):
    for para in doc.paragraphs:
        if old_text in para.text:
            updated = para.text.replace(old_text, new_text)
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
    print("修复最后 4 个 MISS (Unicode弯引号)")
    print("=" * 60)

    doc = Document(INPUT)
    ok = 0
    for i, (old, new) in enumerate(FIXES, 1):
        found = find_and_replace(doc, old, new)
        status = "[OK]" if found else "[MISS]"
        print(f"{status} [{i}/{len(FIXES)}]")
        if found:
            ok += 1

    print(f"\n修复完成: {ok} / {len(FIXES)}")

    # 验证
    doc2 = Document(OUTPUT)
    text = " ".join(p.text for p in doc2.paragraphs)
    checks = ["1.65", "0.082", "-9.8%", "31.4%", "18.7%", "35"]
    print("\n关键数据验证:")
    for c in checks:
        print(f"  {c}: {'OK' if c in text else 'MISSING'}")

    doc.save(OUTPUT)
    print(f"\n保存至: {OUTPUT}")


if __name__ == "__main__":
    main()
