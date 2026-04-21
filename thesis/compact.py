import sys
sys.stdout.reconfigure(encoding='utf-8')
with open(r'd:/transformer/thesis/paper_final.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace 1: Remove redundant paragraph in 1.1
old1 = '将先进时序模型真正转化为可运行、可评估、可部署的系统，具有显著的学术价值与工程价值。一方面，学术研究需要回答"何种建模方式能够稳定提升 Information Coefficient 与风险调整收益"；另一方面，工程落地还必须解决数据泄露、回测失真、换手率过高等现实问题（Ma et al., 2024; Qian, 2025）。'
new1 = '将先进时序模型转化为可运行、可评估、可部署的系统，具有显著学术与工程价值（Ma et al., 2024; Qian, 2025）。'
content = content.replace(old1, new1)

# Replace 2: Compact 1.3 - use a more targeted approach
old2 = """尽管深度学习在股票预测领域已取得诸多进展，但现有研究仍存在以下关键瓶颈。

第一，传统模型对复杂非线性时序模式识别能力不足。金融市场中的价格演化是多主体博弈，信息不对称和流动性冲击共同作用的结果，传统统计模型难以表达突发跳变、异方差扩散和多因子交互所形成的复杂动力学。

第二，标准 Transformer 在长序列场景下面临 \\(O\\(n\\^2\\)\\) 复杂度瓶颈。对于分钟级甚至更高频的行情数据，注意力矩阵带来显著的显存占用与计算延迟，导致训练效率下降与在线推理代价过高。

第三，极端市场状态下模型泛化能力与鲁棒性不足。金融市场具有典型的非平稳性，不同阶段在波动率水平，行业轮动速度与情绪传导强度方面差异显著。若模型假设所有样本服从统一分布，则容易在平稳期表现良好而在极端行情中失效，表现为训练损失下降但 IC 提升有限甚至收益失真。

第四，回测流程中数据泄露问题突出。若在标准化过程中使用全样本统计量或引用未来时点信息，模型将获得现实中不可用的先验知识，使回测结果被系统性高估。标签构造中的时间错位、训练集与测试集边界污染也会造成隐性数据泄露。

第五，高换手率导致策略收益被交易摩擦显著侵蚀。即使模型具有一定排序能力，若组合调仓过于频繁，交易成本和冲击成本仍会吞噬绝大部分账面收益。许多预测模型"收益高而 Sharpe 低"，本质原因在于信号有效性不足以覆盖高频交易摩擦。"""

new2 = '尽管深度学习已取得诸多进展，但现有研究仍存在以下关键瓶颈：第一，传统模型对复杂非线性时序模式识别能力不足，金融市场中的价格演化是多主体博弈与流动性冲击共同作用的结果，传统统计模型难以表达突发跳变和多因子交互；第二，标准 Transformer 在长序列场景下面临 \\(O\\(n\\^2\\)\\) 复杂度瓶颈，分钟级行情数据的注意力矩阵带来显著显存占用与计算延迟；第三，极端市场状态下模型泛化能力不足，不同阶段在波动率和行业轮动速度方面差异显著，模型容易在平稳期表现良好而在极端行情中失效；第四，回测流程中数据泄露问题突出，使用全样本统计量或引用未来时点信息会使回测结果被系统性高估；第五，高换手率导致策略收益被交易摩擦显著侵蚀，信号有效性不足以覆盖高频交易摩擦是"收益高而 Sharpe 低"的本质原因。'

if old2 in content:
    content = content.replace(old2, new2)
    print(f"Replaced old2, saved changes")
else:
    print("old2 NOT FOUND")

# Replace 3: Compact 4.8
old3 = """### 4.8 模型复杂度分析

各版本模型的计算复杂度存在显著差异。v1 的核心复杂度为 \(\Theta(T^2 \cdot d)\)，完全受限于时间维的二次注意力；v2 在 patch 化后约为 \(\Theta(M^2 \cdot d)\)；v3 的时间轴主干近似为 \(\Theta(M \cdot D)\)，即 patch 数乘以状态维度的线性复杂度。v3 将原本完全依赖时间二次复杂度的问题，拆分为"线性时间建模 + 资产维注意力建模"，从而在理论上获得了更好的可扩展性。Mamba-2 的线性递推结构天然适合金融时间序列的"记忆衰减"特性，在长序列场景下不仅效率更高，其选择性机制也对噪声过滤具有更好的效果。"""

new3 = """### 4.8 模型复杂度分析

v1 的核心复杂度为 \(\Theta(T^2 \cdot d)\)，完全受限于时间维的二次注意力；v2 在 patch 化后约为 \(\Theta(M^2 \cdot d)\)；v3 的时间轴主干近似为 \(\Theta(M \cdot D)\)，将原本的时间二次复杂度问题拆分为"线性时间建模 + 资产维注意力建模"。Mamba-2 的线性递推结构天然适合金融时间序列的"记忆衰减"特性，在长序列场景下效率更高，其选择性机制也对噪声过滤具有更好的效果。"""

if old3 in content:
    content = content.replace(old3, new3)
    print(f"Replaced old3")
else:
    print("old3 NOT FOUND")

with open(r'd:/transformer/thesis/paper_final.md', 'w', encoding='utf-8') as f:
    f.write(content)

# Count
chinese = sum(1 for c in content if '\u4e00' <= c <= '\u9fff')
import re
english_letters = len(re.findall(r'[a-zA-Z]', content))
total = chinese + english_letters
print(f"Total (Chinese + English letters): {total}")
print(f"Target: 13000-18000")
print(f"OK: {13000 <= total <= 18000}")
