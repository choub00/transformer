import sys, re
sys.stdout.reconfigure(encoding='utf-8')
with open(r'd:/transformer/thesis/paper_final.md', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Compact section 1.1 - remove a paragraph
old = """随着算力条件改善和深度学习方法的发展，金融时间序列预测逐步从传统统计建模向深度表征学习转变。早期研究多基于 RNN、LSTM 与 CNN（Hochreiter & Schmidhuber, 1997），通过自动提取局部模式与时间依赖来替代手工特征工程，但 RNN 类模型梯度传播路径较长、CNN 难以有效建模长距离依赖，促使研究重点转向 Transformer 体系（Vaswani et al., 2017）。PatchTST 通过将时间序列切分为局部补丁，有效缓解了长序列建模中的冗余计算与局部语义缺失问题（Nie et al., 2023）；iTransformer 进一步从"变量而非时间点"出发重构 token 组织方式，在资产维的表示学习方面表现出更好的泛化性（Liu et al., 2024）。除 Transformer 体系外，Mamba 类模型通过选择性状态更新机制，将序列建模复杂度由二次压缩至近线性，在超长序列处理方面展现出明显潜力（Gu & Dao, 2023; Dao & Gu, 2024）。"""
new = """随着算力条件改善，深度学习方法逐步取代传统统计建模成为主流。早期研究多基于 RNN、LSTM 与 CNN（Hochreiter & Schmidhuber, 1997），但 RNN 类模型梯度传播路径较长、CNN 难以有效建模长距离依赖，促使研究转向 Transformer（Vaswani et al., 2017）。PatchTST 通过局部补丁缓解长序列冗余计算（Nie et al., 2023）；iTransformer 重构 token 语义，在资产维表示学习方面表现更好（Liu et al., 2024）；Mamba 类模型将复杂度由二次压缩至近线性（Gu & Dao, 2023; Dao & Gu, 2024）。"""
content = content.replace(old, new)
print("1.1 done")

# 2. Compact section 1.3 - collapse bullet points to running text
old2 = """尽管深度学习在股票预测领域已取得诸多进展，但现有研究仍存在以下关键瓶颈。

第一，传统模型对复杂非线性时序模式识别能力不足。金融市场中的价格演化是多主体博弈，信息不对称和流动性冲击共同作用的结果，传统统计模型难以表达突发跳变、异方差扩散和多因子交互所形成的复杂动力学。

第二，标准 Transformer 在长序列场景下面临 \\(O\\(n\\^2\\)\\) 复杂度瓶颈。对于分钟级甚至更高频的行情数据，注意力矩阵带来显著的显存占用与计算延迟，导致训练效率下降与在线推理代价过高。

第三，极端市场状态下模型泛化能力与鲁棒性不足。金融市场具有典型的非平稳性，不同阶段在波动率水平，行业轮动速度与情绪传导强度方面差异显著。若模型假设所有样本服从统一分布，则容易在平稳期表现良好而在极端行情中失效，表现为训练损失下降但 IC 提升有限甚至收益失真。

第四，回测流程中数据泄露问题突出。若在标准化过程中使用全样本统计量或引用未来时点信息，模型将获得现实中不可用的先验知识，使回测结果被系统性高估。标签构造中的时间错位、训练集与测试集边界污染也会造成隐性数据泄露。

第五，高换手率导致策略收益被交易摩擦显著侵蚀。即使模型具有一定排序能力，若组合调仓过于频繁，交易成本和冲击成本仍会吞噬绝大部分账面收益。许多预测模型"收益高而 Sharpe 低"，本质原因在于信号有效性不足以覆盖高频交易摩擦。"""
new2 = """尽管深度学习已取得诸多进展，但现有研究仍存在以下关键瓶颈：第一，传统模型对复杂非线性时序模式识别能力不足，金融市场中的价格演化是多主体博弈与流动性冲击共同作用的结果，传统统计模型难以表达突发跳变和多因子交互；第二，标准 Transformer 在长序列场景下面临 \\(O\\(n\\^2\\)\\) 复杂度瓶颈，分钟级行情数据的注意力矩阵带来显著显存占用与计算延迟；第三，极端市场状态下模型泛化能力不足，不同阶段在波动率和行业轮动速度方面差异显著，模型容易在平稳期表现良好而在极端行情中失效；第四，回测流程中数据泄露问题突出，使用全样本统计量或引用未来时点信息会使回测结果被系统性高估；第五，高换手率导致策略收益被交易摩擦显著侵蚀，"收益高而 Sharpe 低"的本质原因是信号有效性不足以覆盖高频交易摩擦。"""
if old2 in content:
    content = content.replace(old2, new2)
    print("1.3 done")
else:
    print("1.3 NOT FOUND")

# 3. Compact section 2.1 IC description
old3 = """该指标度量的是横截面上预测排序与真实收益排序之间的线性相关性。在金融场景中，稳定的 0.05 以上的 IC 已具有较强的研究与交易价值——考虑到金融市场的强噪声环境，能够在统计意义上持续保持正相关的预测信号本身就意味着模型捕捉到了真实的信息驱动因素，而非仅仅是噪声拟合。"""
new3 = """该指标度量的是横截面上预测排序与真实收益排序之间的线性相关性。在金融场景中，稳定的 0.05 以上的 IC 已具有较强的研究与交易价值——考虑到金融市场的强噪声环境，能够持续保持正相关的预测信号本身就意味着模型捕捉到了真实的信息驱动因素，而非仅仅是噪声拟合。"""
content = content.replace(old3, new3)
print("2.1 done")

# 4. Compact section 4.8 already done

with open(r'd:/transformer/thesis/paper_final.md', 'w', encoding='utf-8') as f:
    f.write(content)

chinese = sum(1 for c in content if '\u4e00' <= c <= '\u9fff')
english_letters = len(re.findall(r'[a-zA-Z]', content))
total = chinese + english_letters
print(f"Total: {total}")
print(f"Target: 13000-18000")
print(f"OK: {13000 <= total <= 18000}")
