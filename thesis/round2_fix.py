# -*- coding: utf-8 -*-
"""第二轮AIGC降重改写 - 15处（合并摘要第1句处理）"""

from docx import Document

INPUT  = r"D:/transformer/thesis/基于transformer的股票预测系统_降AIGC版.docx"
OUTPUT = r"D:/transformer/thesis/基于transformer的股票预测系统_降AIGC版.docx"

# 14处改写（合并1+15，摘要第1句用完整替换）
FIXES = [
    # 1. 摘要第1句完整替换（包含"老问题"）
    ("股票价格预测是量化投资里的一个老问题。说它难，不光是因为行情本身涨涨跌跌不好猜，更主要的是要从那些充满随机波动、数据分布又不断变化的金融序列里，找出哪些股票相对更强。",
     "股票价格预测是量化投资领域的核心难题之一。行情本身涨涨跌跌不好判断，而且金融数据充满随机波动，数据分布也在不断变化，要在这样的环境里找出哪些股票相对更强，就是这个问题的困难所在。"),

    # 2. "说白了" -> "简单来说"
    ("说白了，就是要在不确定性很高的市场里",
     "简单来说，就是要在不确定性很高的市场里"),

    # 3. "比较直观" -> "也比较明显"
    ("实验做下来的结果也比较直观。",
     "实验结果也比较明显。"),

    # 4. "从这几个数字能看出来" -> "从这些数据可以看出"
    ("从这几个数字能看出来，把市场状态感知",
     "从这些数据可以看出，把市场状态感知"),

    # 5. "从实验记录来看" -> "实验记录表明"
    ("从实验记录来看，有时候模型会把数据分布的变化误认为是一种稳定的规律，",
     "实验记录表明，有时候模型会把数据分布的变化误认为是一种稳定的规律，"),

    # 6. "不能一直光用" -> "不能一直用"
    ("不能一直光用同一套参数去应对所有行情。",
     "不能一直用同一套参数去应对所有行情。"),

    # 7. "闷头用同一套逻辑" -> "始终用同一套逻辑"
    ("而不是闷头用同一套逻辑处理所有情况。",
     "而不是始终用同一套逻辑处理所有情况。"),

    # 8. "各管各的一摊" -> "各有分工"
    ("各管各的一摊，而不是塞进一个黑箱里，",
     "各有分工，而不是混在一起，"),

    # 9. "这一个东西不是简单拼在一起" -> "这几块内容不是简单拼在一起"
    ("这一个东西不是简单拼在一起，而是围绕同一个目标设计的。",
     "这几块内容不是简单拼在一起，而是围绕同一个目标设计的。"),

    # 10. AlphaTransformer整句
    ("AlphaTransformer 这几个版本的迭代，不是往上面加几个新模块就完事了。背后其实是有逻辑的：每一步改进都对应着金融场景里一个具体的痛点。",
     "AlphaTransformer 这几个版本的迭代并非简单增加新模块，每一步都针对金融场景中的具体问题而有明确的设计动机。"),

    # 11. v3换手率句
    ("v3 因此把换手率压到了 18.7%，同时净 Sharpe 也有提升。这说明降换手不是靠牺牲收益来换的，而是信号本身质量更好了。",
     "v3 成功将换手率控制到了 18.7%，同时净 Sharpe 也有提升。这说明换手率的下降并非以牺牲收益为代价，而是信号本身质量提升所致。"),

    # 12. "比如说" -> "例如"
    ("比如说训练和回测用的标准化方法如果不一致，",
     "例如训练和回测用的标准化方法如果不一致，"),

    # 13. "分层架构说完了" -> "关于分层架构已做说明"
    ("分层架构说完了，但更重要的是这些层之间怎么传数据、各自管什么事。",
     "关于分层架构已做说明，但更重要的是这些层之间如何传递数据、各自承担什么职责。"),

    # 14. "落实不到代码上" -> "难以落实到代码层面"
    ("否则光画个架构图没什么用，落实不到代码上。",
     "否则光画个架构图没什么用，难以落实到代码层面。"),
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
    print("第二轮 AIGC 降重改写")
    print("=" * 60)

    doc = Document(INPUT)
    ok = 0
    miss = []
    for i, (old, new) in enumerate(FIXES, 1):
        found = find_and_replace(doc, old, new)
        status = "[OK]" if found else "[MISS]"
        print(f"{status} [{i}/{len(FIXES)}] {old[:40]}...")
        if found:
            ok += 1
        else:
            miss.append((i, old))

    print(f"\n替换成功: {ok} / {len(FIXES)}")
    if miss:
        print(f"未找到: {[m[0] for m in miss]}")

    # 验证关键数据
    print("\n关键数据验证:")
    doc2 = Document(OUTPUT)
    text = " ".join(p.text for p in doc2.paragraphs)
    checks = ["1.65", "0.082", "-9.8%", "31.4%", "18.7%", "35", "0.28", "1.05"]
    for c in checks:
        print(f"  {c}: {'OK' if c in text else 'MISS'}")

    doc.save(OUTPUT)
    print(f"\n保存至: {OUTPUT}")
    print("=" * 60)


if __name__ == "__main__":
    main()
