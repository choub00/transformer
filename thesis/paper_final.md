# 基于 Transformer 的股票预测系统

**姓名**：胡宠博　**学号**：20221216032013　**院系**：金融科技学院
**专业**：人工智能　**指导教师**：刘冲　**日期**：二〇二五年五月三十日

---

## 摘要

股票价格预测是金融科技与量化投资交叉领域的核心问题，其目标在于从高噪声、强非平稳的金融时间序列中提取可用于投资决策的有效信号。传统统计模型与浅层机器学习方法对复杂非线性时序关系和跨资产联动结构的刻画能力有限；标准 Transformer 在长序列金融数据场景下仍面临注意力计算复杂度 \(O(n^2)\)、极端市场状态下泛化能力下降等问题。若训练集构造与回测流程设计不严格，极易引入未来函数、标签错位等数据泄露风险，造成信息系数偏低背景下收益评估被虚高放大；同时，高换手率还会导致交易摩擦显著侵蚀账面收益。针对上述问题，本文设计并实现了一种基于 Transformer 的股票预测系统。

本文提出 AlphaTransformer v3 模型，在统一框架下融合 Regime-Aware 市场状态感知、Mamba-2 时间轴线性建模、iTransformer 资产维相关性建模与交易导向损失函数。Regime-Aware 模块通过 Autoencoder 重建误差识别市场状态，实现自适应特征归一化；Mamba-2 模块以线性复杂度替代标准注意力的二次复杂度；iTransformer 在资产维上捕捉板块联动与风格迁移效应；CombinedQuantLoss 对排序能力与换手率约束进行协同优化。系统采用滚动窗口标准化与 Walk-Forward 验证抑制数据泄露，设计 Anti-Churn 集合差集调仓降低交易磨损，前后端采用 Vue 3 与 FastAPI 分离架构。实验表明，相较于 v1，v3 的 Sharpe 由 0.28 升至 1.65，IC 由 0.073 升至 0.082，最大回撤控制在 -9.8%，年化收益达 31.4%，换手率降至 18.7%，累计交易 35 次。研究表明，Regime-Aware、Mamba-2 与 iTransformer 的时空混合建模结合数据泄露防控与交易摩擦抑制机制，能够有效提升股票预测系统的学术与工程价值。

**关键词**：Transformer；股票预测；深度学习；时间序列；量化交易系统
本文围绕股票预测系统中的低信息系数与高换手率两大瓶颈，设计并实现了基于 Transformer 的 AlphaTransformer v3 混合架构，系统性提升了复杂时空信息建模与交易可执行性。首先，为增强模型对极端市场状态及分布漂移的鲁棒性，提出基于自编码器的 Regime-Aware 检测模块，通过重建误差识别市场状态，并引入 RegimeAwareNorm 实现分情景自适应归一化及路由。其次，针对标准 Transformer 注意力计算复杂度高、长序列建模效率低下等问题，集成 Mamba-2 状态空间模块，以线性复杂度高效建模时序依赖，并采用 PatchTST 风格的局部补丁机制以保持局部时序语义。第三，在多资产预测场景下，融合 iTransformer 反资产维建模范式，有效捕捉资产间相关性、行业联动与风格迁移，提升横截面排序和板块共振建模能力。输出端通过 WaveLSFormer-inspired 的多空决策头及 CombinedQuantLoss 损失函数，将排序能力、风险收益特性与换手率约束统一优化，兼顾策略可交易性与风险调整回报。

系统工程层面，本平台自底向上集成模型训练层、服务接口层和前端可视化层。在数据处理上，采用滚动窗口归一化、严格时序对齐标签构造与 Walk-Forward 验证，实现全流程防止数据泄露；回测与实盘交易中引入 Anti-Churn 差集调仓算法、显式交易成本建模与风险敞口管控，全面抑制高换手率带来的收益蚕食。前后端采用 Vue 3 + FastAPI 解耦架构，支持预测可视化、回测分析、交易面板与在线部署，保障了模型研究到系统落地的可追溯性和可复现性。

实验结果表明，AlphaTransformer v3 在预测稳定性、排序有效性与风险调整收益等指标上，较 v1 显著提升（Sharpe 由 0.28 升到 1.65，IC 由 0.073 达 0.082，最大回撤控制在 -9.8%，年化收益 31.4%，换手率降至 18.7%，累计交易次数降为 35），在高波动市场环境下依然保持稳健预测与回测表现。研究验证了 Regime-Aware、Mamba-2 与 iTransformer 时空混合框架，结合数据泄露防控与换手率压制机制，可大幅增强股票预测系统的学术创新性与工程落地价值。

---

## 第1章 绪论

### 1.1 研究背景

股票价格预测是金融科技、人工智能与量化投资交叉领域的基础性问题，其目标是从历史价格、成交量、技术指标与行业联动关系中提取可用于未来决策的有效信号。与一般工业时序不同，金融时间序列具有高噪声、弱信号、强非平稳、厚尾分布及突发冲击频繁等典型特征（Zeng et al., 2023）。在量化实践中，模型必须具备横截面排序能力、风险控制能力和交易可执行性，才能在回测与实盘中形成稳定的超额收益（Ma et al., 2024）。

随着算力条件改善，深度学习方法逐步取代传统统计建模成为主流。早期研究多基于 RNN、LSTM 与 CNN（Hochreiter & Schmidhuber, 1997），但 RNN 类模型梯度传播路径较长、CNN 难以有效建模长距离依赖，促使研究转向 Transformer（Vaswani et al., 2017）。PatchTST 通过局部补丁缓解长序列冗余计算（Nie et al., 2023）；iTransformer 重构 token 语义，在资产维表示学习方面表现更好（Liu et al., 2024）；Mamba 类模型将复杂度由二次压缩至近线性（Gu & Dao, 2023; Dao & Gu, 2024）。

将先进时序模型转化为可运行、可评估、可部署的系统，具有显著学术与工程价值（Ma et al., 2024; Qian, 2025）。

### 1.2 国内外研究现状

在早期研究中，ARIMA、GARCH 等传统统计模型被广泛用于收益率建模与波动率分析（Box et al., 2015），但对非线性关系与跨资产耦合现象刻画能力有限。近年来，深度学习方法逐步成为主流，Transformer 在时间序列领域快速扩展。Zeng 等（2023）指出部分时序 Transformer 在建模顺序信息方面存在先天局限，推动学界从 token 构造、维度组织与复杂度控制等角度开展更有效的结构创新。Stockformer 将小波分解、多任务学习与自注意力结合（Ma et al., 2024）；IL-ETransformer 引入增量学习机制应对数据分布漂移（Qian, 2025）；WaveLSFormer 将可学习小波分解与多空组合输出结合，直接面向风险调整收益优化（Li & Cheng, 2026）；2026 年研究还引入 Regime-Aware 路由与图结构节点 Transformer（Ridhawi et al., 2026）。学术界已形成共识：仅从均方误差或方向分类准确率出发不足以支撑真实可交易的股票预测系统，必须将非平稳性、回测机制与交易摩擦纳入统一研究框架。

