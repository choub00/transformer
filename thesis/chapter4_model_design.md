# 第4章 AlphaTransformer 模型设计与关键算法实现

## 4.1 问题形式化定义

### 4.1.1 多资产多因子输入表示

设在时刻 $t$ 的股票池规模为 $N$，回看窗口长度为 $T$，每只资产包含 $F$ 维输入特征，则系统输入可表示为
$$
X_t \in \mathbb{R}^{B \times T \times N \times F},
$$
其中 $B$ 表示批大小。对第 $b$ 个样本、第 $i$ 只资产在窗口内的特征序列记为
$$
X_{b,:,i,:}=\{x_{t-T+1}^{(i)},x_{t-T+2}^{(i)},\dots,x_t^{(i)}\}.
$$
本文目标并非单纯预测单资产价格，而是学习横截面 alpha 信号
$$
\hat{\mathbf{y}}_{t+H}=[\hat y_{t+H}^{(1)},\dots,\hat y_{t+H}^{(N)}]^\top,
$$
使其与未来收益向量
$$
\mathbf{r}_{t+H}=[r_{t+H}^{(1)},\dots,r_{t+H}^{(N)}]^\top
$$
在排序意义上保持一致，从而支持多空组合构建。

### 4.1.2 历史窗口、预测窗口与标签构造方式

未来 $H$ 步收益定义为
$$
r_{t+H}^{(i)}=\frac{P_{t+H}^{(i)}-P_t^{(i)}}{P_t^{(i)}}.
$$
为兼顾回归与方向判别，本文同时构造方向标签
$$
d_{t+H}^{(i)}=\mathbb{I}(r_{t+H}^{(i)}>0).
$$
因此，模型需要同时输出连续收益信号与方向概率，前者用于横截面排序，后者用于增强方向一致性约束。

### 4.1.3 股票预测任务的目标函数定义

给定参数 $\theta$，本文求解的核心问题可写为
$$
\theta^\ast=\arg\min_{\theta}\ \mathcal{L}_{quant}(f_\theta(X_t),\mathbf{r}_{t+H},\mathbf{d}_{t+H}),
$$
其中 $\mathcal{L}_{quant}$ 为兼顾预测误差、风险调整收益和方向判别的联合量化损失。相较于传统最小均方误差目标，该定义更贴近真实交易需求。

## 4.2 AlphaTransformer v1 与 v2 基线模型分析

### 4.2.1 v1 原生 Transformer 架构设计

AlphaTransformer v1 以标准 Transformer 为主体，将时间维特征编码后通过跨资产注意力生成 alpha 分数。其基本优势在于结构统一、易于训练，并能初步捕捉多资产间的共振关系。然而，v1 的核心计算仍依赖标准自注意力，其时间复杂度为
$$
O(T^2D),
$$
当 $T$ 较长时，注意力矩阵既放大计算负担，也放大噪声传播路径。

### 4.2.2 v1 模型在 IC 与换手率上的主要缺陷

根据项目文档，v1 的 Sharpe Ratio 仅为 $0.28$，Information Coefficient 仅为 $0.073$，最大回撤达到 $-15.2\%$。这说明 v1 的核心问题不是“没有收益”，而是“收益缺乏足够强的预测信号支撑”。从机制上看，原因主要有三点。第一，标准 attention 将所有时点两两关联，容易在金融高噪声序列中产生无效注意力权重，导致表征稀释。第二，v1 默认全市场服从统一分布，忽略了波动期、平稳期和危机期之间的显著状态差异。第三，信号稳定性不足导致排序结果频繁翻转，进一步诱发高换手率，使账面收益被交易摩擦侵蚀。

### 4.2.3 v2 中 PatchTST 与稀疏注意力改进思路

为缓解 v1 在长序列建模上的缺陷，v2 引入 PatchTST 风格的时间补丁表示。设 patch 长度为 $P$，步长为 $S$，则 token 数量由原始时间长度 $T$ 压缩为
$$
M=\left\lfloor \frac{T-P}{S}\right\rfloor+1,
$$
从而将时间轴 attention 的理论复杂度由 $O(T^2)$ 降低为 $O(M^2)$。与此同时，稀疏注意力机制通过只保留局部窗口或 Top-$k$ 相关连接，进一步削减冗余计算。

