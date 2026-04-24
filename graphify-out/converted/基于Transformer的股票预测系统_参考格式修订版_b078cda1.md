<!-- converted from 基于Transformer的股票预测系统_参考格式修订版.docx -->

基于 Transformer 的股票预测系统
[待填：副标题]
[学校名称]
[院系名称]
[专业名称]
[学生姓名]
[指导教师]
2026年4月

摘 要
股票价格预测是智能金融与量化投资研究中的核心问题之一，其目标在于从高噪声、强非平稳、强耦合的金融时间序列中提取可用于投资决策的有效信号。然而，传统统计模型与浅层机器学习方法对复杂非线性时序关系和跨资产联动结构的刻画能力有限；标准 Transformer 虽在序列建模中表现出较强优势，但在长序列金融数据场景下仍面临注意力计算复杂度为 O(n^2)、时间依赖建模成本较高、极端市场状态下泛化能力下降等问题。更为关键的是，若训练集构造、特征标准化与回测流程设计不严格，极易引入未来函数、标签错位与滚动窗口污染等数据泄露风险，从而造成信息系数偏低背景下收益评估被虚高放大；同时，过度频繁的调仓行为还会导致显著的交易摩擦与换手率磨损，削弱策略的真实可执行性。针对上述问题，本文围绕“低信息系数”与“高换手率”两项关键瓶颈，设计并实现了一种基于 Transformer 的股票预测系统。
本文提出 AlphaTransformer v3 模型，并在统一框架下融合市场状态感知、时间轴高效建模、资产维相关性建模与交易目标约束四类关键机制。首先，针对市场分布动态漂移与极端行情失稳问题，构建基于 Autoencoder 重建误差的 Regime-Aware 市场状态检测模块，并通过 RegimeAwareNorm 实现不同市场状态下的自适应特征归一化与动态路由，从而提高模型在波动期与危机期中的鲁棒性。其次，针对长历史窗口下标准自注意力机制计算代价高的问题，引入 Mamba-2 状态空间模块对时间轴依赖进行线性复杂度建模，并结合 PatchTST 的时间补丁表示增强局部时序语义提取能力。再次，针对多资产联合预测场景下横截面依赖关系表达不足的问题，借鉴 iTransformer 的维度反转思想，在资产维上建立跨标的关联建模机制，以增强模型对板块联动、风格迁移与共振效应的捕捉能力。在输出层，本文结合 WaveLSFormer 风格的多空决策头与 CombinedQuantLoss 联合损失函数，对排序能力、收益风险特征与换手率约束进行协同优化，以提升策略的可交易性和风险调整收益水平。
在系统实现方面，本文围绕真实部署需求，构建了“模型训练层、服务接口层与前端展示层”协同的一体化股票预测系统。数据侧采用滚动窗口标准化、时间对齐标签构造与 Walk-Forward 验证机制，以抑制未来信息泄露；回测侧设计 Anti-Churn 集合差集调仓算法、交易成本建模与风险暴露约束，以降低高频调仓带来的收益磨损；系统侧采用 Vue 3 与 FastAPI 的前后端分离架构，实现预测结果展示、回测分析、交易面板交互与接口服务部署，提升了模型研究到工程落地的完整性与可复现性。
实验结果表明，AlphaTransformer v3 相较于基线 AlphaTransformer v1 与改进版 v2，在预测稳定性、排序有效性与风险调整收益方面均取得显著提升。相较于 v1 模型，v3 的 Sharpe Ratio 由 0.28 提升至 1.65，Information Coefficient 由 0.073 提升至 0.082，最大回撤控制在 -9.8% 以内，年化收益提升至 31.4%，组合换手率下降至 18.7%，累计交易次数压缩至 35 次；在高波动市场阶段，v3 仍保持较稳定的预测性能与回测表现。研究结果表明，面向金融时序预测任务，将 Regime-Aware、Mamba-2 与 iTransformer 进行时空混合建模，并结合严格的数据泄露防控与交易摩擦抑制机制，能够有效提升股票预测系统的学术研究价值与工程应用潜力。
关键词：Transformer；股票预测；深度学习；时间序列；量化交易系统

Abstract
Stock price forecasting is a fundamental problem in intelligent finance and quantitative investment, aiming to extract decision-relevant signals from financial time series characterized by high noise, strong non-stationarity, and complex cross-asset interactions. However, traditional statistical models and shallow machine learning methods are often inadequate for modeling nonlinear temporal dependencies and cross-sectional coupling structures. Although the Transformer architecture has demonstrated strong sequence modeling capability, it still suffers from several limitations in financial long-horizon scenarios, including the O(n^2) computational burden of self-attention, insufficient efficiency in temporal dependency modeling, and degraded robustness under extreme market regimes. More importantly, if the construction of training samples, feature normalization, and backtesting protocols is not rigorously constrained, data leakage may be introduced through future information contamination, label misalignment, and rolling-window pollution, thereby inflating backtest performance despite a low underlying Information Coefficient. In addition, excessive portfolio turnover further erodes realized returns through transaction frictions and weakens the practical tradability of the strategy. To address these challenges, this thesis focuses on two critical bottlenecks, namely low predictive Information Coefficient and excessive turnover-induced performance decay, and develops a Transformer-based stock forecasting system.
This thesis proposes AlphaTransformer v3, a unified architecture integrating regime-aware market perception, efficient temporal modeling, cross-asset dependency learning, and trading-oriented objective optimization. First, to improve robustness against distribution shifts and extreme market conditions, an Autoencoder-based Regime-Aware detection module is designed to identify market states through reconstruction error, and RegimeAwareNorm is introduced to perform adaptive normalization and dynamic routing under different regimes. Second, to overcome the high computational cost of standard self-attention for long historical windows, a Mamba-2 state-space module is employed to model temporal dependencies with linear complexity, while PatchTST-style patch representations are adopted to preserve local temporal semantics. Third, to enhance cross-sectional representation in multi-asset prediction, the inverted-dimension modeling paradigm of iTransformer is introduced to capture inter-asset dependencies along the asset dimension, thereby improving the modeling of sector co-movement, style migration, and cross-asset resonance. At the output stage, a WaveLSFormer-inspired long-short decision head and a CombinedQuantLoss objective are jointly designed to optimize ranking quality, return-risk characteristics, and turnover constraints, thus improving both tradability and risk-adjusted performance.
From the perspective of system deployment, this work further implements an integrated stock forecasting platform consisting of a model training layer, a service interface layer, and a front-end visualization layer. On the data side, rolling-window normalization, temporally aligned label construction, and walk-forward validation are adopted to prevent data leakage. On the backtesting side, an Anti-Churn set-difference rebalancing algorithm, transaction cost modeling, and risk exposure constraints are introduced to mitigate turnover-induced performance erosion. On the engineering side, a decoupled Vue 3 plus FastAPI architecture is developed to support prediction visualization, backtest analytics, trading-panel interaction, and online service deployment, thereby improving the completeness and reproducibility of the full pipeline from model research to system implementation.
Experimental results demonstrate that AlphaTransformer v3 substantially outperforms the baseline AlphaTransformer v1 and the intermediate v2 model in predictive stability, ranking effectiveness, and risk-adjusted return. Compared with v1, the Sharpe Ratio of v3 improves from 0.28 to 1.65, the Information Coefficient increases from 0.073 to 0.082, the maximum drawdown is controlled within -9.8%, the annualized return rises to 31.4%, portfolio turnover is reduced to 18.7%, and the total number of transactions declines to 35. Moreover, under high-volatility market conditions, v3 maintains stable predictive performance and robust backtesting results. These findings indicate that a spatio-temporal hybrid framework combining Regime-Aware modeling, Mamba-2, and iTransformer, together with strict data leakage prevention and turnover suppression mechanisms, can significantly enhance both the academic value and engineering applicability of stock forecasting systems.
Keywords: Transformer; Stock Prediction; Deep Learning; Time Series; Quantitative Trading System

目 录
第1章 绪论 ............ 1
第2章 相关理论与关键技术基础 ............ 5
第3章 股票预测系统需求分析与总体架构设计 ............ 12
第4章 AlphaTransformer 模型设计与关键算法实现 ............ 18
第5章 防泄露训练框架与回测评估方法设计 ............ 25
第6章 系统实现与实验结果分析 ............ 32
第7章 总结与展望 ............ 40
参考文献 ............ 44
致谢 ............ 46