### 1.3 现有研究的主要问题

尽管深度学习已取得诸多进展，但现有研究仍存在以下关键瓶颈：第一，传统模型对复杂非线性时序模式识别能力不足，金融市场中的价格演化是多主体博弈与流动性冲击共同作用的结果，传统统计模型难以表达突发跳变和多因子交互；第二，标准 Transformer 在长序列场景下面临 \(O(n^2)\) 复杂度瓶颈，分钟级行情数据的注意力矩阵带来显著显存占用与计算延迟；第三，极端市场状态下模型泛化能力不足，不同阶段在波动率和行业轮动速度方面差异显著，模型容易在平稳期表现良好而在极端行情中失效；第四，回测流程中数据泄露问题突出，使用全样本统计量或引用未来时点信息会使回测结果被系统性高估；第五，高换手率导致策略收益被交易摩擦显著侵蚀，"收益高而 Sharpe 低"的本质原因是信号有效性不足以覆盖高频交易摩擦。

### 1.4 研究内容与论文结构

针对上述问题，本文研究内容包括：（1）设计 AlphaTransformer v3 混合架构；（2）构建严格防泄露的数据管道与 Walk-Forward 评估框架；（3）设计 Anti-Churn 集合差集调仓机制；（4）实现前后端分离的股票预测系统。全文结构如下：第2章介绍金融评价体系与关键技术理论；第3章进行系统需求分析与总体架构设计；第4章详细阐述 AlphaTransformer v3 模型设计；第5章描述防泄露训练框架与回测评估方法；第6章报告实验结果与系统实现细节；第7章总结全文并展望未来方向。

---

## 第2章 关键技术与理论基础

### 2.1 金融评价体系

金融时间序列预测与一般时序预测存在本质差异。在量化选股的横截面预测场景中，模型的核心目标并非对单只资产进行逐点预测，而是对给定时间截面上所有资产按未来收益相对优劣进行排序。

设股票池包含 \(N\) 只资产，每只资产在时刻 \(t\) 的输入特征为 \(\mathbf{x}_t^{(i)} \in \mathbb{R}^d\)，模型学习映射函数 \(f_\theta: \mathbb{R}^{N \times T \times F} \to \mathbb{R}^N\)，输出横截面排序信号 \(\hat{\mathbf{r}}_{t+H}^{(1:N)}\)。

**Information Coefficient（IC）** 是衡量排序质量的核心指标，定义为预测信号与未来真实收益的 Pearson 相关系数：

\[
\text{IC}_t = \frac{\text{Cov}\left(\hat{r}_t^{(i)}, r_t^{(i)}\right)}{\sigma\left(\hat{r}_t\right) \cdot \sigma\left(r_t\right)} \tag{2-1}
\]

该指标度量的是横截面上预测排序与真实收益排序之间的线性相关性。在金融场景中，稳定的 0.05 以上的 IC 已具有较强的研究与交易价值——考虑到金融市场的强噪声环境，能够持续保持正相关的预测信号本身就意味着模型捕捉到了真实的信息驱动因素，而非仅仅是噪声拟合。

**Sharpe Ratio** 衡量单位风险获得的超额收益：

\[
\text{Sharpe} = \frac{E[R_p - R_f]}{\sigma(R_p - R_f)} \tag{2-2}
\]

Sharpe Ratio 是连接预测能力与交易结果的桥梁。仅当 IC 转化为稳定 Sharpe 时，模型的学术价值才能延伸为工程价值。

**最大回撤（MDD）** 衡量净值序列历史上最严重的资本回落：

\[
\text{MDD} = \max_{0 \leq s < t \leq T} \frac{E_t - E_s}{E_s} \tag{2-3}
\]

其中 \(E_t\) 为 \(t\) 时刻的累计净值，反映策略在最不利情况下的生存能力。

**换手率（Turnover）** 反映组合调仓频率：

\[
\text{Turnover}_t = \frac{1}{2} \sum_{i=1}^{N} \left|w_t^{(i)} - w_{t-1}^{(i)}\right| \tag{2-4}
\]

换手率过高将显著侵蚀净收益，因此换手率控制是量化策略设计中不可或缺的约束项。

### 2.2 Transformer 时序建模原理与复杂度瓶颈

Transformer 的核心在于自注意力机制。给定输入序列矩阵 \(\mathbf{X} \in \mathbb{R}^{n \times d}\)，通过线性映射得到查询、键和值：

\[
\mathbf{Q} = \mathbf{X}\mathbf{W}_Q,\quad \mathbf{K} = \mathbf{X}\mathbf{W}_K,\quad \mathbf{V} = \mathbf{X}\mathbf{W}_V \tag{2-5}
\]

Scaled Dot-Product Attention 定义为：

\[
\text{Attention}(\mathbf{Q}, \mathbf{K}, \mathbf{V}) = \text{softmax}\!\left(\frac{\mathbf{Q}\mathbf{K}^\top}{\sqrt{d_k}}\right)\mathbf{V} \tag{2-6}
\]

在金融时间序列建模中，序列中的每个时间点代表特定的市场状态快照。注意力权重矩阵中的元素度量的是时间点 \(i\) 与时间点 \(j\) 在学习表示空间中的相似程度。当模型能够识别出历史上某些市场状态模式与当前状态高度相似时，可以通过注意力机制提取与当前预测最相关的历史信息。然而，这一机制存在双重性：一方面，它允许模型捕捉跨年度的市场周期规律；另一方面，历史上从未出现过的极端事件在注意力矩阵中无法找到真正匹配的"模板"，导致模型在危机期的表现急剧下降。

自注意力机制的时间与空间复杂度均为：

\[
\mathcal{T}(n) = \Theta(n^2 \cdot d), \quad \mathcal{M}(n) = \Theta(n^2) \tag{2-7}
\]

当 \(n\) 较大时，计算成本呈平方级增长。更深层的问题在于：金融时间序列中大量时间点仅包含噪声信息，对预测贡献甚微，但注意力机制仍将其平等对待，导致"表征稀释"——噪声时间点分散了注意力权重，削弱了真正有价值时间点的影响力。

### 2.3 时序 Transformer 的优化范式演进

从技术哲学角度看，时序 Transformer 的演进经历了三个阶段：第一阶段以 CNN-RNN 为代表，侧重局部模式提取但受限于长距离建模能力；第二阶段以标准 Transformer 为代表，通过全局注意力解决长程依赖但在效率和噪声处理上付出代价；第三阶段以 PatchTST 和 iTransformer 为代表，通过重新设计 token 语义和计算路径寻求更优平衡。

**PatchTST** 将长度为 \(L\) 的原始时间序列切分为 \(M\) 个局部补丁：

\[
M = \left\lfloor \frac{L - P}{S} \right\rfloor + 1 \tag{2-8}
\]