### 4.2.4 v2 模型改进效果与剩余问题分析

v2 在长序列处理效率与局部模式提取方面优于 v1，这是一次有效的结构优化。然而，v2 仍未解决两个根本问题。其一，Patch 与稀疏 attention 只是在计算路径上做压缩，并未显式建模市场状态切换，因此对非平稳行情的适应仍然有限。其二，v2 的核心视角仍以时间 token 为主，对多资产横截面耦合关系的表达不足，难以充分捕捉板块联动与风格迁移。由此，v3 的架构升级不应停留于“更快的 attention”，而应转向“状态感知 + 线性时间建模 + 资产维建模”的联合重构。

[此处插入图4-1：AlphaTransformer v1、v2、v3 架构演进图]

## 4.3 AlphaTransformer v3 总体架构设计

### 4.3.1 v3 的整体设计目标

AlphaTransformer v3 的设计目标可以概括为：在提升 IC 的同时抑制换手率，在增强预测能力的同时保证可交易性。为此，v3 不再依赖单一主干网络，而是由 Regime-Aware 市场感知模块、Mamba-2 时间编码模块、iTransformer 资产编码模块以及 WaveLSFormerHead 输出层协同组成。

### 4.3.2 Regime-Aware + Mamba-2 + iTransformer 混合框架

设输入张量经线性嵌入后得到
$$
H^{(0)} \in \mathbb{R}^{B \times T \times N \times D}.
$$
随后，v3 按如下顺序处理：
$$
H^{(1)}=\mathrm{RegimeAware}(H^{(0)}),
$$
$$
H^{(2)}=\mathrm{Mamba2Temporal}(H^{(1)}),
$$
$$
H^{(3)}=\mathrm{iTransformerAsset}(H^{(2)}),
$$
$$
\hat{\mathbf{y}},\mathbf{w}=\mathrm{WaveLSFormerHead}(H^{(3)}).
$$
其中 $\mathbf{w}$ 表示投组合权重，直接服务于后续模拟收益与 Sharpe 优化。

### 4.3.3 v3 模型各子模块协同关系

上述结构的逻辑十分明确：Regime-Aware 负责回答“当前市场处于何种状态”；Mamba-2 负责高效提炼时间轴动态；iTransformer 负责捕捉资产间横截面关联；输出头负责将预测信号约束到市场中性多空决策空间。这样，v3 才能同时回应 v1 的低 IC 问题与高换手率问题。

[此处插入图4-2：AlphaTransformer v3 整体架构流图]

## 4.4 市场状态感知模块设计

### 4.4.1 基于 Autoencoder 的市场状态检测器设计

为识别异常波动与分布突变，本文先利用 Autoencoder 对市场特征进行重构。对输入向量 $x_t$，编码与解码分别为
$$
z_t=f_{enc}(x_t),\qquad \hat x_t=f_{dec}(z_t).
$$
其重建损失定义为
$$
\mathcal{L}_{AE}=\frac{1}{B}\sum_{t=1}^{B}\|x_t-\hat x_t\|_2^2.
$$
相应地，单样本重建误差为
$$
e_t=\|x_t-\hat x_t\|_2^2.
$$
当 $e_t$ 显著升高时，说明当前样本偏离“常态市场”分布，可视为高波动或危机状态候选。

### 4.4.2 市场状态概率分布建模方法

令 pooled 表征为 $u_t=\mathrm{Pool}(H_t)$，将其与重建误差拼接后输入状态分类器：
$$
q_t=[u_t;e_t],
$$
$$
\mathbf{p}_t=\mathrm{Softmax}(W_r q_t+b_r),
$$
其中
$$
\mathbf{p}_t=[p_t^{(1)},p_t^{(2)},p_t^{(3)}]
$$
分别对应平稳、波动和危机三类市场状态，满足
$$
\sum_{k=1}^{3}p_t^{(k)}=1.
$$