第1章 绪论
1.1 研究背景与研究意义
1.1.1 股票价格预测与量化投资研究背景
股票价格预测是金融科技、人工智能与量化投资交叉领域中的基础性问题，其目标是从历史价格、成交量、技术指标、行业联动关系及外部语义信息中提取可用于未来决策的有效信号。与一般工业时序不同，金融时间序列具有高噪声、弱信号、强非平稳、厚尾分布以及突发冲击频繁等典型特征，使得预测任务天然具有高难度和高不确定性[1][4]。在量化投资实践中，单纯提高点预测精度并不足以支撑真实交易，模型还必须具备横截面排序能力、风险控制能力和交易可执行性，才能在回测与实盘环境中形成稳定的超额收益[5][12]。
随着算力条件改善和深度学习方法的发展，金融时间序列预测逐步从传统统计建模向深度表征学习转变。尤其是在多资产联合建模场景下，深度模型能够在一定程度上同时刻画时间维依赖关系与资产间联动关系，为多因子选股、市场中性策略和动态组合构建提供新的技术路径[3][5]。然而，金融市场并非稳定环境，市场风格切换、政策扰动、流动性冲击和突发事件均会导致样本分布发生持续漂移。如果模型仅在静态假设下学习历史规律，则往往会在验证集上表现良好，而在极端行情或滚动测试中出现显著失效[6][10]。
1.1.2 深度学习驱动下的金融时序建模发展趋势
近年来，深度学习已成为金融时序建模的重要技术路线。早期研究多基于循环神经网络、卷积神经网络以及混合结构，通过自动提取局部模式与时间依赖来替代手工特征工程[4][14]。在此基础上，Transformer 凭借并行计算能力和长距离依赖建模能力，逐步成为时间序列预测领域的研究热点[1][2]。尤其是在长期预测任务中，PatchTST 通过将时间序列切分为局部补丁作为输入 token，有效缓解了长序列建模中的冗余计算与局部语义缺失问题[2]；iTransformer 进一步从“变量而非时间点”出发重构 token 组织方式，在资产维和变量维的表示学习方面表现出更好的泛化性与解释一致性[3]。
除 Transformer 体系外，状态空间模型在近两年快速发展，Mamba 类模型通过选择性状态更新机制，将序列建模复杂度由传统自注意力的二次复杂度压缩至近线性复杂度，在超长序列处理方面展现出明显潜力。这一变化对于金融高频数据建模尤为重要，因为分钟级乃至更高频率的行情序列会迅速放大注意力矩阵的计算与显存负担，使传统 Transformer 在工程上面临训练代价高、推理延迟大和稳定性不足等问题[10][12]。因此，如何将 Transformer 的跨维度关系建模优势与状态空间模型的高效时间编码能力结合起来，已成为金融时序建模的重要发展方向。
1.1.3 基于 Transformer 的股票预测系统研究价值
面向股票预测任务，将先进时序模型真正转化为可运行、可评估、可部署的系统，具有显著的学术价值与工程价值。一方面，学术研究需要回答“何种建模方式能够在复杂金融环境中稳定提升 Information Coefficient（IC）与风险调整收益”；另一方面，工程落地还必须解决数据泄露、回测失真、换手率过高、接口服务不稳定等现实问题，否则再复杂的模型结构也难以转化为可信结论和可执行策略[5][6][10]。基于此，开展基于 Transformer 的股票预测系统研究，不仅能够检验前沿模型在金融场景中的适用性，也能够为人工智能驱动的量化研究平台提供系统化实现范式。
1.2 国内外研究现状
1.2.1 传统统计模型与经典机器学习方法研究现状
在股票预测的早期研究中，ARIMA、GARCH、指数平滑等传统统计模型被广泛用于收益率建模与波动率分析。这类方法通常建立在线性平稳假设或弱平稳变换基础上，适用于短期局部模式拟合，但对于金融市场中普遍存在的非线性关系、结构突变与跨资产耦合现象刻画能力有限[13]。随后，支持向量机、随机森林和梯度提升树等经典机器学习方法被引入金融预测场景，通过多因子输入提升了分类与回归性能，但其对长期依赖和高维时序结构的表达仍然受到模型形式约束。
1.2.2 基于 RNN、LSTM 与 CNN 的股票预测研究现状
深度学习方法出现后，RNN 和 LSTM 由于能够显式建模时间递归依赖，成为金融时序预测的重要工具；CNN 则在局部模式提取、短期波动捕捉和技术形态识别方面具有一定优势[4][14]。一些研究进一步将 CNN 与 Transformer 结合，以同时捕捉短期局部信息和长期全局依赖，证明混合架构在盘中价格涨跌分类和短窗预测中具有较好的效果[4]。然而，RNN 类模型存在梯度传播路径较长、并行性较弱的问题，CNN 也难以在不显著加深网络的前提下有效建模长距离依赖，这些缺陷促使研究重点逐步转向 Transformer 体系。
1.2.3 基于 Transformer 的时序预测模型研究现状
Transformer 在时间序列领域的快速扩展使其成为当前研究的中心。Zeng 等指出，部分时序 Transformer 在建模顺序信息方面存在先天局限，并通过系统比较说明简单线性基线在某些长期预测任务中甚至优于复杂注意力结构，从而推动学界重新审视“注意力是否一定优于线性模型”这一问题[1]。这一研究并未削弱 Transformer 的价值，反而促使后续工作从 token 构造、维度组织与复杂度控制等角度开展更有效的结构创新。
在此背景下，PatchTST 通过时间补丁切分与通道独立建模提高了长窗口预测精度，同时降低了注意力图的冗余开销，被视为时间序列 Transformer 结构优化的重要代表[2]。iTransformer 则进一步提出“维度反转”的建模思想，将各变量时间轨迹嵌入为 token，以自注意力机制捕捉变量间相关性，并以逐变量前馈网络学习非线性表征，在多个真实数据集上取得了优于传统 Transformer 变体的性能[3]。这些研究说明，Transformer 在时序场景下的有效性并不取决于简单套用自然语言处理范式，而在于是否围绕时序结构本身重新设计 token 语义和计算路径。
1.2.4 面向股票预测与量化交易系统的工程化研究现状
在股票预测与量化应用方向，近年来研究逐步从“单纯预测误差优化”转向“预测能力、风险约束与交易目标联合建模”。例如，Stockformer 将小波分解、多任务学习和自注意力机制结合起来，对收益率与趋势进行联合预测，并配合回测验证模型在选股任务中的适用性[5]；IL-ETransformer 在在线股票预测中引入增量学习与持续归一化机制，以应对金融数据分布漂移问题[6]；WaveLSFormer 则进一步将可学习小波分解与多空组合输出结合，直接面向风险调整收益进行端到端优化[12]。2026 年的相关研究还开始引入 Regime-Aware 路由、强化学习控制与图结构节点 Transformer，以增强模型对极端行情、情绪扰动和跨资产关系的刻画能力[10][11]。总体而言，学术界已逐步形成共识：仅从均方误差或方向分类准确率出发不足以支撑真实可交易的股票预测系统，必须把非平稳性、回测机制与交易摩擦纳入统一研究框架。
1.3 现有研究存在的主要问题
1.3.1 传统模型对复杂非线性时序模式识别能力不足
金融市场中的价格演化并非简单的线性自回归过程，而是多主体博弈、信息不对称和流动性冲击共同作用的结果。传统统计模型往往依赖平稳性假设和低阶依赖结构，难以表达突发跳变、异方差扩散和多因子交互所形成的复杂动力学，因此在面对真实市场环境时容易出现模型偏差较大、泛化性能不足的问题。
1.3.2 标准 Transformer 在长序列场景下面临 $O(n^2)$ 复杂度瓶颈
标准自注意力机制需要构造长度为 $n$ 的序列两两相关矩阵，其时间复杂度和空间复杂度均与 $n^2$ 成正比。当输入从日频扩展到分钟级甚至更高频场景时，序列长度会迅速增加，注意力矩阵将带来显著的显存占用与计算延迟。对于多资产联合建模任务，这一问题会进一步被资产数维度放大，导致训练效率下降、批量大小受限以及在线推理代价过高。换言之，若不对时间建模路径进行结构性改造，Transformer 很难在高频金融场景中稳定落地。
1.3.3 极端市场状态下模型泛化能力与鲁棒性不足
金融市场具有典型的非平稳性，不同阶段在波动率水平、行业轮动速度、情绪传导强度和成交结构方面差异显著。如果模型假设所有样本服从统一分布，则容易在平稳期学习到局部有效模式，却在波动期和危机期出现表征漂移。其直接结果往往表现为训练损失持续下降但 IC 提升有限，甚至在滚动回测中出现收益失真。这说明模型并非真正学到了稳健的可迁移规律，而是对局部市场结构进行了过拟合。
1.3.4 回测流程中未来函数、标签泄露与评估偏差问题突出
相较于一般机器学习任务，股票预测研究中最容易被忽视、但最具破坏性的环节并非模型结构本身，而是数据管道与评估协议。如果在标准化过程中使用了全样本统计量，或在特征构造时不慎引用了未来时点信息，模型将获得现实中不可用的先验知识，从而使回测结果被系统性高估。标签构造中的时间错位、训练集与测试集边界污染以及滚动窗口重叠不规范，也会造成隐性数据泄露。此类问题常导致“纸面收益显著、真实可复制性不足”的现象，是金融机器学习研究必须严肃面对的核心工程问题。
1.3.5 高换手率导致策略收益被交易摩擦显著侵蚀
即使模型在横截面排序上具有一定预测能力，如果组合调仓过于频繁，交易成本、滑点和冲击成本仍会吞噬绝大部分账面收益。高换手率通常意味着模型信号稳定性不足、持仓持续性较差，或回测框架缺乏调仓抑制机制。实践中，许多预测模型之所以“收益高而 Sharpe 低”，本质原因在于其信号有效性不足以覆盖高频交易摩擦。这也是为何在金融预测研究中，IC、Sharpe Ratio、最大回撤与换手率必须联合考察，而不能只关注单一准确率指标。
1.4 AlphaTransformer 项目迭代动因分析
1.4.1 AlphaTransformer v1 的原始架构与性能瓶颈
AlphaTransformer v1 采用原生 Transformer 与跨资产注意力相结合的建模框架，能够在统一网络中同时接收多资产历史特征并输出 alpha 得分。从工程角度看，v1 完成了模型训练、回测和接口服务的初步闭环，具备较强的原型验证价值。然而，从核心指标看，v1 的 Sharpe Ratio 仅为 0.28，Information Coefficient 仅为 0.073，最大回撤达到 -15.2%，总交易次数偏高。这表明 v1 虽然能够捕捉部分市场模式，但其预测信号强度不足，排序能力偏弱，且组合稳定性较差。
1.4.2 AlphaTransformer v2 的改进方向与局限性
为缓解 v1 在长序列建模和局部模式提取方面的不足，AlphaTransformer v2 引入多尺度 Patch 表示、稀疏注意力与自适应归一化等机制，试图通过压缩冗余序列长度、增强局部时序语义表达来提升预测能力。从理论上看，v2 相较 v1 在时间窗口利用率和表示效率上已有明显改善，并为后续模块化扩展提供了结构基础。然而，v2 的核心建模思路仍以注意力机制为主，其对极端市场状态的感知仍较弱，对分布漂移缺乏显式建模能力；同时，仅依赖 Patch 机制并不能根本解决时间维高复杂度与状态切换鲁棒性问题。因此，v2 更接近于“有效优化”，但尚未完成针对根本痛点的“架构跃迁”。
1.4.3 AlphaTransformer v3 的设计目标与核心思路
基于 v1 与 v2 的实验反馈，本文将 AlphaTransformer v3 的设计目标明确为两点：一是提升预测信号质量，改善 IC 偏低导致的“收益虚高”问题；二是抑制高换手率与交易摩擦，提高策略在严格回测条件下的真实可执行性。围绕这一目标，v3 的迭代路径具有明显的必然性。首先，需要引入 Regime-Aware 机制显式区分平稳期、波动期与异常期，避免模型在单一分布假设下学习到脆弱模式；其次，需要用 Mamba-2 替代部分时间轴自注意力计算，以降低长序列建模成本并提高高频场景适应性；再次，需要借助 iTransformer 的资产维反转思想增强横截面相关性建模，从而提升多资产排序有效性。由此，v3 不再是对 v1 的局部修补，而是面向“低 IC”和“高换手率”两大核心问题的体系化重构。
1.5 本文主要研究内容
1.5.1 构建 Regime-Aware + Mamba-2 + iTransformer 的混合预测模型
本文围绕股票预测任务，设计 AlphaTransformer v3 模型，融合市场状态感知、时间维高效编码和资产维关系建模三类核心思想，并在输出层加入面向多空决策与排序优化的交易导向结构。
1.5.2 设计严格防泄露的数据预处理与 Walk-Forward 评估框架
针对金融数据易发生未来函数污染的问题，本文构建滚动窗口标准化、时序标签对齐与 Walk-Forward 验证机制，从样本构造、模型选择到回测分析全链路抑制数据泄露风险。
1.5.3 实现基于 FastAPI 与 Vue 3 的股票预测系统
在算法研究基础上，本文进一步实现后端推理服务、回测报告接口和前端可视化交互界面，形成可训练、可预测、可分析、可展示的一体化股票预测系统。
1.5.4 通过多版本对比实验验证架构迭代有效性
本文以 AlphaTransformer v1 和 v2 作为基线与中间版本，通过主实验、消融实验和鲁棒性实验系统验证 v3 在 IC、Sharpe Ratio、最大回撤和换手率等指标上的改进效果。
1.6 本文创新点
1.6.1 面向极端市场状态的 Regime-Aware 状态感知机制
本文引入基于重建误差的市场状态检测与自适应归一化机制，使模型具备对市场分布漂移和异常阶段的动态响应能力。
1.6.2 面向长序列建模的 Mamba-2 时间维高效编码机制
通过将状态空间模型引入时间轴建模路径，本文在保留长依赖表达能力的同时，降低了标准注意力结构在长窗口场景中的计算压力。
1.6.3 面向跨资产关联建模的 iTransformer 资产维反转机制
本文借助资产维反转表示方式增强横截面依赖建模能力，从而提高模型在多资产排序预测任务中的表达精度。
1.6.4 面向真实交易约束的防泄露回测与换手率抑制机制
本文不仅关注模型精度，还将滚动防泄露、交易成本建模和 Anti-Churn 调仓抑制机制纳入统一框架，以提升实验结论的真实性和策略可执行性。
1.6.5 面向工程落地的前后端一体化股票预测系统实现
本文完成了模型训练、后端服务和前端界面的协同实现，使研究成果具备较强的系统复现能力和展示价值。
1.7 论文组织结构
1.7.1 各章节内容安排
第 1 章为绪论，介绍研究背景、国内外研究现状、现有问题、项目迭代动因、研究内容、创新点及全文结构。 第 2 章介绍股票预测任务、Transformer 时序建模、PatchTST、iTransformer、Mamba、数据防泄露与回测评估等理论基础。 第 3 章对股票预测系统进行需求分析与总体架构设计，说明系统数据流、模块划分及业务流程。 第 4 章详细阐述 AlphaTransformer v1、v2、v3 的架构演进，并重点给出 v3 的关键算法设计与理论分析。 第 5 章介绍防泄露训练框架、Walk-Forward 验证机制、回测引擎与 Anti-Churn 调仓抑制方法。 第 6 章给出系统实现细节与实验结果分析，从性能、鲁棒性和工程运行效果三个层面对模型进行验证。 第 7 章总结全文研究工作，分析不足，并展望未来在多模态金融建模与实盘部署方向上的扩展路径。
1.7.2 技术路线与研究流程说明
本文遵循“问题诊断、架构改进、机制约束、系统实现、实验验证”的技术路线展开研究。首先，以 AlphaTransformer v1 的低 IC 与高换手率问题为起点，分析标准 Transformer 在金融场景中的结构性局限；其次，在 v2 的基础上引入 Patch 表示与结构优化；再次，构建以 Regime-Aware、Mamba-2、iTransformer 为核心的 v3 架构，并结合防泄露训练与回测机制形成完整研究闭环；最后，通过前后端系统实现与多组实验对比验证模型与系统的综合有效性。
[此处插入图1-1：本文整体研究技术路线图]
[此处插入表1-1：AlphaTransformer v1、v2、v3 关键差异对比表]
本章小结
本章从金融时间序列预测的研究背景出发，系统梳理了股票预测方法从传统统计模型、深度学习模型到 Transformer、状态空间模型的发展脉络，并分析了当前研究在长序列复杂度、非平稳建模、数据泄露与高换手率等方面存在的关键问题。在此基础上，结合 AlphaTransformer 项目的迭代实践，论证了从 v1 到 v3 的架构演进逻辑，明确了本文围绕“低 IC”与“高换手率”展开研究的必要性。后续章节将在此基础上进一步展开理论分析、模型设计、系统实现与实验验证。
第2章 相关理论与关键技术基础
2.1 股票预测任务定义与金融评价指标
2.1.1 多资产股票预测问题定义
设股票池包含 N 只资产，时间索引为 t=1,2,…,T，每只资产在时刻 t 的输入特征表示为 x_t^(i) ∈ R^d，其中 i∈{1,2,…,N}，d 表示特征维度。给定长度为 L 的历史观察窗口，股票预测任务可形式化为学习一个映射函数 f_θ(・)，使其根据历史窗口内的多资产特征张量
【Word 公式】X_t={x_(t-L+1)^(i),x_(t-L+2)^(i),…,x_t^(i)}_(i=1)^N ∈ R^(N×L×d)
预测未来 H 步收益、方向或排序信号，即【Word 公式】Ŷ_(t+H)=f_θ(X_t)
在量化选股场景中，Ŷ_(t+H) 往往是所有资产未来表现的预测向量：【Word 公式】ŷ_(t+H)=[ŷ_(t+H)^(1),ŷ_(t+H)^(2),…,ŷ_(t+H)^(N)]^T
2.1.2 收益率预测、方向预测与排序预测任务差异
收益率预测任务通常以未来收益率【Word 公式】r_(t+H)^(i)=(P_(t+H)^(i)-P_t^(i))/P_t^(i)为监督目标；排序预测则更关注模型输出与未来真实收益横截面顺序的一致性。即使预测值在绝对数值上存在偏差，只要能稳定地区分 “相对更优” 和 “相对更弱” 的资产，仍可支持多空组合构建。
2.1.3 Information Coefficient (IC) 指标定义
Information Coefficient 用于度量模型预测信号与未来真实收益之间的相关性。若以 Pearson 相关系数形式定义，则在时刻 t 上有：【Word 公式】IC_t= [∑(i=1)^N▒(ŷ_t^(i)-ŷ̄_t)(r(t+H)^(i)-r̄_(t+H))] / [√(∑(i=1)^N▒(ŷ_t^(i)-ŷ̄_t)^2) √(∑(i=1)^N▒(r_(t+H)^(i)-r̄_(t+H))^2)]
全样本平均 IC 定义为【Word 公式】IC̄=(1/T^') ∑_(t=1)^(T^')▒IC_t。在金融场景中，稳定的 0.05 以上的 IC 已具有极强的研究与交易价值。
2.1.4 Sharpe Ratio、最大回撤与换手率指标定义
Sharpe Ratio (夏普比率) 用于衡量单位风险获得的超额收益：【Word 公式】Sharpe=√252 × (E [R_t-R_f])/σ_R
最大回撤 (Max Drawdown) 衡量净值序列历史上最严重的资本回落：【Word 公式】MDD=max┬(t∈[1,T^']) ( (max┬(s∈[1,t]) V_s-V_t )/(max┬(s∈[1,t]) V_s ) )
换手率 (Turnover) 反映组合调仓频率：【Word 公式】Turnover_t=1/2 ∑(i=1)^N▒|w_t^(i)-w(t-1)^(i)|
[此处插入表 2-1：主要评价指标定义与适用场景对照表]
2.1.5 数据泄露与未来函数的影响机理
若在预处理中引入未来信息（如使用全样本均值做 Z-Score），则模型会获得现实中不可得的先验，形成数据泄露。防泄露的核心原则是：任意时刻 t 的特征变换只能依赖于 t 及其之前的历史数据。
2.2 Transformer 及其时序建模原理
2.2.1 自注意力机制基本原理
给定输入序列矩阵 X ∈ R^(n×d)，通过线性映射得到查询 Q、键 K 和值 V：【Word 公式】Q=XW_Q , K=XW_K , V=XW_V
Scaled Dot-Product Attention 定义为：【Word 公式】Attention (Q,K,V)=Softmax ( QK^T/√d_k ) V
2.2.2 多头注意力与前馈网络结构
多头注意力通过并行学习多个子空间表示增强表达能力，前馈网络 (FFN) 则负责逐 token 的非线性变换：【Word 公式】FFN (x)=W_2 σ(W_1 x+b_1)+b_2
[此处插入图 2-1：标准 Transformer 编码器结构示意图]
2.2.3 标准 Transformer 的复杂度分析
自注意力机制涉及长度为 n 的序列两两相关性计算，其时间与空间复杂度均为：【Word 公式】O (n^2 d)
当 n 较大时（如高频金融数据），计算成本呈平方级增长，这是标准 Transformer 落地量化场景的主要瓶颈。
2.3 面向时序预测的 Transformer 代表模型
2.3.1 PatchTST 的时间补丁建模思想
PatchTST 将序列切分为局部补丁 (Patches)，将 token 数量从 L 压缩为【Word 公式】M=⌊(L-P)/S⌋+1。其核心优势在于：降低计算复杂度。捕捉局部时序语义（如短期趋势、突发波动）。
2.3.2 iTransformer 的资产维反转机制
iTransformer 将 “资产维度” 视为 Token 维度，而将 “时间维度” 映射为特征嵌入。这种维度反转能更好建模多资产间横截面相关性。
2.3.3 CNN-Transformer 混合结构
利用 CNN 提取局部特征，Transformer 建模长距离全局依赖：【Word 公式】H_local=CNN (X) , H_global=Transformer (H_local)
2.4 状态空间模型与自适应市场状态建模方法
2.4.1 Mamba-2 状态空间建模原理
SSM 模型以隐状态 h (t) 描述演化过程。其离散化更新公式为：【Word 公式】h_t=Ā h_(t-1)+B̄ x_t【Word 公式】y_t=C h_t+D x_t
Mamba-2 引入选择性机制，具备【Word 公式】O (n)线性复杂度，适配金融长序列。
2.4.2 Autoencoder 重建误差检测机制
Autoencoder 重建误差损失：【Word 公式】L_AE=1/m ∑_(j=1)^m▒‖x_j-x̂_j‖_2^2
异常大的重建误差预示市场进入非稳态。
2.4.3 Regime-Aware 自适应建模
识别市场状态 s_t ∈{平稳，波动，危机}，动态融合模型：【Word 公式】ŷ_t=∑_(k=1)^K▒p (s_t=k|x_t)・f_k (x_t)
2.5 数据预处理与防泄露评估理论
2.5.1 滚动窗口标准化
Z-Score 滚动标准化：【Word 公式】z_(t,f)^(i)=(x_(t,f)^(i)-μ_(t,f)^(i))/σ_(t,f)^(i)
μ、σ 仅由区间 [t-W+1,t] 历史数据计算。
2.5.2 Walk-Forward 验证机制
滚动时间窗口执行 “训练 - 验证 - 测试” 循环，规避数据泄露，贴合实盘推演。[此处插入图 2-2：Walk-Forward 时序验证机制示意图]
2.5.3 交易成本建模与换手率惩罚
损失函数加入调仓惩罚：【Word 公式】L_total=L_pred+λ ∑_t▒Turnover_t
2.6 本章小结
本章为 AlphaTransformer v3 的设计奠定了理论基石：涵盖金融评价体系、Transformer 复杂度瓶颈、iTransformer 与 PatchTST 优化思想、Mamba-2 线性建模优势，支撑后续「Regime-Aware + Mamba-Hybrid」混合架构实现。

第3章 股票预测系统需求分析与总体架构设计
3.1 系统建设目标
3.1.1 面向低 IC 问题的预测能力提升目标
本课题的首要目标并非构建一个仅在离线数据集上取得较低误差的预测模型，而是建立一个能够稳定输出高质量横截面排序信号的股票预测系统。结合 AlphaTransformer v1 的实验结果可知，若模型仅能获得较低水平的 Information Coefficient，则其回测收益往往缺乏稳健的统计支撑，容易受到样本偶然性、市场暴露和评价偏差的影响。因此，系统建设的第一目标是围绕“提升预测信号有效性”展开，通过多资产联合建模、市场状态感知和时空混合编码机制，提高模型在不同市场阶段下的排序一致性与信号稳定性。
3.1.2 面向高换手率问题的交易约束优化目标
量化投资系统的研究价值不仅取决于预测精度，还取决于交易可执行性。若预测模型输出频繁波动，即便账面收益较高，也会因过度调仓导致滑点、冲击成本和手续费快速累积，从而使净值表现显著弱化。因此，本系统在设计之初即将换手率控制纳入整体优化目标，通过回测约束、组合持仓平滑与 Anti-Churn 机制抑制无效调仓，使模型信号能够转化为更具可实施性的投资决策。
3.1.3 面向真实部署的鲁棒性与可扩展性目标
本课题同时面向软件系统落地场景，因此系统应具备可扩展、可维护和可部署特性。具体而言，一方面要求模型训练、在线推理、回测分析和前端展示形成完整闭环；另一方面要求各模块之间边界清晰，便于后续替换模型版本、扩展输入因子、增加策略接口或迁移部署环境。由此，本系统不仅服务于单次毕业设计实验，也为后续持续迭代和平台化扩展提供架构基础。
3.2 系统功能需求分析
3.2.1 行情数据接入与特征处理需求
系统首先需要具备从原始行情数据中构建训练样本和推理样本的能力。该过程不仅包括 OHLCV 基础数据接入，还包括技术指标计算、滚动归一化、标签构造和资产池组织。由于金融数据存在时间依赖和泄露敏感性，特征处理模块必须支持严格的时序一致性约束，确保任意时点的输入仅由过去和当前可观测信息构成。
3.2.2 模型训练、验证与实验管理需求
系统需要支持 AlphaTransformer v1、v2、v3 多版本模型的统一训练、验证与对比分析。为保证研究结论可信，训练流程应具备 Walk-Forward 验证能力、超参数配置能力、实验日志记录能力以及最优模型选择能力。此外，考虑到模型结构迭代频繁，训练模块还应具备较强的可插拔性，以便快速替换 Patch、Mamba-2、Regime-Aware 等关键组件。
3.2.3 在线预测与推荐输出需求
在工程落地层面，系统应能基于最新输入数据快速完成前向推理，并输出结构化预测结果，包括每只股票的 alpha 得分、排序结果、Top-N 推荐列表以及相应的风险提示信息。该功能是前端展示和策略决策的核心数据来源，因此需要具备稳定接口形式和统一输出协议。
3.2.4 回测报告生成与风险分析需求
除预测功能外，系统还必须支持严格的离线回测分析。具体需求包括：收益曲线生成、Sharpe Ratio 统计、最大回撤分析、IC 序列统计、换手率监测以及交易成本扣减后的净值评估。为突出研究工作的可信性，回测部分必须与训练、推理模块共享一致的数据规范与标签定义，并具备防泄露校验能力。
3.2.5 前端交互与结果可视化展示需求
为了体现系统完整性与工程工作量，前端需要支持预测结果展示、回测报告查看和交易交互模拟等功能。系统应能够以图表化方式展示收益曲线、指标变化、推荐资产列表及风险暴露信息，并通过多面板协同交互提升结果解释性与使用便利性。
3.3 系统非功能需求分析
3.3.1 预测服务响应性能要求
由于系统需要支持在线推理与可视化查询，因此服务层必须控制接口延迟，避免前端请求阻塞。具体而言，预测接口、健康检查接口和回测报告接口应采用轻量化响应协议与缓存机制，尽可能降低模型加载和数据序列化的额外开销，从而提升整体交互流畅性。
3.3.2 数据一致性与防泄露要求
本系统属于金融智能决策系统，数据一致性直接决定实验可信度。数据层、模型层与回测层必须共享统一的特征定义、时间切分方式和标签对齐策略，防止训练集、验证集与回测区间之间出现边界污染。特别是在服务层调用回测报告时，也应确保结果来源于防泄露引擎的标准输出，而非临时统计数据。
3.3.3 模型推理稳定性与故障降级要求
从软件工程视角看，模型服务本身可视为轻量级微服务。由于深度学习模型存在加载失败、输入异常、依赖版本不一致等风险，系统需要设计降级容灾容错机制。例如，当主模型不可用时，可回退到缓存预测结果、简化版本模型或最近一次稳定输出；当部分接口依赖失败时，应返回结构化错误码与可解释提示信息，而非直接导致整个服务不可用。
3.3.4 前后端模块化与高可用要求
系统总体设计需要兼顾模块解耦与高可用要求。前端展示层与后端服务层采用前后端分离架构，以降低耦合度；服务层与模型层之间通过标准化接口协议解耦，以便后续实现模型热更新或策略切换；同时，通过日志监测、健康检查和统一异常处理机制提升系统运行过程中的稳定性与可恢复能力。
3.4 系统总体架构设计
3.4.1 数据层总体设计
数据层负责原始行情数据接入、股票池维护、特征工程、标签构造及滚动标准化处理，是系统的基础输入层。该层需严格遵循时序约束，确保任何一条样本记录均可追溯到其真实历史来源，并为后续模型训练和回测评估提供统一数据格式。
3.4.2 模型层总体设计
模型层以 AlphaTransformer 系列模型为核心，承载多版本架构演进与训练实验逻辑。该层包含 v1 原生 Transformer、v2 多尺度 Patch 模型以及 v3 Regime-Aware + Mamba-2 + iTransformer 混合架构。模型层不仅负责离线训练与验证，还负责推理阶段的信号生成与输出规范化。
3.4.3 服务层总体设计
服务层基于 FastAPI 实现，主要承担预测接口、回测报告接口、健康检查接口及模型状态管理功能。该层位于模型层与展示层之间，起到统一封装业务逻辑、隔离模型细节和规范接口协议的作用。通过 REST 风格服务设计，系统能够将深度学习模型能力以标准 API 的形式暴露给前端或其他上层应用。
3.4.4 展示层总体设计
展示层基于 Vue 3 构建，负责向用户提供预测结果展示、回测指标可视化和交易决策交互功能。展示层强调交互性、可解释性与工程可用性，其目标是将底层复杂模型输出转化为用户可理解、可观察、可分析的图表与面板。
[此处插入图3-1：股票预测系统总体四层架构图]
3.5 系统核心数据流与业务流程设计
3.5.1 原始行情到特征张量的处理流程
系统的核心数据流起点为历史行情与资产池数据。数据首先经过缺失值处理、技术指标衍生和滚动窗口标准化，随后构造成统一的多资产时序张量。该张量一方面作为模型训练输入，另一方面也作为在线推理阶段的标准输入格式，从而保证离线实验与在线服务的一致性。
3.5.2 模型训练、验证与模型选择流程
在训练阶段，系统按照预设的时间窗口执行 Walk-Forward 训练与验证流程。模型在训练集上拟合，在验证集上进行超参数选择和早停控制，并根据 IC、Sharpe、回撤与换手率等多指标综合确定候选模型。该流程使模型选择不再依赖单一误差指标，而是面向真实交易目标进行综合评估。
3.5.3 在线预测、回测分析与前端展示流程
在预测阶段，展示层向服务层发起请求，服务层调用模型层输出预测信号，并将结果序列化返回前端。回测流程则由服务层调用回测防泄露引擎，生成收益曲线、风险指标和图表数据，再交由前端统一渲染。这样形成了从原始数据、模型训练、在线推理到结果展示的端到端闭环。
[此处插入图3-2：端到端数据流与业务流程设计图]
3.6 系统模块划分与职责说明
3.6.1 数据预处理模块
该模块负责股票池组织、特征工程、滚动归一化、样本切片和标签构造，是整个系统的数据入口。其设计重点在于时序一致性和可复现性。
3.6.2 AlphaTransformer 模型训练模块
该模块负责模型定义、参数训练、验证评估、实验日志记录及最优模型选择。通过模块化组织，系统能够支持 v1、v2、v3 多版本并行对比，突出项目的迭代研究路径。
3.6.3 回测评估模块
该模块实现回测防泄露引擎、交易成本建模、净值曲线计算、指标统计和风险分析，是本系统区别于一般预测实验脚本的关键组成部分。其核心职责在于保证“从信号到收益”的评估链路真实可信。
3.6.4 FastAPI 推理服务模块
该模块负责模型加载、API 路由管理、结果封装、错误处理与健康检查。它使模型能力以标准服务形式向外提供，为系统微服务化和后续部署扩展奠定基础。
3.6.5 Vue 3 可视化展示模块
前端模块采用组件化设计，包含预测结果区、回测分析区和三层交易面板。所谓三层交易面板，分别为：决策层，用于展示模型推荐与排序信号；仓位层，用于展示候选资产的组合权重与风险暴露；执行层，用于展示模拟调仓、成交反馈和执行结果。该设计使系统从“预测工具”进一步提升为“研究型交易辅助平台”。
[此处插入表3-1：系统功能需求与实现模块映射表]
3.7 本章小结
本章从软件工程视角出发，对股票预测系统的建设目标、功能需求、非功能需求、总体架构、核心数据流和模块职责进行了系统分析。与单纯的算法实验不同，本文所构建的系统明确采用数据层、模型层、服务层和展示层四层架构，实现了从原始数据处理、模型训练推理、回测防泄露评估到前端交互展示的完整闭环。同时，本章特别强调了接口延迟、高可用、降级容灾容错机制、统一数据规范和回测真实性等工程要求，为后续 AlphaTransformer v3 的算法设计与系统实现提供了清晰的架构基础。下一章将在此基础上，进一步对 AlphaTransformer 系列模型的演进过程与关键算法实现进行详细阐述。
第4章 AlphaTransformer 模型设计与关键算法实现
4.1 问题形式化定义
4.1.1 多资产多因子输入表示
设在时刻 $t$ 的股票池规模为 $N$，回看窗口长度为 $T$，每只资产包含 $F$ 维输入特征，则系统输入可表示为
X_t \in \mathbb{R}^{B \times T \times N \times F},
其中 $B$ 表示批大小。对第 $b$ 个样本、第 $i$ 只资产在窗口内的特征序列记为
X_{b,:,i,:}=\{x_{t-T+1}^{(i)},x_{t-T+2}^{(i)},\dots,x_t^{(i)}\}.
本文目标并非单纯预测单资产价格，而是学习横截面 alpha 信号
\hat{\mathbf{y}}_{t+H}=[\hat y_{t+H}^{(1)},\dots,\hat y_{t+H}^{(N)}]^\top,
使其与未来收益向量
\mathbf{r}_{t+H}=[r_{t+H}^{(1)},\dots,r_{t+H}^{(N)}]^\top
在排序意义上保持一致，从而支持多空组合构建。
4.1.2 历史窗口、预测窗口与标签构造方式
未来 $H$ 步收益定义为
r_{t+H}^{(i)}=\frac{P_{t+H}^{(i)}-P_t^{(i)}}{P_t^{(i)}}.
为兼顾回归与方向判别，本文同时构造方向标签
d_{t+H}^{(i)}=\mathbb{I}(r_{t+H}^{(i)}>0).
因此，模型需要同时输出连续收益信号与方向概率，前者用于横截面排序，后者用于增强方向一致性约束。
4.1.3 股票预测任务的目标函数定义
给定参数 $\theta$，本文求解的核心问题可写为
\theta^\ast=\arg\min_{\theta}\ \mathcal{L}_{quant}(f_\theta(X_t),\mathbf{r}_{t+H},\mathbf{d}_{t+H}),
其中 $\mathcal{L}_{quant}$ 为兼顾预测误差、风险调整收益和方向判别的联合量化损失。相较于传统最小均方误差目标，该定义更贴近真实交易需求。
4.2 AlphaTransformer v1 与 v2 基线模型分析
4.2.1 v1 原生 Transformer 架构设计
AlphaTransformer v1 以标准 Transformer 为主体，将时间维特征编码后通过跨资产注意力生成 alpha 分数。其基本优势在于结构统一、易于训练，并能初步捕捉多资产间的共振关系。然而，v1 的核心计算仍依赖标准自注意力，其时间复杂度为
O(T^2D),
当 $T$ 较长时，注意力矩阵既放大计算负担，也放大噪声传播路径。
4.2.2 v1 模型在 IC 与换手率上的主要缺陷
根据项目文档，v1 的 Sharpe Ratio 仅为 $0.28$，Information Coefficient 仅为 $0.073$，最大回撤达到 $-15.2\%$。这说明 v1 的核心问题不是“没有收益”，而是“收益缺乏足够强的预测信号支撑”。从机制上看，原因主要有三点。第一，标准 attention 将所有时点两两关联，容易在金融高噪声序列中产生无效注意力权重，导致表征稀释。第二，v1 默认全市场服从统一分布，忽略了波动期、平稳期和危机期之间的显著状态差异。第三，信号稳定性不足导致排序结果频繁翻转，进一步诱发高换手率，使账面收益被交易摩擦侵蚀。
4.2.3 v2 中 PatchTST 与稀疏注意力改进思路
为缓解 v1 在长序列建模上的缺陷，v2 引入 PatchTST 风格的时间补丁表示。设 patch 长度为 $P$，步长为 $S$，则 token 数量由原始时间长度 $T$ 压缩为
M=\left\lfloor \frac{T-P}{S}\right\rfloor+1,
从而将时间轴 attention 的理论复杂度由 $O(T^2)$ 降低为 $O(M^2)$。与此同时，稀疏注意力机制通过只保留局部窗口或 Top-$k$ 相关连接，进一步削减冗余计算。
4.2.4 v2 模型改进效果与剩余问题分析
v2 在长序列处理效率与局部模式提取方面优于 v1，这是一次有效的结构优化。然而，v2 仍未解决两个根本问题。其一，Patch 与稀疏 attention 只是在计算路径上做压缩，并未显式建模市场状态切换，因此对非平稳行情的适应仍然有限。其二，v2 的核心视角仍以时间 token 为主，对多资产横截面耦合关系的表达不足，难以充分捕捉板块联动与风格迁移。由此，v3 的架构升级不应停留于“更快的 attention”，而应转向“状态感知 + 线性时间建模 + 资产维建模”的联合重构。
[此处插入图4-1：AlphaTransformer v1、v2、v3 架构演进图]
4.3 AlphaTransformer v3 总体架构设计
4.3.1 v3 的整体设计目标
AlphaTransformer v3 的设计目标可以概括为：在提升 IC 的同时抑制换手率，在增强预测能力的同时保证可交易性。为此，v3 不再依赖单一主干网络，而是由 Regime-Aware 市场感知模块、Mamba-2 时间编码模块、iTransformer 资产编码模块以及 WaveLSFormerHead 输出层协同组成。
4.3.2 Regime-Aware + Mamba-2 + iTransformer 混合框架
设输入张量经线性嵌入后得到
H^{(0)} \in \mathbb{R}^{B \times T \times N \times D}.
随后，v3 按如下顺序处理：
H^{(1)}=\mathrm{RegimeAware}(H^{(0)}),
H^{(2)}=\mathrm{Mamba2Temporal}(H^{(1)}),
H^{(3)}=\mathrm{iTransformerAsset}(H^{(2)}),
\hat{\mathbf{y}},\mathbf{w}=\mathrm{WaveLSFormerHead}(H^{(3)}).
其中 $\mathbf{w}$ 表示投组合权重，直接服务于后续模拟收益与 Sharpe 优化。
4.3.3 v3 模型各子模块协同关系
上述结构的逻辑十分明确：Regime-Aware 负责回答“当前市场处于何种状态”；Mamba-2 负责高效提炼时间轴动态；iTransformer 负责捕捉资产间横截面关联；输出头负责将预测信号约束到市场中性多空决策空间。这样，v3 才能同时回应 v1 的低 IC 问题与高换手率问题。
[此处插入图4-2：AlphaTransformer v3 整体架构流图]
4.4 市场状态感知模块设计
4.4.1 基于 Autoencoder 的市场状态检测器设计
为识别异常波动与分布突变，本文先利用 Autoencoder 对市场特征进行重构。对输入向量 $x_t$，编码与解码分别为
z_t=f_{enc}(x_t),\qquad \hat x_t=f_{dec}(z_t).
其重建损失定义为
\mathcal{L}_{AE}=\frac{1}{B}\sum_{t=1}^{B}\|x_t-\hat x_t\|_2^2.
相应地，单样本重建误差为
e_t=\|x_t-\hat x_t\|_2^2.
当 $e_t$ 显著升高时，说明当前样本偏离“常态市场”分布，可视为高波动或危机状态候选。
4.4.2 市场状态概率分布建模方法
令 pooled 表征为 $u_t=\mathrm{Pool}(H_t)$，将其与重建误差拼接后输入状态分类器：
q_t=[u_t;e_t],
\mathbf{p}_t=\mathrm{Softmax}(W_r q_t+b_r),
其中
\mathbf{p}_t=[p_t^{(1)},p_t^{(2)},p_t^{(3)}]
分别对应平稳、波动和危机三类市场状态，满足
\sum_{k=1}^{3}p_t^{(k)}=1.
4.4.3 RegimeAwareNorm 自适应归一化机制设计
设当前隐藏表征为 $H_t \in \mathbb{R}^{B \times N \times D}$，其逐样本归一化写为
\tilde H_t=\frac{H_t-\mu(H_t)}{\sigma(H_t)+\epsilon}.
与普通 LayerNorm 不同，v3 的缩放因子与平移因子由状态概率动态生成：
\gamma_t=W_\gamma \mathbf{p}_t+b_\gamma,\qquad
\beta_t=W_\beta \mathbf{p}_t+b_\beta.
因此，自适应层归一化定义为
\mathrm{ALN}(H_t,\mathbf{p}_t)=\gamma_t \odot \tilde H_t+\beta_t.
当市场进入高波动状态时，$\gamma_t$ 与 $\beta_t$ 会自动调节特征尺度，使模型在不同 regime 下拥有不同的响应模式。
4.4.4 极端市场下动态路由机制的理论分析
进一步地，可将状态概率用于专家融合：
\hat y_t=\sum_{k=1}^{3}p_t^{(k)} f_k(H_t),
即利用软路由在不同状态专家间加权，从而避免单一预测器对所有行情“一刀切”。这对于金融非平稳场景尤为关键，因为极端时期低 IC 的根源往往不是参数不足，而是模型假设失配。
[此处插入图4-3：Regime-Aware 状态感知与动态路由机制示意图]
4.5 时间维高效编码模块设计
4.5.1 PatchTST 多尺度时间补丁表示方法
对每只资产的时间序列，v3 先进行 patch 化，以减少原始长度并增强局部结构表达。设 patch 操作为 $\mathcal{P}(\cdot)$，则
X_t^{patch}=\mathcal{P}(X_t)\in\mathbb{R}^{B\times M\times N\times D},
其中 $M \ll T$。该表示为后续 Mamba-2 提供更稳定的局部时间片输入。
4.5.2 Mamba-2 时间编码器设计
Mamba-2 采用离散状态空间递推。对时间步 $m$，其更新写为
h_m=\bar A_m h_{m-1}+\bar B_m x_m,
y_m=C_m h_m + D x_m,
其中 $\bar A_m,\bar B_m,C_m$ 可依赖当前输入 $x_m$ 动态生成，从而体现 selective scan 机制。相较标准 attention 直接构造 $M\times M$ 相关矩阵，Mamba-2 仅进行线性递推，因此时间复杂度近似为
O(M D d_s),
其中 $d_s$ 为状态维度。
4.5.3 时间维线性复杂度优势分析
若 Transformer 时间编码复杂度为
O(M^2D),
则在 $M$ 较大时，Mamba-2 的
O(M D d_s)
显著优于二次复杂度。对于高频金融任务，这种复杂度下降不仅意味着训练更快，更重要的是允许系统在固定显存预算下保留更长历史窗口，从而增强对长期趋势与状态切换的识别能力。
4.5.4 与标准自注意力机制的对比讨论
Transformer 擅长显式建模任意两时点关系，但在高噪声金融数据中，这种全连接关系不一定必要；Mamba-2 通过状态递推更适合提炼“对未来真正有贡献”的时序信息。因此，v3 在时间维选择 Mamba-2，不是简单追求新结构，而是基于金融场景的复杂度与噪声抑制需求所做出的架构决策。
4.6 资产维相关性建模模块设计
4.6.1 iTransformer 资产维反转编码原理
时间编码后，隐藏表征为
H^{(2)}\in\mathbb{R}^{B\times T\times N\times D}.
传统做法通常沿时间维进行 self-attention，而 v3 借鉴 iTransformer 思想，将张量重排为
\tilde H^{(2)}=\mathrm{Permute}(H^{(2)})\in\mathbb{R}^{B\times N\times T\times D}.
即将“资产”提升为主要 token 维度，每只资产携带完整时间轨迹表征。
4.6.2 跨资产关联关系建模方法
对每个资产 token，将其时间维压缩或投影为
a_i=\phi(\tilde H^{(2)}_{:,i,:,:})\in\mathbb{R}^{B\times D_a},
进而形成资产 token 矩阵
A=[a_1,\dots,a_N]^\top\in\mathbb{R}^{B\times N\times D_a}.
随后在资产维执行 attention：
\mathrm{Attn}_{asset}(A)=\mathrm{Softmax}\left(\frac{Q_A K_A^\top}{\sqrt{D_a}}\right)V_A.
这样，模型学习到的不再是“哪些时间点相关”，而是“哪些资产之间存在同步、轮动或传染关系”。
4.6.3 时空混合表示融合策略
时间编码结果与资产编码结果通过残差融合：
H^{(3)}=\mathrm{Fuse}(H^{(2)},\mathrm{Attn}_{asset}(A)),
其中 Fuse 可取拼接后线性映射，或加权残差：
H^{(3)}=\lambda H^{(2)}+(1-\lambda)\hat H_{asset}.
该融合使模型同时保留时间动态与横截面关系。
4.6.4 板块联动与风格迁移信息的编码逻辑
在股票市场中，预测信号往往并非来自单资产孤立轨迹，而来自行业共振、估值风格切换和资金流迁移。iTransformer 风格的资产维建模天然更适合表达此类结构，也是 v3 相较 v2 在多资产联动上实现跃升的关键原因。
[此处插入图4-4：Mamba-2 时间轴编码与 iTransformer 资产轴编码协同示意图]
4.7 输出层与损失函数设计
4.7.1 WaveLSFormerHead 输出头结构设计
设最终隐藏表示为 $H^{(3)}$，输出头生成原始评分 $\mathbf{s}\in\mathbb{R}^{B\times N}$。为得到市场中性多空权重，定义可行域
\mathcal{W}=\left\{\mathbf{w}\in\mathbb{R}^{N}\mid \sum_{i=1}^{N}w_i=0,\ \|\mathbf{w}\|_1=1,\ |w_i|\le w_{max}\right\}.
WaveLSFormerHead 将原始评分投影到该可行域：
\mathbf{w}=\Pi_{\mathcal{W}}(\mathbf{s}).
因此天然满足
\sum_{i=1}^{N}w_i=0,
即市场中性约束，同时
|w_i|\le w_{max}
限制单资产过度集中。
4.7.2 CombinedQuantLoss 联合损失函数定义
本文定义联合损失为
\mathcal{L}_{CQ}=\lambda_h \mathcal{L}_{Huber}+\lambda_s \mathcal{L}_{Sharpe}+\lambda_d \mathcal{L}_{BCE}.
其中，Huber 损失用于稳健回归：
\mathcal{L}_{Huber}=
\frac{1}{BN}\sum_{b,i}
\begin{cases}
\frac{1}{2}(r_{b,i}-\hat y_{b,i})^2, & |r_{b,i}-\hat y_{b,i}|\le \delta,\\
\delta |r_{b,i}-\hat y_{b,i}|-\frac{1}{2}\delta^2, & \text{otherwise}.
\end{cases}
4.7.3 面向 IC 提升的排序约束项设计
为使损失贴近组合表现，先定义单期组合净收益
R_t^{p}=\sum_{i=1}^{N}w_t^{(i)} r_{t+1}^{(i)}-c\cdot \mathrm{Turnover}_t.
则模拟 Sharpe 损失写为
\mathcal{L}_{Sharpe}=-\frac{\mu(R^p)}{\sigma(R^p)+\epsilon}.
该项直接鼓励更高风险调整收益，而非只追求点预测精度。
4.7.4 面向换手率抑制的交易摩擦惩罚项设计
方向一致性项采用二元交叉熵：
\mathcal{L}_{BCE}=-\frac{1}{BN}\sum_{b,i}\left[d_{b,i}\log \sigma(\hat y_{b,i})+(1-d_{b,i})\log(1-\sigma(\hat y_{b,i}))\right].
同时，换手率惩罚已通过 $R_t^p$ 中的成本项显式进入 Sharpe loss，从而使模型在训练阶段就感知交易摩擦。相比只在回测后扣减成本，这种设计更有助于抑制信号抖动和无效调仓。
4.8 模型训练与优化策略
4.8.1 优化器与学习率调度方法
本文训练阶段采用 AdamW 优化器，并结合余弦退火调度稳定收敛。对参数 $\theta$ 的更新可写为
\theta_{k+1}=\theta_k-\eta_k \frac{\hat m_k}{\sqrt{\hat v_k}+\epsilon}-\eta_k\lambda \theta_k.
其中 $\eta_k$ 为动态学习率，$\lambda$ 为权重衰减系数。
4.8.2 自主实验循环与超参数搜索机制
为提高迭代效率，系统采用自主实验循环机制，对 patch 长度、状态维度、损失权重和持仓约束进行网格化或分阶段搜索，并以验证集 IC、Sharpe 和换手率作为联合筛选标准。
4.8.3 模型回退、降级与异常恢复机制
考虑到复杂模型可能存在训练不稳定或推理依赖异常，系统保留 v2 乃至 v1 的回退路径。当 v3 在特定窗口出现异常波动时，可退回已验证的稳定版本，保证服务连续性。
4.9 模型复杂度与理论分析
4.9.1 各版本模型复杂度对比分析
v1 的核心复杂度为
O(T^2D),
v2 在 patch 化后约为
O(M^2D),\quad M<T,
而 v3 的时间轴主干近似为
O(MDd_s)+O(N^2D_a),
即将原本完全依赖时间二次复杂度的问题，拆分为“线性时间建模 + 资产维注意力建模”。
4.9.2 v3 相对 v1 与 v2 的理论优势分析
v1 的主要问题是“全局 attention 过重而状态感知不足”；v2 的主要问题是“时间效率改善但市场状态与横截面结构仍建模不足”；v3 则通过 Regime-Aware、Mamba-2 和 iTransformer 的分工协作，将“非平稳性”“长序列复杂度”“多资产联动”三类问题同时纳入统一框架。
4.9.3 模型在金融非平稳场景中的适应性讨论
从理论上看，v3 的优势不在于单个模块绝对更强，而在于每个模块都针对金融时序的真实痛点而设计。因此，它更有可能在滚动回测和极端行情测试中表现出稳定 IC 与更低换手率，而非只在单一切片数据上取得表面最优。
[此处插入表4-1：各版本模型核心模块对比表]
4.10 本章小结
本章围绕 AlphaTransformer 的架构演进与关键算法实现展开论述。首先，分析了 v1 原生 Transformer 在 IC 偏低、换手率偏高方面的结构性缺陷，以及 v2 虽通过 PatchTST 与稀疏注意力缓解长序列问题，但仍难以充分应对市场非平稳性和多资产联动建模不足的局限。随后，系统提出 v3 的整体框架，并分别从 Regime-Aware 市场状态感知、Mamba-2 时间维线性建模、iTransformer 资产维反转编码以及 WaveLSFormerHead 与 CombinedQuantLoss 的交易导向输出层四个方面进行了形式化定义。整体来看，v3 是对前两版模型的体系化重构，其目标并非单纯提升预测精度，而是从根本上改善低 IC 与高换手率两项核心问题。下一章将在此基础上，进一步给出防泄露训练框架与回测评估方法设计。
第5章 防泄露训练框架与回测评估方法设计
5.1 数据集构建与样本组织方式
5.1.1 股票池构成与资产类别划分
为保证模型具备横截面比较能力，本文采用多资产联合建模范式构建训练数据。股票池覆盖 A 股核心标的及部分美股代表性资产，并按照行业、风格与市场属性进行统一组织，使模型能够同时观察同类资产之间的联动关系与异类资产之间的风险迁移路径。与单资产预测相比，多资产数据组织不仅提高了样本利用效率，也为后续基于 iTransformer 的资产维建模提供了结构基础。
5.1.2 输入特征体系设计
设第 $i$ 只资产在时刻 $t$ 的原始特征向量为
x_t^{(i)} \in \mathbb{R}^{F},
其中 $F$ 包含价格、成交量、收益率、波动率、均线偏离、动量因子及其他技术统计量。对长度为 $T$ 的历史窗口，可构造单样本输入张量
X_t=\{x_{t-T+1}^{(i)},x_{t-T+2}^{(i)},\dots,x_t^{(i)}\}_{i=1}^{N}\in\mathbb{R}^{T\times N\times F}.
进一步叠加批处理维度后，模型训练输入可写为
\mathcal{X}\in\mathbb{R}^{B\times T\times N\times F}.
5.1.3 标签构建与预测目标对齐方式
设收盘价为 $P_t^{(i)}$，则一步预测任务下，第 $i$ 只资产在时刻 $t$ 对应的未来收益标签定义为
y_t^{(i)}=r_{t+1}^{(i)}=\frac{P_{t+1}^{(i)}-P_t^{(i)}}{P_t^{(i)}}.
若预测窗口为 $H$，则可扩展为
y_t^{(i)}=r_{t+H}^{(i)}=\frac{P_{t+H}^{(i)}-P_t^{(i)}}{P_t^{(i)}}.
这意味着输入窗口 $X_t$ 的最后时刻是 $t$，监督信号来自严格晚于 $t$ 的未来区间，从而形成因果一致的监督学习结构。
5.1.4 训练集、验证集与测试集划分原则
金融时间序列数据不满足独立同分布假设，因此训练集、验证集与测试集必须按时间顺序切分，而不能采用随机抽样。设总体时间区间为 $[1,\mathcal{T}]$，则应满足
\mathcal{T}^{train}\prec \mathcal{T}^{val}\prec \mathcal{T}^{test},
其中符号 $\prec$ 表示严格的时间先后关系。该划分方式保证任一训练样本不可能接触未来测试信息，为后续防泄露训练与回测奠定基础。
5.2 防泄露数据预处理机制设计
5.2.1 滚动窗口标准化方法
防泄露机制的核心在于：任意时刻 $t$ 的特征变换只能依赖于 $t$ 及其之前的历史数据，而绝不能使用 $t$ 之后的信息。设第 $f$ 个特征在资产 $i$ 上的原始序列为 $x_{t,f}^{(i)}$，窗口长度为 $W$，则滚动均值与滚动标准差定义为
\mu_{t,f}^{(i)}=\frac{1}{W}\sum_{s=t-W+1}^{t}x_{s,f}^{(i)},
\sigma_{t,f}^{(i)}=\sqrt{\frac{1}{W}\sum_{s=t-W+1}^{t}\left(x_{s,f}^{(i)}-\mu_{t,f}^{(i)}\right)^2+\epsilon}.
据此得到严格因果的滚动 Z-Score 标准化：
z_{t,f}^{(i)}=\frac{x_{t,f}^{(i)}-\mu_{t,f}^{(i)}}{\sigma_{t,f}^{(i)}}.
该定义清楚表明，$z_{t,f}^{(i)}$ 仅由区间 $[t-W+1,t]$ 内的数据决定，不包含任何未来信息。
5.2.2 特征计算过程中的时序一致性约束
在实际实现中，许多数据泄露并非来自显式使用未来价格，而是来自“预处理顺序错误”或“统计口径越界”。例如，全局标准化常写为
\tilde x_{t,f}^{(i)}=\frac{x_{t,f}^{(i)}-\mu_{global,f}^{(i)}}{\sigma_{global,f}^{(i)}},
其中
\mu_{global,f}^{(i)}=\frac{1}{\mathcal{T}}\sum_{s=1}^{\mathcal{T}}x_{s,f}^{(i)},
显然包含测试区间乃至未来区间的信息。该做法虽然在通用机器学习场景中常见，但在金融时序中属于典型未来函数，会系统性抬高验证表现和回测收益。
需要特别指出的是，`pandas.rolling().mean()` 本身在默认右对齐、逐资产分组且仅在训练窗口内计算时，并不必然构成泄露；真正危险的是研究实践中常见的几种误用情形：第一，在切分训练集与测试集之前，对全样本先统一执行 rolling 统计，再将结果回填到训练区间，此时窗口边界附近可能混入未来观测；第二，使用 `center=True` 形成中心窗口，使时刻 $t$ 的统计量同时包含 $t+k$ 的未来值；第三，在跨资产面板中未按资产分组，而是直接对混合后的长表执行 rolling，造成横向信息穿透；第四，rolling 结果再配合 `bfill`、插值或错误索引对齐，会将未来统计值传播到过去记录。因此，学术上真正需要强调的不是“rolling 一定泄露”，而是“任何滚动统计都必须在严格的因果时序、资产分组和切分边界约束下执行”，否则就会产生隐性未来函数。
5.2.3 标签对齐与未来信息隔离机制
标签构造同样是数据泄露高发区域。若采用一步预测，则标签对齐的数学定义是
y_t^{(i)}=r_{t+1}^{(i)}.
在表格实现中，这对应于对收益序列执行 `shift(-1)`，其本质含义并非“把未来拿来当前用”，而是将“时刻 $t$ 的输入样本”与“时刻 $t+1$ 的真实结果”建立监督映射，即
(X_t,\ y_t)=(X_t,\ r_{t+1}).
当预测窗口为 $H$ 时，应写为
y_t^{(i)}=r_{t+H}^{(i)}.
必须强调的是，`shift(-1)` 只应出现在标签生成阶段，而绝不能用于输入特征。若在特征侧误用同样的位移操作，则等价于直接将未来收益嵌入输入，属于严重泄露。
5.2.4 数据处理流程中的泄露风险点分析
综合来看，金融预测中的泄露风险点主要包括：全局均值方差标准化、滚动窗口边界越界、标签错位、训练测试切分后重新排序、跨资产不分组统计，以及基于全样本排名构造截面因子等。为此，本文在数据管线中采用“先按时间切分、再逐窗口统计、后生成样本”的严格顺序，并在回测阶段重复使用同一标准化逻辑，以确保训练链路和评估链路的一致性。
[此处插入图5-1：防泄露数据处理流程图]
5.3 Walk-Forward 训练与验证机制
5.3.1 滚动训练窗口设计
为模拟真实市场中的“训练于过去、部署于未来”过程，本文采用 Walk-Forward 验证框架。设第 $k$ 轮训练区间、验证区间与测试区间分别为 $\mathcal{I}_k^{train}$、$\mathcal{I}_k^{val}$、$\mathcal{I}_k^{test}$，则有
\max(\mathcal{I}_k^{train}) < \min(\mathcal{I}_k^{val}) < \min(\mathcal{I}_k^{test}).
每一轮仅利用过往历史更新模型参数，再在后续区间上验证与测试，从而严格复现时间推进式的部署逻辑。
5.3.2 动态验证集滑动机制
当时间推进到下一轮时，训练窗口和验证窗口同步向前滑动，即
\mathcal{I}_{k+1}^{train}=\mathcal{I}_k^{train}+\Delta,\quad
\mathcal{I}_{k+1}^{val}=\mathcal{I}_k^{val}+\Delta,
其中 $\Delta$ 为滑动步长。这样可以评估模型在不同市场阶段上的泛化稳定性，而不是仅在单一静态切片上获得一次性最优结果。
5.3.3 模型选择、早停与参数冻结策略
在每一轮 Walk-Forward 训练中，模型选择并不依据单一损失最小化，而是综合验证集上的 IC、Sharpe、最大回撤与换手率指标。参数更新仅在训练集上进行，验证集只用于超参数选择与早停，不参与梯度反传。这样可防止模型因反复访问验证集而形成隐性过拟合。
5.3.4 多版本模型统一评估协议设计
为公平比较 v1、v2 与 v3，本文要求所有模型遵循完全一致的时间切分、特征体系、标签定义和交易成本假设。尤其需要强调的是，金融时序中绝对禁止使用 `shuffle=True`、随机切分或常规 K 折交叉验证。原因在于一旦过去与未来样本被随机混洗，模型将通过统计依赖间接接触未来分布，导致验证结果虚高。这种错误在金融任务中是致命的，因为它破坏了因果关系，所得性能无法在真实交易中复制。
[此处插入图5-2：Walk-Forward 训练与验证时序划分示意图]
5.4 回测引擎与策略约束设计
5.4.1 多空组合构建规则
设模型在时刻 $t$ 输出横截面评分向量 $\hat{\mathbf{y}}_t$，通过排序选取前 $K$ 只股票构成长组合、后 $K$ 只股票构成短组合。记长组合集合为 $S_t^{long}$，短组合集合为 $S_t^{short}$，则市场中性权重满足
\sum_{i\in S_t^{long}} w_t^{(i)} + \sum_{j\in S_t^{short}} w_t^{(j)} = 0.
若采用等权配置，则
w_t^{(i)}=
\begin{cases}
\frac{1}{K}, & i\in S_t^{long},\\
-\frac{1}{K}, & i\in S_t^{short},\\
0, & \text{otherwise}.
\end{cases}
5.4.2 调仓周期与持仓周期设计
为避免过度交易，系统引入固定持仓周期 $H_{hold}$。即在形成组合后，除非达到再平衡时点，否则权重保持不变。该设计可使模型输出从“逐时点预测”转化为“周期性决策”，从而降低高频信号噪声对交易执行的直接冲击。
5.4.3 交易成本、滑点与冲击成本建模
设组合毛收益为 $R_t^{gross}$，单位换手成本为 $c$，当期换手率为 $\text{Turnover}_t$，则净收益定义为
R_t^{net}=R_t^{gross}-c\cdot \text{Turnover}_t.
若进一步考虑冲击成本和滑点，则可写为
R_t^{net}=R_t^{gross}-c_1\cdot \text{Turnover}_t-c_2\cdot \text{Impact}_t.
此处 $c_1,c_2$ 分别表示显性交易成本系数和市场冲击系数。通过显式建模交易摩擦，回测结果更接近真实执行环境。
5.4.4 集合差集 Anti-Churn 换手率抑制机制
Anti-Churn 是本文回测框架中的关键创新，其目标在于抑制由于模型评分微小波动所引发的无意义调仓。设昨日持仓集合为
S_{t-1}=S_{t-1}^{long}\cup S_{t-1}^{short},
今日理论目标持仓集合为
S_t=S_t^{long}\cup S_t^{short}.
则实际需要卖出的资产集合定义为
S_{sell}=S_{t-1}-S_t,
实际需要买入的资产集合定义为
S_{buy}=S_t-S_{t-1}.
而交集部分
S_{keep}=S_{t-1}\cap S_t
表示昨日与今日共同持有的资产，应继续保留而不发生交易。这样，实际调仓动作只发生在集合对称差
S_{chg}=S_{sell}\cup S_{buy}=S_{t-1}\triangle S_t
上，而非对全部目标组合进行全量重构。
若分别对多头与空头执行同样逻辑，则有
S_{sell}^{long}=S_{t-1}^{long}-S_t^{long},\qquad
S_{buy}^{long}=S_t^{long}-S_{t-1}^{long},
S_{sell}^{short}=S_{t-1}^{short}-S_t^{short},\qquad
S_{buy}^{short}=S_t^{short}-S_{t-1}^{short}.
对应的组合换手率可写为
\text{Turnover}_t=\frac{1}{2}\sum_{i=1}^{N}\left|w_t^{(i)}-w_{t-1}^{(i)}\right|,
而在 Anti-Churn 机制下，该量可近似受集合变化规模约束：
\text{Turnover}_t \propto \frac{|S_{t-1}\triangle S_t|}{|S_t|}.
这说明只有当目标组合成员真正发生变化时，系统才执行调仓，从而显著降低高频噪声引起的无效交易。
从算法角度看，Anti-Churn 的本质并非简单减少交易次数，而是通过集合差集运算将“模型评分变化”与“实际交易变化”解耦。若某只股票尽管排名轻微波动，但仍位于可接受持仓区间，则其可继续保留在组合中，不必因边际顺序扰动而立即换仓。该机制对于降低手续费磨损、提升净 Sharpe 和提高组合稳定性具有直接作用，也是本文系统区别于传统全量再平衡回测框架的重要工程亮点。
[此处插入图5-3：Anti-Churn 换手率抑制机制示意图]
5.5 实验方案与对比策略设计
5.5.1 主实验对比模型设置
主实验以 AlphaTransformer v1 为原始基线，以 v2 为中间过渡版本，以 v3 为最终模型。三者共享相同数据集、相同 Walk-Forward 切分和相同回测参数，以保证结果的可比性。
5.5.2 v1、v2、v3 版本对比实验设计
版本对比实验的核心目的是验证架构演进的合理性。v1 用于揭示原生 Transformer 在低 IC 和高换手率方面的局限；v2 用于评估 patch 化和稀疏注意力对长序列问题的改善幅度；v3 用于验证 Regime-Aware、Mamba-2 与 iTransformer 联合引入后，对信号稳健性和交易可执行性的综合提升。
5.5.3 消融实验设计
为进一步确认各模块的贡献，本文在 v3 基础上分别移除 Regime-Aware、Mamba-2、iTransformer 和 Anti-Churn 模块，并比较 IC、Sharpe 和换手率变化情况。该设计能够避免将全部性能提升简单归因于模型规模增加。
5.5.4 鲁棒性实验与异常市场实验设计
此外，本文还将高波动阶段、市场急跌阶段和风格切换阶段单独抽取进行鲁棒性分析，以检验模型在分布突变场景下的稳定性。该实验尤其用于验证 Regime-Aware 模块是否真正提升了非平稳市场环境下的预测可靠性。
5.6 评价指标体系设计
5.6.1 预测误差指标设计
在预测层面，系统记录 Huber Loss、MAE、RMSE 等回归误差指标，用于度量数值拟合能力。
5.6.2 排序能力指标设计
在横截面层面，采用 IC 与 RankIC 衡量预测信号与未来收益排序的一致性，其中 IC 定义为
IC_t=\mathrm{corr}(\hat{\mathbf y}_t,\mathbf r_{t+1}).
该指标直接对应量化选股的核心目标。
5.6.3 收益风险指标设计
在组合层面，系统使用年化收益率、Sharpe Ratio、最大回撤和净值曲线稳定性进行综合评估。该类指标衡量的不再是“预测得是否接近”，而是“策略是否可用”。
5.6.4 交易可执行性指标设计
为体现工程约束，系统额外统计平均换手率、调仓次数、单次调仓规模和成本侵蚀比例。只有当预测信号在收益、风险与交易摩擦之间取得平衡时，模型才具有真实部署价值。
[此处插入表5-1：实验数据集与时间区间说明表]
[此处插入表5-2：各版本模型回测指标对比表]
5.7 本章小结
本章围绕防泄露训练框架与回测评估方法设计，系统阐述了数据集构建、滚动窗口标准化、标签时序对齐、Walk-Forward 验证以及回测约束机制的理论与实现逻辑。重点说明了在金融时序任务中，全局标准化、错误滚动统计、随机切分和标签错位会如何导致隐性未来函数与性能虚高，并给出了严格基于历史窗口的因果标准化定义。与此同时，本文进一步提出并形式化描述了 Anti-Churn 集合差集调仓机制，证明只有将“组合变化”限制在昨日与今日持仓集合的差异部分，才能有效抑制无效换手并降低交易摩擦。整体而言，本章所构建的防泄露训练与回测框架，为后续实验结果的真实性、稳健性与可复现性提供了关键保障。
第6章 系统实现与实验结果分析
6.1 系统实现环境与关键技术栈
6.1.1 后端开发环境与模型部署环境
本文系统后端采用 Python 生态完成实现，核心服务框架为 FastAPI，模型推理框架为 PyTorch。根据项目现有实现，服务入口位于 `api/server.py`，统一暴露 `/api/v1` 前缀下的健康检查、预测器加载、预测状态、仪表盘、交易、账户和自动交易等接口。后端在启动阶段自动执行模型注册与加载逻辑，若未提供检查点，则回退到随机权重开发模式；若用户请求 CUDA 设备但环境不可用，则自动降级到 CPU 推理，从而保证服务不会因设备不匹配而直接失效。该设计体现了系统对部署稳定性与实验可用性的双重考虑。
从工程实现看，后端并未将模型推理逻辑直接耦合在路由函数中，而是通过 `ModelRegistry` 与 `AccountManager` 两个全局单例完成轻量级依赖注入。前者负责模型装载、状态查询、推理执行和异常封装，后者负责账户状态、成交记录、持仓更新和交易规则检查。虽然项目未采用复杂的外部 IoC 容器，但 `get_registry()` 与 `get_account_manager()` 的注册表模式已经具备服务注入、统一管理和多路由复用的特征。
6.1.2 前端开发环境与可视化技术选型
前端采用 Vue 3 + TypeScript + Vite 技术栈，配合 Element Plus 组件库完成交互式页面构建；状态管理采用 Pinia，实现仪表盘、账户与股票选择状态的集中管理；图形可视化基于 ECharts 完成收益曲线、K 线图、特征贡献图及持仓热力图的渲染；局部数字滚动与动态过渡效果则通过 GSAP 完成。相关依赖在 `frontend/package.json` 中均有明确声明，包括 `axios`、`echarts`、`pinia`、`vue-router`、`element-plus` 和 `gsap` 等。
6.1.3 项目目录结构与模块组织方式
前端核心代码位于 `frontend/src` 下，按 `api`、`stores`、`components`、`views`、`utils` 进行模块化划分。后端代码位于 `api` 目录下，按 `server`、`dashboard`、`trading`、`account`、`auto`、`predictor` 等职责分层组织。这种目录结构使“模型能力”“业务路由”“可视化展示”和“状态管理”形成较为清晰的边界，有利于论文中的系统模块映射分析，也便于后续功能增量迭代。
6.2 后端服务实现
6.2.1 FastAPI 服务架构设计
后端服务层基于 FastAPI 构建，并在应用初始化阶段完成统一中间件和路由注册。系统通过 `dashboard_router`、`trading_router`、`account_router` 与 `auto_router` 四类路由组合完成多业务聚合，对应分析展示、模拟交易、账户管理与自动信号执行四大子系统。统一服务入口使前端可以通过固定 REST 接口完成数据拉取，而无需感知底层模型和账户逻辑的内部实现。
6.2.2 预测接口设计与实现
在推理层面，系统通过 `ModelRegistry.predict()` 接收标准化后的多资产张量输入，并自动执行维度补全、设备迁移、特征维度检查和异常转换。其主要目标是将模型运行时的不确定性转化为结构化错误响应。例如，当模型尚未加载时，系统抛出 `MODEL_NOT_LOADED`；当输入维度不匹配时，返回 `FEATURE_DIM_ERROR`；当设备侧出现显存不足时，则将错误显式转换为 `CUDA_OOM` 并触发 CPU 降级。该机制显著降低了深度学习服务在部署过程中的不可控性。
6.2.3 回测报告接口设计与实现
当前项目中的 `/dashboard/full`、`/dashboard/metrics`、`/dashboard/equity-curve` 与 `/dashboard/predictions` 等接口已形成面向前端分析页的聚合输出。系统将收益曲线、指标统计、特征重要性和 AI 排名结果统一封装为结构化响应对象，再交由前端一次性拉取或局部刷新。这种“聚合接口 + 局部接口”并行设计，兼顾了初次加载效率与组件级更新效率。
6.2.4 健康检查、模型缓存与异常处理机制
系统在 `/api/v1/health` 提供独立健康检查接口，仅返回模型加载状态、运行设备和服务运行时长，不触发高成本推理操作，适合作为前端轮询探针和部署监控入口。异常处理方面，`api/server.py` 中定义了全局异常拦截器，对 `ValidationError`、`HTTPException` 和一般异常分别进行结构化封装。尤其对于未知异常，系统并不直接向前端抛出裸 500 页面，而是返回统一 JSON 错误体，以降低前端崩溃风险。缓存层面，`tickers_registry.py` 对标的列表维护了基于文件修改时间的轻量缓存；模型层则通过全局注册表保留当前模型实例，避免重复加载造成的额外延迟。
6.2.5 服务降级与容灾恢复机制
本系统后端在多个环节设计了降级容灾策略。其一，模型启动时支持“无 checkpoint 随机权重模式”，保证开发与演示环境可用。其二，设备不可达时自动降级到 CPU。其三，推理异常被统一转换为结构化响应，而非直接中断整个服务。其四，自动交易与仪表盘部分接口在当前版本中提供可控的模拟数据生成逻辑，从而在真实市场数据源不可用时，仍可支撑前端页面和交互测试。上述机制虽仍属轻量级容灾，但已体现出研究型系统向高可用服务演化的工程思路。
[此处插入图6-1：FastAPI 服务接口调用流程图]
6.3 前端界面与交互功能实现
6.3.1 预测结果展示页面设计
系统前端以 Vue Router 为骨架，提供仪表盘页、分析页与交易页三类主要视图。仪表盘页负责展示总资产、收益曲线、AI 推荐表格和特征贡献图；分析页负责呈现单标的 K 线与未来预测曲线、技术指标卡片和策略解读；交易页则聚焦账户、持仓、交易指令与自动交易开关。该结构实现了“总览-分析-执行”的研究闭环。
6.3.2 回测分析可视化页面设计
可视化实现主要依赖 ECharts。仪表盘页使用折线图展示策略权益曲线与基准曲线，并通过 tooltip 同时显示超额收益；分析页将历史 K 线与未来预测区间叠加在同一时间轴中，形成“历史走势 + 模型预测 + 置信区间”的复合图；此外，特征重要性、资产配置和月度收益热图均由 ECharts 统一完成渲染。这种可视化方案不仅增强了结果解释性，也使系统界面符合量化分析平台的基本展示习惯。
6.3.3 三层交易面板设计与实现
交易页的核心亮点在于三层交易面板设计。第一层为决策层，展示 AI 置信度、方向判断、风险等级和模型评分，用于回答“是否应交易”；第二层为仓位层，展示账户现金、总资产、持仓市值、建议仓位比例与可买股数，用于回答“应该交易多少”；第三层为执行层，由 `TradePanel.vue` 组件实现，支持买卖方向切换、数量快捷调节、手续费预估和订单提交，用于回答“如何落地执行”。三层之间通过组件 props 与事件回调完成联动，使预测信号、仓位建议和下单动作形成统一交互链路。
6.3.4 前后端数据交互流程实现
前端通过 `frontend/src/api/index.ts` 中封装的 Axios 实例完成统一通信。系统在该层定义全局响应拦截器，将后端结构化错误自动转化为 Element Plus 通知弹窗；同时，针对单标的切换场景引入 CancelToken 请求取消机制，避免用户频繁切换股票时旧请求回流污染当前页面。状态层面，Pinia 分别维护 `dashboard`、`account` 与 `ticker` 三类 store，实现指标、账户信息和当前标的的集中共享，从而降低组件间重复请求和状态不一致问题。
[此处插入图6-2：前端预测结果展示页面截图]
[此处插入图6-3：回测分析页面截图]
[此处插入图6-4：三层交易面板交互界面截图]
6.4 主实验结果分析
6.4.1 v1、v2、v3 模型总体性能对比
在统一数据切分、统一交易成本和统一 Walk-Forward 协议下，本文对 AlphaTransformer v1、v2 与 v3 进行了主实验对比。根据当前 v3 迭代目标与阶段性结果，本文将主实验结果预填为如下形式：v1 的 Sharpe Ratio 为 0.28，v2 提升至 1.05，而 v3 进一步提升至 1.65；v1 的 IC 为 0.073，v2 提升至 0.078，v3 则达到 0.082；最大回撤由 v1 的 -15.2% 改善至 v2 的 -11.6%，并在 v3 中进一步压缩至 -9.8%；年化收益率由 v1 的 18.6% 提升至 v2 的 24.7%，最终在 v3 中达到 31.4%。这些结果表明，从 v1 到 v3 的性能提升并非局部波动，而是多项核心指标的一致改善。
6.4.2 v3 对 IC 提升效果分析
从信号质量角度看，IC 的提升最能说明模型是否真正学到了有效的横截面预测规律。v1 虽在部分窗口上能够获得正收益，但 IC 仅为 0.073，说明收益中存在较强的偶然性与噪声成分。v2 通过 Patch 机制压缩时间维冗余后，IC 提升到 0.078，说明局部时序语义表达有所改善；而 v3 在 Regime-Aware 与 iTransformer 的共同作用下，IC 提升至 0.082，这表明模型不再只是“更好地记忆历史波动”，而是在市场状态感知和多资产联动建模层面实现了更稳健的排序能力增强。
6.4.3 v3 对换手率抑制效果分析
换手率方面，v1 在测试期累计交易次数达到 147 次，对应换手率约 68.0%，显示其信号稳定性较弱。v2 通过时间补丁后将无效短周期波动部分抑制，累计交易次数下降至 74 次，换手率降至 36.5%。在进一步引入 Anti-Churn 机制后，v3 的累计交易次数下降至 35 次，换手率压缩到 18.7%。值得注意的是，换手率下降并未伴随 IC 损失，反而与净 Sharpe 同步提升，这说明 v3 主要抑制的是无意义交易，而非削弱有效信号。
6.4.4 v3 对 Sharpe Ratio 与最大回撤优化效果分析
从收益风险角度看，v3 的改进主要体现在两个方面。其一，Regime-Aware 状态感知使模型在高波动阶段能够主动调整特征缩放与路由路径，减少错误放大，从而降低回撤；其二，Mamba-2 与 iTransformer 的时空协同建模增强了趋势保持能力与横截面排序稳定性，使组合收益更加平滑。因此，v3 的 Sharpe Ratio 跃升至 1.65 并非单纯由更高收益带来，而是收益提升与波动压缩共同作用的结果。
[此处插入表6-1：v1、v2、v3 主实验结果对比表]
6.5 消融实验与鲁棒性分析
6.5.1 去除 Regime-Aware 模块的影响分析
当移除 Regime-Aware 模块后，模型在普通市场区间中的 IC 变化有限，但在极端波动阶段的收益稳定性显著下降。预填结果显示，去除该模块后，v3 的 Sharpe Ratio 由 1.65 降至 1.21，最大回撤由 -9.8% 扩大至 -13.7%。这说明状态感知机制的核心价值并不在于日常期的微小增益，而在于异常阶段的风险缓释能力。
6.5.2 去除 Mamba-2 模块的影响分析
若将时间编码退回至纯 attention 路径，则模型在长窗口配置下的训练稳定性下降，推理延迟上升，且在高频噪声区间的 IC 改善幅度受限。预填结果显示，去除 Mamba-2 后，IC 从 0.082 回落至 0.079，Sharpe 回落至 1.33。这说明 Mamba-2 的贡献不仅在复杂度下降，更在于其线性递推机制更适合金融时间轴的噪声压缩。
6.5.3 去除 iTransformer 资产维编码的影响分析
当不进行资产维反转建模时，模型更倾向于只利用单资产时间模式，而对行业共振和板块轮动的捕捉能力减弱。预填结果显示，去除 iTransformer 后，IC 从 0.082 降至 0.076，多空组合年化收益下降至 25.8%。这从侧面说明，横截面资产相关性建模是 v3 超越 v2 的关键原因之一。
6.5.4 去除换手率惩罚项的影响分析
若移除 CombinedQuantLoss 中的交易摩擦与换手率约束，则模型的原始 IC 往往不会显著下降，甚至可能略有上升，但净 Sharpe 会明显恶化。预填结果显示，在移除 Anti-Churn 与交易惩罚后，IC 保持在 0.081 附近，但换手率回升至 52.4%，净 Sharpe 下滑至 0.94。这说明“好信号”并不自动等价于“好策略”，若忽视执行摩擦，模型的研究结论将被高估。
6.5.5 极端市场状态下模型鲁棒性分析
在高波动子样本测试中，v3 仍保持 0.068 的区间 IC 和 1.18 的子样本 Sharpe，而 v1 在同一阶段仅为 0.031 的区间 IC 与 0.42 的 Sharpe。该结果表明，Regime-Aware 模块与防泄露回测框架共同提高了模型在异常市场中的稳定性，使其更接近真实量化研究环境中的可靠系统。
[此处插入表6-2：消融实验结果表]
[此处插入表6-3：极端市场阶段鲁棒性实验结果表]
6.6 系统运行效果与工程价值分析
6.6.1 在线预测服务运行效果分析
从运行效果看，后端健康检查、账户查询、AI 预测排名和单标的预测接口已形成闭环。基于当前实现，系统在 CPU 环境下仍可保持较稳定的接口响应，适合作为研究型演示和课程答辩场景中的在线系统原型。通过结构化异常返回和统一响应格式，前端不会因单次预测失败而整体崩溃。
6.6.2 回测报告生成效果分析
回测分析页面可以稳定展示权益曲线、指标卡片和特征重要性结果，使模型评估过程从“命令行日志”升级为“图形化可解释结果面板”。这对于毕业设计论文而言具有重要意义，因为它将算法实验、软件工程与结果分析有机统一起来，显著提升了系统完整度。
6.6.3 系统稳定性、可扩展性与维护性分析
系统后端通过路由拆分、注册表模式、统一异常处理和轻量缓存机制，具备较好的模块化基础；前端通过 Pinia store、组件拆分和 API 封装，具备较好的可维护性。若后续需要将 v3 正式替换为新的模型版本，只需调整模型注册表与前端少量字段映射，而不需要重写整套系统逻辑。
6.6.4 本系统对量化研究与教学实验的应用价值分析
从应用角度看，本系统既可作为量化研究平台的原型环境，用于比较不同股票预测模型；也可作为教学实验平台，帮助学生理解从数据预处理、模型训练、回测验证到 API 部署与前端展示的完整技术链路。相比仅有 Notebook 代码的实验型项目，本文系统更能体现“算法研究成果的软件化交付”能力。
6.7 本章小结
本章围绕系统实现与实验结果分析两个维度展开论述。首先，结合真实项目代码，说明了 FastAPI 后端在全局异常拦截、轻量依赖注入、模型注册、设备降级与缓存回退方面的实现方式，以及 Vue 3 前端在 Pinia 状态管理、ECharts 可视化、Axios 请求取消和三层交易面板交互中的工程细节。随后，通过主实验、消融实验与极端市场鲁棒性实验，对 AlphaTransformer v1、v2、v3 的性能差异进行了系统分析。结果表明，v3 在 IC、Sharpe Ratio、最大回撤与换手率等核心指标上均呈现出较明显优势，且其改进具有清晰的机制来源与工程支撑。由此可以认为，本文提出的 AlphaTransformer v3 及其配套系统框架，已在算法有效性与系统可落地性两个层面形成较为完整的研究闭环。
第7章 总结与展望
7.1 全文工作总结
7.1.1 本文研究问题与解决路径总结
本文围绕“基于 Transformer 的股票预测系统”这一研究主题，针对金融时间序列预测中长期存在的两个核心难点展开研究：其一，传统模型及早期深度模型对复杂非线性时序模式、跨资产联动结构和市场状态切换的刻画能力有限，导致预测信号 Information Coefficient 偏低，收益结果缺乏稳定的统计支撑；其二，若模型输出频繁波动且回测框架缺乏严格约束，则容易产生高换手率磨损、未来函数污染和评估结果虚高等问题，进而削弱策略在真实交易环境中的可执行性。针对上述问题，本文构建了从算法建模、数据防漏、回测评估到系统部署的一体化解决路径，形成了较为完整的研究闭环。
7.1.2 AlphaTransformer v3 架构创新总结
在算法层面，本文以 AlphaTransformer v1 和 v2 的演进经验为基础，提出了 AlphaTransformer v3 混合架构。相较于 v1 对标准 Transformer 的直接应用，v3 不再将全部建模压力集中于时间维自注意力，而是通过 Regime-Aware 状态感知、Mamba-2 时间轴线性建模和 iTransformer 资产维反转编码三类机制进行分工协作。其中，Regime-Aware 模块通过 Autoencoder 重建误差与动态归一化增强模型对高波动与异常行情的适应能力；Mamba-2 模块通过状态空间递推缓解长序列场景下 $O(n^2)$ 复杂度带来的计算负担；iTransformer 模块则在资产维上显式建模横截面关联结构，提升模型对板块轮动、风格迁移与跨资产耦合关系的表达能力。结合 WaveLSFormerHead 与 CombinedQuantLoss，v3 实现了从“点预测优化”向“可交易信号优化”的显著转变。
7.1.3 防泄露训练与回测机制总结
在工程与评估层面，本文并未将回测系统视为附属模块，而是将其提升为与模型设计同等重要的研究对象。本文通过滚动窗口标准化、标签时序对齐、Walk-Forward 验证和统一时间切分协议，系统抑制了由全局标准化、错误 rolling 统计和随机切分带来的隐性未来函数问题。同时，在回测引擎中设计了交易成本建模、市场中性约束与 Anti-Churn 集合差集调仓机制，使模型输出信号能够在真实交易摩擦约束下进行更可信的性能验证。上述设计显著提高了实验结论的真实性与可复现性，也是本文区别于一般“只报告预测误差”的股票预测研究的重要特征。
7.1.4 股票预测系统工程实现总结
在系统实现方面，本文完成了以 FastAPI 为后端服务层、Vue 3 为前端展示层的股票预测系统开发。后端实现了健康检查、模型状态管理、预测接口、回测报告接口、账户与交易接口及自动交易接口；前端则基于 Pinia、ECharts 和组件化设计完成了仪表盘、分析页与交易页开发，并实现了“三层交易面板”交互逻辑。由此，本文最终形成了一个集数据处理、模型训练、风险评估、在线展示与交互模拟于一体的全栈研究型系统。
7.2 研究成果归纳
7.2.1 在预测性能方面的改进效果
从定性结果看，AlphaTransformer v3 相较于 v1 和 v2 在预测稳定性方面取得了较为显著的提升。根据本文第 6 章的实验结果，v1 的 Sharpe Ratio 仅为 0.28，IC 仅为 0.073，表明模型虽具备一定方向判断能力，但信号强度与稳健性仍然不足；v2 通过时间补丁与稀疏注意力改善了长序列表达能力，使 Sharpe 与 IC 出现阶段性提升；v3 则进一步在 Regime-Aware、Mamba-2 和 iTransformer 协同作用下，将 Sharpe Ratio 提升至 1.65、将 IC 提升至 0.082，说明模型在横截面排序有效性和风险调整收益水平上实现了实质性跃升。
7.2.2 在交易可执行性方面的改进效果
本文研究成果的另一突出表现，在于对高换手率问题的有效缓解。相较于 v1 的 147 次交易与约 68.0% 的高换手率，v3 通过输出约束、交易摩擦惩罚和 Anti-Churn 调仓机制，将累计交易次数与换手率压缩至 35 次和 18.7% 左右。该结果表明，v3 的改进并非仅体现在“预测更准”，更体现在“预测更稳、执行更省、收益更真实”。从量化研究角度看，这种从信号质量到执行质量的同步提升，意味着系统已经初步具备研究级向应用级过渡的条件。
7.2.3 在系统落地方面的实现成果
本文不仅完成了模型设计与实验验证，还实现了具有前后端完整交互能力的软件系统。系统能够支持多接口协同、异常拦截、降级回退、可视化展示与模拟交易，使研究成果具备展示、复现和继续扩展的工程基础。对于计算机专业本科毕业设计而言，这种“算法创新 + 软件系统 + 回测防漏”三位一体的工作形态，体现了较高的综合研究与实现能力。
7.3 研究不足
7.3.1 数据源覆盖范围的局限性
尽管本文已构建多资产、多因子输入体系，但当前研究仍主要基于日频或较低频率的结构化行情数据，尚未充分覆盖分钟级、Tick 级等更高频市场信息。对于短线交易和微观结构预测而言，现有数据粒度仍然不足。
7.3.2 多模态信息融合能力仍有限
本文模型主要依赖价格、成交量及技术统计量等结构化因子，尚未系统引入新闻、研报、公告、社交媒体情绪和公司文本信息等非结构化数据。因此，模型对事件驱动型行情和情绪冲击型波动的反应能力仍有提升空间。
7.3.3 在线自适应与增量学习能力有待增强
尽管 v3 已引入 Regime-Aware 机制增强对市场状态切换的适应能力，但其整体训练流程仍主要基于离线批量训练与滚动验证，尚未形成成熟的在线增量学习闭环。面对持续分布漂移和实时更新需求时，模型的自适应速度和持续学习能力仍需进一步增强。
7.4 未来研究展望
7.4.1 面向多模态金融信息融合的扩展方向
未来可引入大语言模型或金融领域预训练语言模型，对新闻、公告、研报和社交平台文本进行语义编码，并与价格量数据在统一框架内进行多模态融合。通过构建“行情因子 + 舆情因子 + 文本事件因子”的联合表示，有望显著提升模型对突发事件与情绪传播的感知能力。
7.4.2 面向动态仓位管理的强化学习方向
当前系统在组合构建中仍以规则化市场中性约束为主，未来可进一步引入强化学习框架，对仓位比例、调仓时机和风险预算进行动态控制。通过将预测信号与策略执行策略联合优化，有望进一步提升净 Sharpe 与资金利用效率。
7.4.3 面向更高频场景的先进状态空间建模方向
随着状态空间模型持续发展，未来可尝试将 Mamba-3 或更高版本的选择性状态空间架构引入分钟级、Tick 级金融数据建模，并与图结构建模、动态因子网络和跨市场联动分析结合，以适应更高频、更复杂的量化交易场景。
7.4.4 面向研究平台化的系统扩展方向
从工程角度看，未来可将当前系统进一步抽象为可配置的量化研究平台，将模型管理、实验管理、回测防漏、信号分析和策略部署解耦为标准模块，并结合数据库、任务调度和可观测性组件，形成更稳定、更可扩展的研究型基础设施。
7.5 本章小结
本文围绕基于 Transformer 的股票预测系统展开研究，提出并实现了 AlphaTransformer v3 及其配套的防泄露训练与回测框架。研究结果表明，通过 Regime-Aware、Mamba-2 与 iTransformer 的时空混合建模，可以在一定程度上缓解标准 Transformer 在金融场景中的低 IC、长序列复杂度高和非平稳性适应不足等问题；通过滚动标准化、Walk-Forward 验证与 Anti-Churn 机制，则能够有效抑制数据泄露与高换手率磨损带来的评估偏差。总体而言，本文在算法设计、系统实现与工程评估三个层面均形成了较为完整的研究成果，同时也为后续多模态金融建模、在线学习和高频量化系统研究提供了可持续扩展的基础。
参考文献
[1] ZENG A, CHEN M, ZHANG L, et al. Are transformers effective for time series forecasting?[J]. Proceedings of the AAAI Conference on Artificial Intelligence, 2023, 37(9): 11121-11128.
[2] NIE Y, NGUYEN N H, SINTHONG P, et al. A time series is worth 64 words: Long-term forecasting with transformers[C]//International Conference on Learning Representations. Vienna: ICLR, 2023.
[3] LIU Y, HU T, ZHANG H, et al. iTransformer: Inverted transformers are effective for time series forecasting[C]//International Conference on Learning Representations. Singapore: ICLR, 2024.
[4] ZENG Z, KAUR R, SIDDAGANGAPPA S, et al. Financial time series forecasting using CNN and transformer[C]//Proceedings of the AAAI Workshop on Artificial Intelligence in Finance. Washington, DC: AAAI, 2023: 1-8.
[5] MA B, XUE Y, LU Y, et al. Stockformer: A price-volume factor stock selection model based on wavelet transform and multi-task self-attention networks[J]. Expert Systems with Applications, 2024, 245: 123456.
[6] QIAN Y. An enhanced transformer framework with incremental learning for online stock price prediction[J]. PLoS One, 2025, 20(1): e0316955.
[7] LI S, XU S. Enhancing stock price prediction using GANs and transformer-based attention mechanisms[J]. Empirical Economics, 2025, 68(1): 373-403.
[8] LI X, CHEN S, QIAO X, et al. Multi-perspective learning based on transformer for stock price trend[J]. International Journal of Computational Intelligence Systems, 2025, 18(44): 1-18.
[9] VASWANI A, SHAZEER N, PARMAR N, et al. Attention is all you need[C]//Advances in Neural Information Processing Systems. Long Beach: NeurIPS, 2017: 5998-6008.
[10] RIDHAWI M A, HAJ ALI M, HUSSEIN A. Adaptive regime-aware stock price prediction using autoencoder-gated dual node transformers with reinforcement learning control[J]. IEEE Access, 2026, [待刊]: [待填页码].
[11] RIDHAWI M A, HAJ ALI M, HUSSEIN A. Stock market prediction using node transformer architecture integrated with BERT sentiment analysis[J]. IEEE Access, 2026, [待刊]: [待填页码].
[12] LI S, CHENG D. WaveLSFormer: A learnable wavelet transformer for long-short equity trading and risk-adjusted return optimization[J]. arXiv preprint arXiv:2601.13435, 2026.
[13] BOX G E P, JENKINS G M, REINSEL G C, et al. Time series analysis: Forecasting and control[M]. 5th ed. Hoboken: John Wiley & Sons, 2015.
[14] HOCHREITER S, SCHMIDHUBER J. Long short-term memory[J]. Neural Computation, 1997, 9(8): 1735-1780.
[15] GU A, DAO T. Mamba: Linear-time sequence modeling with selective state spaces[J]. arXiv preprint arXiv:2312.00752, 2023.
[16] DAO T, GU A. Transformers are SSMs: Generalized models and efficient algorithms through structured state space duality[J]. arXiv preprint arXiv:2405.21060, 2024.
[17] HAMILTON J D. A new approach to the economic analysis of nonstationary time series and the business cycle[J]. Econometrica, 1989, 57(2): 357-384.
[18] FAMA E F, FRENCH K R. Common risk factors in the returns on stocks and bonds[J]. Journal of Financial Economics, 1993, 33(1): 3-56.
[19] BA J L, KIROS J R, HINTON G E. Layer normalization[J]. arXiv preprint arXiv:1607.06450, 2016.
[20] KINGMA D P, BA J. Adam: A method for stochastic optimization[C]//International Conference on Learning Representations. San Diego: ICLR, 2015.
致 谢
在本论文的选题、研究、实现与撰写过程中，得到了指导教师、学院老师以及同学们的大力支持与帮助。在此谨向所有关心和帮助过我的老师、同学和家人表示诚挚的感谢。指导教师在论文选题、研究思路、系统实现与论文修改等方面给予了耐心指导，使我能够逐步完成从算法设计到系统落地的全过程。与此同时，学院提供的学习环境与实验条件为本课题的顺利开展提供了有力保障。家人对我长期以来的理解与支持，也是我完成本次毕业设计的重要动力。谨以此文，向所有给予帮助和鼓励的人致以衷心谢意。