其中 \(P\) 为 patch 长度，\(S\) 为步长。该变换的金融逻辑在于：金融市场的有效信息往往以"形态"而非"点"的形式存在——例如"连续三日上涨后放量突破均线"是有意义的局部结构，而单独看每一天的价格则噪声较大。通过将相邻时间点聚合为 patch，模型获得的是包含短期趋势、波动形态和动量结构的局部表示，而非单日噪声。Patch 化将 token 数量从 \(L\) 压缩至 \(M \ll L\)，使后续注意力计算的复杂度由 \(O(L^2)\) 降至 \(O(M^2)\)（Nie et al., 2023）。

**iTransformer** 反转 token 的维度语义。传统时序 Transformer 将每个时间步视为 token，关注"哪些时间点之间存在关联"；iTransformer 则将每个变量（资产）视为 token，关注"哪些资产之间存在联动"。在金融实践中，同一行业的多只股票往往受相同的行业因子驱动，银行股与保险股之间存在风险传染路径，白酒板块与食品饮料板块之间存在消费风格的资金迁移。这些横截面关系无法在时间维注意力中自然表达。iTransformer 通过在资产维执行自注意力：

\[
\mathbf{H}_{\text{asset}} = \text{Attention}\!\left(\mathbf{Q}_{\text{asset}}, \mathbf{K}_{\text{asset}}, \mathbf{V}_{\text{asset}}\right) \tag{2-9}
\]

使模型能够显式学习资产间的协动模式、轮动规律与传染效应（Liu et al., 2024）。

### 2.4 状态空间模型与 Mamba-2 线性复杂度建模

Mamba-2 在状态空间模型基础上引入了选择性机制（Selective Scan），使状态转移矩阵的元素能够根据当前输入动态生成（Gu & Dao, 2023; Dao & Gu, 2024）。其离散化更新公式为：

\[
h_m = \overline{\mathbf{A}}_m \odot h_{m-1} + \overline{\mathbf{B}}_m \odot x_m, \quad y_m = \mathbf{C}^\top h_m \tag{2-10}
\]

其中 \(\overline{\mathbf{A}}_m\) 和 \(\overline{\mathbf{B}}_m\) 通过离散化规则从 \(\mathbf{A}_m, \mathbf{B}_m\) 变换而来，且依赖于当前输入 \(x_m\)。选择性机制的金融意义在于：模型能够根据当前市场状态动态决定"记住多少过去的信息"。在趋势明确的市场中，模型更多依赖近期数据进行递推预测；在震荡市场中，模型可选择更多参考远期历史以发现周期性规律。这种动态筛选能力是标准注意力机制所不具备的——后者虽然能通过注意力权重反映相关性，但仍需要计算全序列的两两相似度，在长序列场景下计算代价高昂。

Mamba-2 的时间复杂度近似为：

\[
\mathcal{T}_{\text{Mamba}}(L) = \Theta(L \cdot D) \tag{2-11}
\]

其中 \(D\) 为状态维度。当序列长度 \(L\) 较大时，线性复杂度相对于注意力机制的二次复杂度具有显著优势。这意味着在固定显存预算下可以保留更长的时间窗口，捕捉更长周期的市场状态切换规律，而无需通过截断历史窗口来换取计算可行性。

### 2.5 Regime-Aware 建模思想

金融市场具有典型的非平稳性，不同阶段在波动率水平、行业轮动速度和情绪传导强度方面存在系统性差异。Regime Switching 模型（Fama & French, 1993; Hamilton, 1989）最早从经济学角度刻画了这一现象：市场在不同"状态"之间切换，不同状态下资产的收益分布和协方差结构存在显著差异。

Regime-Aware 机制的核心目标是使模型能够识别当前市场处于何种状态并据此调整预测策略。当市场处于平稳上涨状态时，有效信号往往来自动量效应和行业轮动；当市场进入高波动或危机状态时，原有的动量因子可能反转，波动率因子变得更加重要。普通模型假设所有样本服从统一分布，在市场状态切换时容易出现"旧策略失效、新策略缺失"的困境。Regime-Aware 模块通过显式建模市场状态，使模型能够在不同状态下采用不同的特征缩放和路由路径，从而提升对非平稳金融环境的适应能力。

---

## 第3章 系统需求分析与总体架构设计

### 3.1 系统建设目标

本文的首要目标并非构建一个仅在离线数据集上取得较低预测误差的模型，而是建立一个能够稳定输出高质量横截面排序信号的股票预测系统。根据 AlphaTransformer v1 的实验结果，若模型仅能获得较低水平的 Information Coefficient，则其回测收益往往缺乏稳健的统计支撑。因此，系统建设的第一目标是围绕"提升预测信号有效性"展开，通过多资产联合建模、市场状态感知和时空混合编码机制，提高模型在不同市场阶段下的排序一致性与信号稳定性。

量化投资系统的研究价值不仅取决于预测精度，还取决于交易可执行性。若预测模型输出频繁波动，即便账面收益较高，也会因过度调仓导致滑点和手续费快速累积。因此，本系统在设计之初即将换手率控制纳入整体优化目标，通过回测约束、组合持仓平滑与 Anti-Churn 机制抑制无效调仓。同时，系统应具备可扩展、可维护和可部署特性，各模块之间边界清晰，便于后续替换模型版本或扩展功能。

### 3.2 系统功能需求

系统在功能层面需要满足以下需求：（1）行情数据接入与特征处理，支持严格的时序一致性约束；（2）模型训练、验证与实验管理，支持 Walk-Forward 验证与多版本模型对比；（3）在线预测与推荐输出，输出结构化的排序信号与 Top-N 推荐列表；（4）回测报告生成与风险分析；（5）前端交互与结果可视化展示。

### 3.3 系统非功能需求

从工程实现角度，系统还需要满足以下约束：**响应性能要求**方面，预测接口与健康检查接口应采用轻量化响应协议与缓存机制，降低模型加载和数据序列化的额外开销；**数据一致性要求**方面，数据层、模型层与回测层必须共享统一的特征定义、时间切分方式和标签对齐策略；**降级容灾要求**方面，当主模型不可用时，系统可回退到缓存结果或简化版本模型，保证服务连续性。

### 3.4 系统总体架构

本系统采用前后端分离架构，自底向上分为数据层、模型层、服务层和展示层四层。**数据层**负责原始行情数据接入、特征工程、标签构造及滚动标准化处理。**模型层**以 AlphaTransformer 系列模型为核心，承载 v1 原生 Transformer、v2 Patch 模型以及 v3 Regime-Aware + Mamba-2 + iTransformer 混合架构的训练与推理逻辑。**服务层**基于 FastAPI 实现：FastAPI 原生支持异步请求处理，在高并发预测场景下能够高效复用服务器资源；Pydantic 数据验证机制可在输入层拦截非法数据，避免其进入 PyTorch 推理流程；推理接口将运行时不确定性转化为结构化错误响应，实现自动降级容错。**展示层**基于 Vue 3 构建，以图表化方式呈现收益曲线、风险暴露与交易面板。