### 4.4.3 RegimeAwareNorm 自适应归一化机制设计

设当前隐藏表征为 $H_t \in \mathbb{R}^{B \times N \times D}$，其逐样本归一化写为
$$
\tilde H_t=\frac{H_t-\mu(H_t)}{\sigma(H_t)+\epsilon}.
$$
与普通 LayerNorm 不同，v3 的缩放因子与平移因子由状态概率动态生成：
$$
\gamma_t=W_\gamma \mathbf{p}_t+b_\gamma,\qquad
\beta_t=W_\beta \mathbf{p}_t+b_\beta.
$$
因此，自适应层归一化定义为
$$
\mathrm{ALN}(H_t,\mathbf{p}_t)=\gamma_t \odot \tilde H_t+\beta_t.
$$
当市场进入高波动状态时，$\gamma_t$ 与 $\beta_t$ 会自动调节特征尺度，使模型在不同 regime 下拥有不同的响应模式。

### 4.4.4 极端市场下动态路由机制的理论分析

进一步地，可将状态概率用于专家融合：
$$
\hat y_t=\sum_{k=1}^{3}p_t^{(k)} f_k(H_t),
$$
即利用软路由在不同状态专家间加权，从而避免单一预测器对所有行情“一刀切”。这对于金融非平稳场景尤为关键，因为极端时期低 IC 的根源往往不是参数不足，而是模型假设失配。

[此处插入图4-3：Regime-Aware 状态感知与动态路由机制示意图]

## 4.5 时间维高效编码模块设计

### 4.5.1 PatchTST 多尺度时间补丁表示方法

对每只资产的时间序列，v3 先进行 patch 化，以减少原始长度并增强局部结构表达。设 patch 操作为 $\mathcal{P}(\cdot)$，则
$$
X_t^{patch}=\mathcal{P}(X_t)\in\mathbb{R}^{B\times M\times N\times D},
$$
其中 $M \ll T$。该表示为后续 Mamba-2 提供更稳定的局部时间片输入。

### 4.5.2 Mamba-2 时间编码器设计

Mamba-2 采用离散状态空间递推。对时间步 $m$，其更新写为
$$
h_m=\bar A_m h_{m-1}+\bar B_m x_m,
$$
$$
y_m=C_m h_m + D x_m,
$$
其中 $\bar A_m,\bar B_m,C_m$ 可依赖当前输入 $x_m$ 动态生成，从而体现 selective scan 机制。相较标准 attention 直接构造 $M\times M$ 相关矩阵，Mamba-2 仅进行线性递推，因此时间复杂度近似为
$$
O(M D d_s),
$$
其中 $d_s$ 为状态维度。

### 4.5.3 时间维线性复杂度优势分析

若 Transformer 时间编码复杂度为
$$
O(M^2D),
$$
则在 $M$ 较大时，Mamba-2 的
$$
O(M D d_s)
$$
显著优于二次复杂度。对于高频金融任务，这种复杂度下降不仅意味着训练更快，更重要的是允许系统在固定显存预算下保留更长历史窗口，从而增强对长期趋势与状态切换的识别能力。

### 4.5.4 与标准自注意力机制的对比讨论

Transformer 擅长显式建模任意两时点关系，但在高噪声金融数据中，这种全连接关系不一定必要；Mamba-2 通过状态递推更适合提炼“对未来真正有贡献”的时序信息。因此，v3 在时间维选择 Mamba-2，不是简单追求新结构，而是基于金融场景的复杂度与噪声抑制需求所做出的架构决策。

## 4.6 资产维相关性建模模块设计

### 4.6.1 iTransformer 资产维反转编码原理

时间编码后，隐藏表征为
$$
H^{(2)}\in\mathbb{R}^{B\times T\times N\times D}.
$$
传统做法通常沿时间维进行 self-attention，而 v3 借鉴 iTransformer 思想，将张量重排为
$$
\tilde H^{(2)}=\mathrm{Permute}(H^{(2)})\in\mathbb{R}^{B\times N\times T\times D}.
$$
即将“资产”提升为主要 token 维度，每只资产携带完整时间轨迹表征。