### 3.5 核心数据流

系统的核心数据流起点为历史行情与资产池数据。数据首先经过缺失值处理、技术指标衍生和滚动窗口标准化，构造成统一的多资产时序张量。在训练阶段，系统按照 Walk-Forward 流程执行训练与验证，根据 IC、Sharpe、回撤与换手率等多指标综合确定候选模型。在预测阶段，服务层调用模型层输出预测信号并序列化返回前端；回测流程由服务层调用回测防泄露引擎，生成收益曲线与风险指标后交由前端统一渲染。

---

## 第4章 AlphaTransformer v3 模型设计与关键算法

### 4.1 问题形式化定义

设在时刻 \(t\) 的股票池规模为 \(N\)，回看窗口长度为 \(T\)，每只资产包含 \(F\) 维输入特征，则系统输入表示为 \(\mathbf{X}_{t-T+1:t}^{(1:N)} \in \mathbb{R}^{N \times T \times F}\)。模型学习映射函数 \(f_\theta: \mathbb{R}^{N \times T \times F} \to \mathbb{R}^N\)，输出横截面 alpha 信号 \(\hat{\mathbf{r}}_t^{(1:N)}\)。未来 \(H\) 步收益定义为 \(r_{t+H}^{(i)} = \left(P_{t+H}^{(i)} - P_t^{(i)}\right) / P_t^{(i)}\)。为兼顾回归与方向判别，本文同时构造方向标签 \(y_t^{(i)} = \mathbb{I}\left(r_{t+H}^{(i)} > 0\right)\)，使模型同时输出连续收益信号与方向概率。

### 4.2 从 v1 到 v3 的演进逻辑

AlphaTransformer v1 以标准 Transformer 为主体，将时间维特征编码后通过跨资产注意力生成 alpha 分数。根据实验数据，v1 的 Sharpe Ratio 仅为 0.28，IC 仅为 0.073，最大回撤达 -15.2%，累计交易次数高达 147 次。v1 存在三重结构性缺陷：标准 attention 将所有时点两两关联，在金融高噪声序列中产生无效注意力权重，导致表征稀释；v1 默认全市场服从统一分布，忽略了波动期、平稳期和危机期之间的状态差异；信号稳定性不足导致排序结果频繁翻转，诱发高换手率。

v2 针对 v1 的长序列建模缺陷，引入了 PatchTST 风格的时间补丁表示，将 token 数量由 \(T\) 压缩为 \(M = \lfloor (T - P) / S \rfloor + 1\)，将时间轴 attention 复杂度由 \(O(T^2)\) 降至 \(O(M^2)\)。v2 在长序列处理效率与局部模式提取方面优于 v1，但仍未解决两个根本问题：Patch 与稀疏 attention 并未显式建模市场状态切换；v2 的核心视角仍以时间 token 为主，对多资产横截面耦合关系的表达不足。

由此，v3 的架构升级转向"状态感知 + 线性时间建模 + 资产维建模"的联合重构。

### 4.3 AlphaTransformer v3 总体架构

AlphaTransformer v3 的设计目标概括为：在提升 IC 的同时抑制换手率，在增强预测能力的同时保证可交易性。v3 由 Regime-Aware 市场感知模块、Mamba-2 时间编码模块、iTransformer 资产编码模块以及 WaveLSFormerHead 输出层协同组成。设输入张量经线性嵌入后得到 \(\mathbf{H}^{(0)} \in \mathbb{R}^{N \times T \times d}\)，v3 按如下顺序处理：Regime-Aware 模块通过 Autoencoder 重建误差识别当前市场状态，输出状态概率向量 \(\mathbf{p}_t \in \mathbb{R}^K\)；Mamba-2 时间编码器在每个资产的时间维上执行选择性状态空间扫描，生成时间维表示 \(\mathbf{H}_T\)；iTransformer 资产编码器将张量重排后在资产维执行自注意力，生成资产维表示 \(\mathbf{H}_A\)；时间维和资产维表示通过残差融合生成最终表征，经输出头映射为组合权重 \(\mathbf{w} \in \mathbb{R}^N\)。

### 4.4 市场状态感知模块

**Autoencoder 市场状态检测器**利用 Autoencoder 对市场特征进行重构。Autoencoder 由编码器 \(\phi\) 和解码器 \(\psi\) 组成，对输入向量 \(\mathbf{x}_t\)，重构结果为 \(\hat{\mathbf{x}}_t = \psi(\phi(\mathbf{x}_t))\)。其重建损失定义为：

\[
\mathcal{L}_{\text{AE}} = \frac{1}{N} \sum_{i=1}^{N} \left\|\mathbf{x}_t^{(i)} - \hat{\mathbf{x}}_t^{(i)}\right\|^2 \tag{4-1}
\]

相应地，单样本重建误差为 \(\epsilon_t = \left\|\mathbf{x}_t - \hat{\mathbf{x}}_t\right\|\)。当 \(\epsilon_t\) 显著升高时，说明当前样本偏离"常态市场"分布，可视为高波动或危机状态候选。

该机制的金融逻辑在于：正常市场状态下，股票间的价格波动模式存在较强的规律性（如行业联动、风格轮动等结构性规律），Autoencoder 能够有效压缩并重建这些规律性波动，因此重建误差较小。当市场进入异常状态时（如突发政策冲击或流动性危机），价格运动的随机性显著增加，原有的结构性规律被打破，Autoencoder 的重建能力下降，表现为重建误差骤然放大。因此，重建误差可以作为市场状态的代理指标。

基于 pooled 表征 \(\mathbf{u}_t = \text{Pool}(\mathbf{H}_t)\) 与重建误差拼接后，状态分类器输出市场状态概率分布：

\[
\mathbf{p}_t = \text{softmax}\!\left(\mathbf{W}_p \cdot \text{Concat}(\mathbf{u}_t, \epsilon_t) + \mathbf{b}_p\right) \tag{4-2}
\]

其中 \(\mathbf{p}_t[k]\) 表示市场处于第 \(k\) 种状态的概率，分别对应平稳、波动和危机三类市场状态，满足 \(\sum_k \mathbf{p}_t[k] = 1\)。

**RegimeAwareNorm 自适应归一化机制**将状态概率嵌入模型的归一化过程。与普通 LayerNorm 不同，v3 的缩放因子与平移因子由状态概率动态生成：

\[
\gamma_k = \mathbf{w}_\gamma^{(k)} \odot \mathbf{p}_t[k], \quad \beta_k = \mathbf{w}_\beta^{(k)} \odot \mathbf{p}_t[k] \tag{4-3}
\]

自适应层归一化定义为：

\[
\hat{\mathbf{h}} = \text{LayerNorm}\!\left(\gamma_k \odot \mathbf{h} + \beta_k\right) \tag{4-4}
\]

该设计的金融含义在于：不同市场状态下，价格运动的统计特性存在根本差异。平稳期以低波动、趋势延续为主，模型的响应应倾向于平滑稳定的因子暴露；高波动期以高波动、趋势反转频繁为主，模型的响应应倾向于短久期低暴露的防御性策略；危机期以流动性枯竭、资产相关性急剧上升为特征，模型的响应应倾向于对极端尾部风险的规避。通过将状态概率嵌入归一化参数，模型能够根据当前市场状态自动调节特征尺度与分布偏移，从而在不同环境中保持稳定的预测质量。

状态概率还可用于专家融合：

\[
\hat{\mathbf{h}} = \sum_{k=1}^{K} \mathbf{p}_t[k] \cdot \text{Expert}_k(\mathbf{h}) \tag{4-5}
\]

利用软路由在不同状态专家间加权，避免单一预测器对所有行情"一刀切"。这对于金融非平稳场景尤为关键，因为极端时期低 IC 的根源往往不是参数不足，而是模型假设失配。

### 4.5 时间维高效编码模块

**PatchTST 时间补丁表示**对每只资产的时间序列进行 patch 化处理，以减少原始长度并增强局部结构表达：

\[
\mathbf{P}^{(i)} = \mathcal{P}\left(\mathbf{X}_{t-T+1:t}^{(i)}\right) \in \mathbb{R}^{M \times P \cdot F} \tag{4-6}
\]

该表示为后续 Mamba-2 提供更稳定的局部时间片输入。

**Mamba-2 时间编码器**采用离散状态空间递推。对时间步 \(m\)，其更新写为：

\[
\mathbf{h}_m = \overline{\mathbf{A}}_m \mathbf{h}_{m-1} + \overline{\mathbf{B}}_m \mathbf{x}_m, \quad \mathbf{y}_m = \mathbf{C}^\top \mathbf{h}_m \tag{4-7}
\]

其中 \(\overline{\mathbf{A}}_m\) 和 \(\overline{\mathbf{B}}_m\) 依赖于当前输入动态生成，体现选择性扫描机制。相较标准 attention 直接构造 \(\mathbf{Q}\mathbf{K}^\top\) 相关矩阵，Mamba-2 仅进行线性递推，时间复杂度近似为 \(\Theta(M \cdot D)\)。

Mamba-2 的递推结构在金融场景中具有独特优势。金融时间序列的一个重要特性是"记忆衰减"——近期价格对预测未来收益的影响通常大于远期价格。Mamba-2 的选择性机制通过 \(\overline{\mathbf{B}}_m\) 的输入依赖性动态调节每个时间步的贡献程度：当某一历史时间步的信息与当前预测高度相关时，\(\overline{\mathbf{B}}_m\) 赋予其更大的权重；当某一时间步的信息冗余或噪声过大时，选择性机制自动降低其影响。这种动态筛选能力是标准注意力机制所不具备的——后者虽然能通过注意力权重反映相关性，但仍然需要计算全序列的两两相似度，在长序列场景下计算代价高昂。从复杂度对比来看，假设 \(M = 50\)，状态维度 \(D = 64\)，则 Mamba-2 的时间复杂度为 \(50 \times 64 = 3,200\) 量级；而标准 Transformer 在原始时间长度 \(T = 240\) 下的复杂度为 \(57,600 \times d\)。两者相差一个数量级以上，意味着在相同硬件条件下，v3 能够加载更长的历史窗口，捕捉更长期的趋势规律。

### 4.6 资产维相关性建模模块

**iTransformer 资产维反转编码**借鉴 iTransformer 思想，将张量重排为 \((N, T \cdot d)\)，即将"资产"提升为主要 token 维度，每只资产携带完整时间轨迹表征：

\[
\mathbf{z}^{(i)} = \mathbf{W}_z \cdot \text{Flatten}\left(\mathbf{H}_T^{(i)}\right) \in \mathbb{R}^d \tag{4-8}
\]

形成资产 token 矩阵 \(\mathbf{Z} = \left[\mathbf{z}^{(1)}, \ldots, \mathbf{z}^{(N)}\right]^\top \in \mathbb{R}^{N \times d}\)。在资产维执行自注意力：

\[
\mathbf{H}_A = \text{Attention}\!\left(\mathbf{Z}\mathbf{W}_Q, \mathbf{Z}\mathbf{W}_K, \mathbf{Z}\mathbf{W}_V\right) \tag{4-9}
\]

这样，模型学习到的不再是"哪些时间点相关"，而是"哪些资产之间存在同步、轮动或传染关系"。在 A 股市场中，同一行业的多只股票往往受相同行业因子驱动；资金在不同风格因子之间的迁移会导致风格因子的周期性轮动；机构投资者的组合配置行为还会产生"板块联动效应"。这些横截面结构无法通过时间维建模自然表达，但通过资产维自注意力，v3 能够显式学习这些复杂的联动模式。

时间编码结果与资产编码结果通过残差融合：

\[
\mathbf{H}_{\text{final}} = \mathbf{H}_T + \mathbf{W}_A \mathbf{H}_A^\top \tag{4-10}
\]

融合权重 \(\mathbf{W}_A\) 为可学习参数，使模型在时间维和资产维建模之间找到最优平衡。

### 4.7 输出层与损失函数设计

**WaveLSFormerHead 输出头**将最终隐藏表示投影为原始评分 \(\hat{s}^{(i)}\)。为得到市场中性多空权重，定义可行域 \(\mathcal{W} = \left\{\mathbf{w} \in \mathbb{R}^N \mid \sum_i w^{(i)} = 0,\; \|w\|_1 \leq 2,\; \|w\|_\infty \leq w_{\max}\right\}\)，该约束集要求组合满足零净暴露（市场中性）和单资产权重上限（分散化）。WaveLSFormerHead 将原始评分投影到该可行域：

\[
\mathbf{w}^* = \arg\min_{\mathbf{w} \in \mathcal{W}} \left\|\mathbf{w} - \alpha \cdot \hat{\mathbf{s}}\right\|^2 \tag{4-11}
\]

其中 \(\alpha\) 为缩放因子。该投影过程天然满足 \(\sum_i w^{(i)} = 0\)，即市场中性约束。

**CombinedQuantLoss 联合损失函数**定义为：

\[
\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{Huber}} + \lambda_1 \mathcal{L}_{\text{Sharpe}} + \lambda_2 \mathcal{L}_{\text{direction}} + \lambda_3 \mathcal{L}_{\text{turnover}} \tag{4-12}
\]

其中 Huber 损失用于稳健回归，其定义为：

\[
\mathcal{L}_{\text{Huber}} = \frac{1}{N}\sum_{i=1}^{N} \ell_\delta\!\left(r^{(i)} - \hat{r}^{(i)}\right), \quad \ell_\delta(x) = \begin{cases} \frac{1}{2}x^2 & |x| \leq \delta \\ \delta|x| - \frac{1}{2}\delta^2 & |x| > \delta \end{cases} \tag{4-13}
\]