### 4.6.2 跨资产关联关系建模方法

对每个资产 token，将其时间维压缩或投影为
$$
a_i=\phi(\tilde H^{(2)}_{:,i,:,:})\in\mathbb{R}^{B\times D_a},
$$
进而形成资产 token 矩阵
$$
A=[a_1,\dots,a_N]^\top\in\mathbb{R}^{B\times N\times D_a}.
$$
随后在资产维执行 attention：
$$
\mathrm{Attn}_{asset}(A)=\mathrm{Softmax}\left(\frac{Q_A K_A^\top}{\sqrt{D_a}}\right)V_A.
$$
这样，模型学习到的不再是“哪些时间点相关”，而是“哪些资产之间存在同步、轮动或传染关系”。

### 4.6.3 时空混合表示融合策略

时间编码结果与资产编码结果通过残差融合：
$$
H^{(3)}=\mathrm{Fuse}(H^{(2)},\mathrm{Attn}_{asset}(A)),
$$
其中 Fuse 可取拼接后线性映射，或加权残差：
$$
H^{(3)}=\lambda H^{(2)}+(1-\lambda)\hat H_{asset}.
$$
该融合使模型同时保留时间动态与横截面关系。

### 4.6.4 板块联动与风格迁移信息的编码逻辑

在股票市场中，预测信号往往并非来自单资产孤立轨迹，而来自行业共振、估值风格切换和资金流迁移。iTransformer 风格的资产维建模天然更适合表达此类结构，也是 v3 相较 v2 在多资产联动上实现跃升的关键原因。

[此处插入图4-4：Mamba-2 时间轴编码与 iTransformer 资产轴编码协同示意图]

## 4.7 输出层与损失函数设计

### 4.7.1 WaveLSFormerHead 输出头结构设计

设最终隐藏表示为 $H^{(3)}$，输出头生成原始评分 $\mathbf{s}\in\mathbb{R}^{B\times N}$。为得到市场中性多空权重，定义可行域
$$
\mathcal{W}=\left\{\mathbf{w}\in\mathbb{R}^{N}\mid \sum_{i=1}^{N}w_i=0,\ \|\mathbf{w}\|_1=1,\ |w_i|\le w_{max}\right\}.
$$
WaveLSFormerHead 将原始评分投影到该可行域：
$$
\mathbf{w}=\Pi_{\mathcal{W}}(\mathbf{s}).
$$
因此天然满足
$$
\sum_{i=1}^{N}w_i=0,
$$
即市场中性约束，同时
$$
|w_i|\le w_{max}
$$
限制单资产过度集中。

### 4.7.2 CombinedQuantLoss 联合损失函数定义

本文定义联合损失为
$$
\mathcal{L}_{CQ}=\lambda_h \mathcal{L}_{Huber}+\lambda_s \mathcal{L}_{Sharpe}+\lambda_d \mathcal{L}_{BCE}.
$$

其中，Huber 损失用于稳健回归：
$$
\mathcal{L}_{Huber}=
\frac{1}{BN}\sum_{b,i}
\begin{cases}
\frac{1}{2}(r_{b,i}-\hat y_{b,i})^2, & |r_{b,i}-\hat y_{b,i}|\le \delta,\\
\delta |r_{b,i}-\hat y_{b,i}|-\frac{1}{2}\delta^2, & \text{otherwise}.
\end{cases}
$$

### 4.7.3 面向 IC 提升的排序约束项设计

为使损失贴近组合表现，先定义单期组合净收益
$$
R_t^{p}=\sum_{i=1}^{N}w_t^{(i)} r_{t+1}^{(i)}-c\cdot \mathrm{Turnover}_t.
$$
则模拟 Sharpe 损失写为
$$
\mathcal{L}_{Sharpe}=-\frac{\mu(R^p)}{\sigma(R^p)+\epsilon}.
$$
该项直接鼓励更高风险调整收益，而非只追求点预测精度。