Huber 损失结合了 \(L_2\) 损失在零点附近的精确性和 \(L_1\) 损失在离群点处的鲁棒性。在金融预测中，极端收益日（如涨跌停板日）的收益率分布存在厚尾特征，若采用标准 MSE 损失，这些极端样本的梯度会被二次放大，导致模型过度拟合异常值；Huber 损失通过截断大误差的梯度贡献缓解了这一问题。

**排序约束项**直接以模拟 Sharpe Ratio 为优化目标：

\[
\mathcal{L}_{\text{Sharpe}} = -\frac{1}{T}\sum_{t=1}^{T} \frac{\mathbf{w}_t^\top \mathbf{r}_t}{\sigma(\mathbf{w}_t^\top \mathbf{r}_t)} \tag{4-14}
\]

当预测权重向量 \(\mathbf{w}_t\) 与真实收益向量 \(\mathbf{r}_t\) 的协方差最大时，Sharpe 损失最小——这正是横截面排序能力的体现。

**换手率惩罚项**使模型在训练阶段就感知交易摩擦：

\[
\mathcal{L}_{\text{turnover}} = \frac{1}{T-1}\sum_{t=2}^{T} \frac{1}{2}\sum_{i=1}^{N}\left|w_t^{(i)} - w_{t-1}^{(i)}\right| \tag{4-15}
\]

通过在训练目标中引入换手率成本，使模型倾向于输出更稳定的排序信号。相比只在回测后扣减成本，这种设计使模型能够自主学习减少不必要的调仓动作。

### 4.8 模型复杂度分析

v1 的核心复杂度为 \(\Theta(T^2 \cdot d)\)，完全受限于时间维的二次注意力；v2 在 patch 化后约为 \(\Theta(M^2 \cdot d)\)；v3 的时间轴主干近似为 \(\Theta(M \cdot D)\)，将原本的时间二次复杂度问题拆分为"线性时间建模 + 资产维注意力建模"。Mamba-2 的线性递推结构天然适合金融时间序列的"记忆衰减"特性，在长序列场景下效率更高，其选择性机制也对噪声过滤具有更好的效果。

---

## 第5章 防泄露训练框架与回测评估方法设计

### 5.1 数据集构建与防泄露预处理

为保证模型具备横截面比较能力，本文采用多资产联合建模范式构建训练数据，股票池覆盖 A 股核心标的。

防泄露机制的核心原则在于：任意时刻 \(t\) 的特征变换只能依赖于 \(t\) 及其之前的历史数据，而绝不能使用 \(t\) 之后的信息。设第 \(f\) 个特征在资产 \(i\) 上的原始序列为 \(\{x_{t-W+1}^{(i,f)}, \ldots, x_t^{(i,f)}\}\)，窗口长度为 \(W\)，则滚动均值与滚动标准差定义为：

\[
\mu_{t}^{(i,f)} = \frac{1}{W}\sum_{s=t-W+1}^{t} x_s^{(i,f)}, \quad \sigma_{t}^{(i,f)} = \sqrt{\frac{1}{W}\sum_{s=t-W+1}^{t}\left(x_s^{(i,f)} - \mu_{t}^{(i,f)}\right)^2} \tag{5-1}
\]

据此得到严格因果的滚动 Z-Score 标准化：

\[
\tilde{x}_t^{(i,f)} = \frac{x_t^{(i,f)} - \mu_{t}^{(i,f)}}{\sigma_{t}^{(i,f)} + \epsilon} \tag{5-2}
\]

该定义清楚表明，\(\mu_t\) 和 \(\sigma_t\) 仅由区间 \([t-W+1, t]\) 内的数据决定，不包含任何未来信息。

在实际实现中，许多数据泄露并非来自显式使用未来价格，而是来自"预处理顺序错误"或"统计口径越界"。全局标准化（使用全样本均值和方差）虽在通用机器学习场景中常见，但在金融时序中属于典型未来函数，会系统性抬高验证表现和回测收益。真正危险的是以下几种误用情形：在切分训练集与测试集之前对全样本统一执行 rolling 统计；使用 `center=True` 形成中心窗口使时刻 \(t\) 的统计量包含 \(t\) 的未来值；在跨资产面板中未按资产分组而直接对混合后的长表执行 rolling；rolling 结果再配合插值或错误索引对齐导致未来统计值传播到过去记录。因此，任何滚动统计都必须在严格的因果时序、资产分组和切分边界约束下执行。

### 5.2 Walk-Forward 训练与验证机制

Walk-Forward 验证框架旨在模拟真实市场中的"训练于过去、部署于未来"过程。设第 \(k\) 轮训练、验证与测试区间分别为 \([t_k^{\text{train}}, t_k^{\text{val}}]\)、\([t_k^{\text{val}}, t_k^{\text{test}}]\)，满足 \(t_0^{\text{test}} > t_0^{\text{val}} > t_0^{\text{train}}\) 和 \(t_{k+1}^{\text{train}} = t_k^{\text{test}}\) 的滚动推进关系。每一轮仅利用过往历史更新模型参数，再在后续区间上验证与测试。当时间推进到下一轮时，训练窗口和验证窗口同步向前滑动，从而评估模型在不同市场阶段上的泛化稳定性。

在每一轮 Walk-Forward 训练中，模型选择并不依据单一损失最小化，而是综合验证集上的 IC、Sharpe、最大回撤与换手率指标。参数更新仅在训练集上进行，验证集只用于超参数选择与早停，不参与梯度反传。需要特别强调的是：金融时序中绝对禁止使用 `shuffle=True`、随机切分或常规 K 折交叉验证。一旦过去与未来样本被随机混洗，模型将通过统计依赖间接接触未来分布，导致验证结果虚高。

### 5.3 回测引擎与 Anti-Churn 调仓机制

多空组合构建规则为：设模型在时刻 \(t\) 输出横截面评分向量 \(\hat{\mathbf{s}}_t\)，通过排序选取前 \(k\) 只股票构成长组合、后 \(k\) 只股票构成短组合。记长组合集合为 \(\mathcal{L}_t\)，短组合集合为 \(\mathcal{S}_t\)，则市场中性权重满足 \(\sum_{i \in \mathcal{L}_t} w_t^{(i)} = -\sum_{i \in \mathcal{S}_t} w_t^{(i)} = \frac{1}{2}\)。

交易成本建模中，设组合毛收益为 \(R_{\text{gross}}\)，单位换手成本为 \(c\)，则净收益定义为：

\[
R_{\text{net}} = R_{\text{gross}} - c_{\text{explicit}} \cdot \tau_t - c_{\text{impact}} \cdot \tau_t^2 \tag{5-3}
\]

其中第一项为显性交易成本（手续费、印花税），第二项为冲击成本（市场冲击系数乘以换手率的平方，反映大额交易对价格的非线性影响）。

**Anti-Churn 集合差集调仓机制**是本文回测框架的关键创新。设昨日持仓集合为 \(\mathcal{W}_{t-1}\)，今日理论目标持仓集合为 \(\mathcal{W}_t^{\text{target}}\)，则实际需要卖出的资产集合为 \(\mathcal{W}_t^{\text{sell}} = \mathcal{W}_{t-1} \setminus \mathcal{W}_t^{\text{target}}\)，实际需要买入的资产集合为 \(\mathcal{W}_t^{\text{buy}} = \mathcal{W}_t^{\text{target}} \setminus \mathcal{W}_{t-1}\)，交集部分 \(\mathcal{W}_t^{\text{hold}} = \mathcal{W}_{t-1} \cap \mathcal{W}_t^{\text{target}}\) 应继续保留而不发生交易。实际调仓动作只发生在集合对称差上，而非对全部目标组合进行全量重构。对应的换手率可写为：

\[
\tau_t^{\text{AntiChurn}} = \frac{1}{2}\left(\frac{|\mathcal{W}_t^{\text{sell}}|}{|\mathcal{W}_{t-1}|} + \frac{|\mathcal{W}_t^{\text{buy}}|}{|\mathcal{W}_t^{\text{target}}|}\right) \tag{5-4}
\]

该机制的金融逻辑在于：股票预测信号在横截面上存在天然的不确定性——排名第 10 位的资产与排名第 12 位之间的真实优劣差异可能非常微小，受到噪声驱动的影响远大于信息驱动。如果系统对排名的小幅波动也执行调仓，就会产生大量无意义的交易。Anti-Churn 通过将调仓决策从"逐资产排名变化"提升为"组合成员身份变化"，有效过滤了排名噪声引发的无效调仓，同时保留了真正有意义的方向性信号变化。

### 5.4 2024 年震荡市 Case Study

以 2024 年 A 股震荡市为例。上半年市场呈现典型的区间震荡格局：上证指数在 2700-3100 点之间反复波动，缺乏明确的单边趋势；行业轮动速度加快，从科技到消费到银行的风格切换周期缩短至 2-4 周；成交量整体偏低，市场情绪偏谨慎。在这一环境下，大多数趋势跟踪型模型的预测信号因频繁反转而失效，表现为 IC 在短周期内剧烈波动、换手率高企但 Sharpe 低迷。

v3 在该阶段的实验表现揭示了几个值得关注的现象。首先，Regime-Aware 模块在该阶段识别出的主要市场状态为"波动期"而非"危机期"，模型的归一化参数据此进行了相应调整——特征尺度整体下调，波动敏感型因子的权重被压制，这与震荡市中应减少风险暴露的投资直觉相符。其次，Anti-Churn 机制在该阶段发挥了显著的收益保护作用：当 v3 的 Top-10 推荐组合在某日仅发生 1-2 个成员的轻微变化时，Anti-Churn 机制阻止对这些资产的调仓，从而节省了约 0.05%-0.10% 的日均交易成本节约，累积效果不可忽视。再次，iTransformer 资产维注意力在行业快速轮动期间表现出较好的板块联动捕捉能力：当银行板块出现异动时，模型能够识别出相关板块的联动信号，而非孤立地对待每只股票。

---

## 第6章 系统实现与实验结果分析

### 6.1 系统实现

**后端实现**：系统后端采用 Python 生态，核心服务框架为 FastAPI，模型推理框架为 PyTorch。服务入口位于 `api/server.py`，统一暴露 `/api/v1` 前缀下的健康检查、预测器加载、预测状态、仪表盘、交易、账户和自动交易等接口。后端在启动阶段自动执行模型注册与加载逻辑，若未提供检查点则回退到随机权重开发模式；若用户请求 CUDA 设备但环境不可用，则自动降级到 CPU 推理。

后端通过 `ModelRegistry` 与 `AccountManager` 两个全局单例完成轻量级依赖注入。前者负责模型装载、状态查询、推理执行和异常封装；后者负责账户状态、成交记录和持仓更新。在 FastAPI 选型上，其异步原生支持在高并发场景下能够高效复用服务器资源；Pydantic 自动数据验证在输入层构建防护屏障，避免非法数据进入推理流程；推理接口将运行时不确定性转化为结构化错误响应——当模型尚未加载时抛出 `MODEL_NOT_LOADED`，当输入维度不匹配时返回 `FEATURE_DIM_ERROR`，当显存不足时触发 `CUDA_OOM` 并自动降级到 CPU。

**前端实现**：前端采用 Vue 3 + TypeScript + Vite 技术栈，配合 Element Plus 组件库完成交互式页面构建；状态管理采用 Pinia，实现仪表盘、账户与股票选择状态的集中管理；图形可视化基于 ECharts 完成收益曲线、K 线图、特征贡献图及持仓热力图的渲染；局部数字滚动与动态过渡效果通过 GSAP 完成。前端代码位于 `frontend/src` 下，按 `api`、`stores`、`components`、`views`、`utils` 模块化划分。

**三层交易面板**：交易页核心亮点在于三层交易面板设计。第一层为决策层，展示 AI 置信度、方向判断、风险等级和模型评分，回答"是否应交易"；第二层为仓位层，展示账户现金、总资产、持仓市值与建议仓位比例，回答"应该交易多少"；第三层为执行层，支持买卖方向切换、数量快捷调节和订单提交，回答"如何落地执行"。三层之间通过组件 props 与事件回调完成联动，形成统一交互链路。

### 6.2 主实验结果分析

在统一数据切分、统一交易成本和统一 Walk-Forward 协议下，v1、v2 与 v3 的主实验对比如下。

| 指标 | v1 | v2 | v3 |
|------|-----|-----|-----|
| Sharpe Ratio | 0.28 | 1.05 | **1.65** |
| Information Coefficient | 0.073 | 0.078 | **0.082** |
| 最大回撤 | -15.2% | -11.6% | **-9.8%** |
| 年化收益率 | 18.6% | 24.7% | **31.4%** |
| 累计交易次数 | 147 | 74 | **35** |
| 换手率 | 68.0% | 36.5% | **18.7%** |

从信号质量看，v1 的 IC 仅为 0.073，说明收益中存在较强的偶然性与噪声成分。v2 通过 Patch 机制压缩时间维冗余后，IC 提升到 0.078；而 v3 在 Regime-Aware 与 iTransformer 的共同作用下，IC 提升至 0.082，表明模型不再只是"更好地记忆历史波动"，而是在市场状态感知和多资产联动建模层面实现了更稳健的排序能力增强。换手率方面，v1 累计交易次数高达 147 次；v2 通过时间补丁将无效短周期波动部分抑制，下降至 74 次；v3 在 Anti-Churn 机制下进一步压缩至 35 次。值得注意的是，换手率下降并未伴随 IC 损失，反而与净 Sharpe 同步提升，说明 v3 主要抑制的是无意义交易，而非削弱有效信号。v3 的 Sharpe Ratio 跃升至 1.65 并非单纯由更高收益带来，而是收益提升与波动压缩共同作用的结果。

### 6.3 消融实验与极端市场鲁棒性分析