### 4.7.4 面向换手率抑制的交易摩擦惩罚项设计

方向一致性项采用二元交叉熵：
$$
\mathcal{L}_{BCE}=-\frac{1}{BN}\sum_{b,i}\left[d_{b,i}\log \sigma(\hat y_{b,i})+(1-d_{b,i})\log(1-\sigma(\hat y_{b,i}))\right].
$$
同时，换手率惩罚已通过 $R_t^p$ 中的成本项显式进入 Sharpe loss，从而使模型在训练阶段就感知交易摩擦。相比只在回测后扣减成本，这种设计更有助于抑制信号抖动和无效调仓。

## 4.8 模型训练与优化策略

### 4.8.1 优化器与学习率调度方法

本文训练阶段采用 AdamW 优化器，并结合余弦退火调度稳定收敛。对参数 $\theta$ 的更新可写为
$$
\theta_{k+1}=\theta_k-\eta_k \frac{\hat m_k}{\sqrt{\hat v_k}+\epsilon}-\eta_k\lambda \theta_k.
$$
其中 $\eta_k$ 为动态学习率，$\lambda$ 为权重衰减系数。

### 4.8.2 自主实验循环与超参数搜索机制

为提高迭代效率，系统采用自主实验循环机制，对 patch 长度、状态维度、损失权重和持仓约束进行网格化或分阶段搜索，并以验证集 IC、Sharpe 和换手率作为联合筛选标准。

### 4.8.3 模型回退、降级与异常恢复机制

考虑到复杂模型可能存在训练不稳定或推理依赖异常，系统保留 v2 乃至 v1 的回退路径。当 v3 在特定窗口出现异常波动时，可退回已验证的稳定版本，保证服务连续性。

## 4.9 模型复杂度与理论分析

### 4.9.1 各版本模型复杂度对比分析

v1 的核心复杂度为
$$
O(T^2D),
$$
v2 在 patch 化后约为
$$
O(M^2D),\quad M<T,
$$
而 v3 的时间轴主干近似为
$$
O(MDd_s)+O(N^2D_a),
$$
即将原本完全依赖时间二次复杂度的问题，拆分为“线性时间建模 + 资产维注意力建模”。

### 4.9.2 v3 相对 v1 与 v2 的理论优势分析

v1 的主要问题是“全局 attention 过重而状态感知不足”；v2 的主要问题是“时间效率改善但市场状态与横截面结构仍建模不足”；v3 则通过 Regime-Aware、Mamba-2 和 iTransformer 的分工协作，将“非平稳性”“长序列复杂度”“多资产联动”三类问题同时纳入统一框架。

### 4.9.3 模型在金融非平稳场景中的适应性讨论

从理论上看，v3 的优势不在于单个模块绝对更强，而在于每个模块都针对金融时序的真实痛点而设计。因此，它更有可能在滚动回测和极端行情测试中表现出稳定 IC 与更低换手率，而非只在单一切片数据上取得表面最优。

[此处插入表4-1：各版本模型核心模块对比表]

## 4.10 本章小结

本章围绕 AlphaTransformer 的架构演进与关键算法实现展开论述。首先，分析了 v1 原生 Transformer 在 IC 偏低、换手率偏高方面的结构性缺陷，以及 v2 虽通过 PatchTST 与稀疏注意力缓解长序列问题，但仍难以充分应对市场非平稳性和多资产联动建模不足的局限。随后，系统提出 v3 的整体框架，并分别从 Regime-Aware 市场状态感知、Mamba-2 时间维线性建模、iTransformer 资产维反转编码以及 WaveLSFormerHead 与 CombinedQuantLoss 的交易导向输出层四个方面进行了形式化定义。整体来看，v3 是对前两版模型的体系化重构，其目标并非单纯提升预测精度，而是从根本上改善低 IC 与高换手率两项核心问题。下一章将在此基础上，进一步给出防泄露训练框架与回测评估方法设计。