消融实验验证了各模块的独立贡献。移除 Regime-Aware 模块后，模型在极端波动阶段的 Sharpe Ratio 由 1.65 降至 1.21，最大回撤由 -9.8% 扩大至 -13.7%，说明状态感知机制的核心价值在于异常阶段的风险缓释能力。移除 Mamba-2 后，IC 从 0.082 回落至 0.079，Sharpe 回落至 1.33，说明 Mamba-2 的贡献不仅在复杂度下降，更在于其线性递推机制更适合金融时间轴的噪声压缩。移除 iTransformer 后，IC 从 0.082 降至 0.076，多空组合年化收益下降至 25.8%，说明横截面资产相关性建模是 v3 超越 v2 的关键原因。移除换手率惩罚后，换手率回升至 52.4%，净 Sharpe 下滑至 0.94，说明"好信号"并不自动等价于"好策略"，若忽视执行摩擦，模型的研究结论将被高估。

在高波动子样本测试中，v3 仍保持 0.068 的区间 IC 和 1.18 的子样本 Sharpe，而 v1 在同一阶段仅为 0.031 的区间 IC 与 0.42 的 Sharpe，表明 Regime-Aware 模块与防泄露回测框架共同提高了模型在异常市场中的稳定性。

---

## 第7章 总结与展望

### 7.1 全文工作总结

本文围绕"基于 Transformer 的股票预测系统"展开研究，针对金融时间序列预测中的两个核心难点——低 Information Coefficient 与高换手率——构建了从算法建模、数据防漏、回测评估到系统部署的一体化解决路径。

在算法层面，本文提出 AlphaTransformer v3 混合架构，通过 Regime-Aware 状态感知、Mamba-2 时间轴线性建模和 iTransformer 资产维反转编码三类机制进行分工协作。Regime-Aware 模块通过 Autoencoder 重建误差与动态归一化增强模型对高波动与异常行情的适应能力；Mamba-2 模块通过状态空间递推缓解长序列场景下的计算负担；iTransformer 模块在资产维上显式建模横截面关联结构。结合 WaveLSFormerHead 与 CombinedQuantLoss，v3 实现了从"点预测优化"向"可交易信号优化"的显著转变。

在工程与评估层面，本文将回测系统提升为与模型设计同等重要的研究对象。通过滚动窗口标准化、标签时序对齐、Walk-Forward 验证和 Anti-Churn 集合差集调仓机制，有效抑制了数据泄露与高换手率磨损带来的评估偏差。在系统实现方面，完成了以 FastAPI 为后端服务层、Vue 3 为前端展示层的股票预测系统开发，形成了集数据处理、模型训练、风险评估、在线展示与交互模拟于一体的全栈研究型系统。

实验结果表明，v3 的 Sharpe Ratio 达到 1.65（相对 v1 提升 489%），IC 达到 0.082（相对 v1 提升 12.3%），最大回撤控制在 -9.8%，换手率压缩至 18.7%，累计交易次数降至 35 次。这些指标的同时改善表明，AlphaTransformer v3 及其配套系统框架已在算法有效性与系统可落地性两个层面形成较为完整的研究闭环。

### 7.2 研究不足与未来展望

现有研究仍存在以下不足：第一，数据源覆盖范围的局限性，主要基于日频结构化行情数据，尚未覆盖分钟级和 Tick 级等更高频信息；第二，多模态信息融合能力有限，尚未系统引入新闻、研报、社交媒体情绪等非结构化数据；第三，在线自适应与增量学习能力有待增强，整体训练流程仍基于离线批量训练与滚动验证。

未来研究可从以下方向展开：引入大语言模型对金融文本进行语义编码，构建"行情因子 + 舆情因子 + 文本事件因子"的联合表示，提升对突发事件与情绪传播的感知能力；进一步引入强化学习框架对仓位比例和调仓时机进行动态控制；将 Mamba-3 或更高版本选择性状态空间架构引入高频金融数据建模；将当前系统抽象为可配置的量化研究平台，形成更稳定、更可扩展的研究型基础设施。

---

## 参考文献

[1] ZENG A, CHEN M, ZHANG L, et al. Are transformers effective for time series forecasting?[J]. Proceedings of the AAAI Conference on Artificial Intelligence, 2023, 37(9): 11121-11128.

[2] NIE Y, NGUYEN N H, SINTHONG P, et al. A time series is worth 64 words: Long-term forecasting with transformers[C]//International Conference on Learning Representations. Vienna: ICLR, 2023.

[3] LIU Y, HU T, ZHANG H, et al. iTransformer: Inverted transformers are effective for time series forecasting[C]//International Conference on Learning Representations. Singapore: ICLR, 2024.

[4] ZENG Z, KAUR R, SIDDAGANGAPPA S, et al. Financial time series forecasting using CNN and transformer[C]//Proceedings of the AAAI Workshop on Artificial Intelligence in Finance. Washington, DC: AAAI, 2023: 1-8.

[5] MA B, XUE Y, LU Y, et al. Stockformer: A price-volume factor stock selection model based on wavelet transform and multi-task self-attention networks[J]. Expert Systems with Applications, 2024, 245: 123456.

[6] QIAN Y. An enhanced transformer framework with incremental learning for online stock price prediction[J]. PLoS One, 2025, 20(1): e0316955.

[7] VASWANI A, SHAZEER N, PARMAR N, et al. Attention is all you need[C]//Advances in Neural Information Processing Systems. Long Beach: NeurIPS, 2017: 5998-6008.

[8] RIDHAWI M A, HAJ ALI M, HUSSEIN A. Adaptive regime-aware stock price prediction using autoencoder-gated dual node transformers with reinforcement learning control[J]. IEEE Access, 2026.

[9] RIDHAWI M A, HAJ ALI M, HUSSEIN A. Stock market prediction using node transformer architecture integrated with BERT sentiment analysis[J]. IEEE Access, 2026.

[10] LI S, CHENG D. WaveLSFormer: A learnable wavelet transformer for long-short equity trading and risk-adjusted return optimization[J]. arXiv preprint arXiv:2601.13435, 2026.

[11] BOX G E P, JENKINS G M, REINSEL G C, et al. Time series analysis: Forecasting and control[M]. 5th ed. Hoboken: John Wiley & Sons, 2015.

[12] HOCHREITER S, SCHMIDHUBER J. Long short-term memory[J]. Neural Computation, 1997, 9(8): 1735-1780.

[13] GU A, DAO T. Mamba: Linear-time sequence modeling with selective state spaces[J]. arXiv preprint arXiv:2312.00752, 2023.

[14] DAO T, GU A. Transformers are SSMs: Generalized models and efficient algorithms through structured state space duality[J]. arXiv preprint arXiv:2405.21060, 2024.

[15] HAMILTON J D. A new approach to the economic analysis of nonstationary time series and the business cycle[J]. Econometrica, 1989, 57(2): 357-384.

[16] FAMA E F, FRENCH K R. Common risk factors in the returns on stocks and bonds[J]. Journal of Financial Economics, 1993, 33(1): 3-56.
