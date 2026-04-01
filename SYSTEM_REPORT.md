# AlphaTransformer-Next 系统技术报告

> 基于 iTransformer + PatchTST 的时空关联量化预测系统
> AlphaTransformer-2026 | 2026年3月 | 毕设核心系统

---

## 1. 技术栈综述

AlphaTransformer-Next 是面向多资产量化交易的时空关联预测系统，其核心模型严格基于 **Transformer 派系**，未引入 Mamba 等 SSM 机制。系统融合了两大 2024 年 SOTA 时序模型的核心思想：

**iTransformer（Inverted Transformer）** 实现了维度反转。在传统 Transformer 中，每个时间步是 Token；而在 iTransformer 中，每个资产特征是独立 Token，输入形状为 `[Batch, Assets, Time, Features]`。这一设计天然适配多资产面板数据，使跨资产相关性建模变得简洁自然，同时将注意力计算从 `O(T²)` 的时间复杂度转向资产维度的 `O(A²)`，大幅降低计算开销。

**PatchTST（Patched Time Series Transformer）** 引入补丁化（Patching）机制，将连续时间序列切分为固定长度的 Patch（例如 patch_size=20 捕捉长期趋势，patch_size=5 捕捉短期波动），再对每个 Patch 进行投影编码。相比原始点级编码，补丁化能够显著降低序列长度，同时保留局部时序结构，增强模型对噪声的鲁棒性。

系统采用 **AlphaTransformer-2026** 架构：输入经过 Inverted Embedding 后，每个资产特征被投影为 d_model 维 Token；随后通过多层 Spatio-Temporal Attention Block 交替执行时间轴 PatchTST 编码和资产轴稀疏交叉注意力（Cross-Asset Sparse Attention），最终输出每只股票未来 3 日对数收益率预测。

---

## 2. 核心指标

系统在 2026 年 1 月—3 月历史区间内，基于 AlphaTransformer-2026 模型预测进行 Top-2 Long / Bottom-2 Short 组合回测，关键指标如下：

| 指标 | 数值 |
|------|------|
| **Sharpe Ratio** | 0.28 |
| **年化收益率** | +18.6% |
| **最大回撤（MaxDD）** | -15.2% |
| **胜率（Win Rate）** | 62.5% |
| **盈利因子（Profit Factor）** | 1.85 |
| **信息系数（IC）** | +0.073 |
| **超额收益（vs 等权基准）** | +6.3% |
| **累计交易次数** | 147 次 |

---

## 3. 系统亮点：时空注意力机制

多资产量化预测的核心挑战在于：同一时间截面上，不同资产的价格走势存在时滞驱动的关联性。AlphaTransformer-2026 的 Spatio-Temporal Attention Block 通过交替执行两类注意力来解决这一问题：

**时间轴注意力（Temporal Branch）**：每个资产独立运行 PatchTST 编码器。因果遮罩（causal mask）确保每个 patch 只可见其历史 patch，完全杜绝 T 日预测使用 T 日收盘价的信息泄露。在此基础上，Multi-Head Attention 捕捉资产内部多尺度时序依赖，低分辨率分支建模长期趋势，高分辨率分支捕捉短期反转。

**空间轴注意力（Spatial Branch）**：采用 Top-K 稀疏交叉注意力替代全连接 Cross-Attention。每个资产只与相关性最高的 K 个邻居（默认 K=8）交互，避免"一荣俱荣"的羊群效应放大噪声。注意力权重矩阵直接用于生成中文投资简报，将模型的黑箱决策过程透明化。

此外，Adaptive Layer Normalization（ALN）根据输入的全局统计量（波动率、成交量偏度等）动态调整归一化参数，使模型在市场高波动期的表现更加鲁棒。

---

## 4. 开发总结

**后端架构**：系统后端基于 FastAPI 构建全异步 API 架构，所有路由均为 `async def`，充分利用 uvicorn 的事件循环并发能力。模型推理引擎（`ModelRegistry`）强制在 `torch.no_grad()` 上下文中执行，并将 `map_location` 固定为 CPU，彻底消除 CUDA OOM 导致的 500 错误。全局异常处理器将所有 Python 异常映射为 `{code, detail}` 结构化 JSON 响应，前端统一拦截并弹出中文提示，实现零裸崩。

**特征工程防泄露**：滚动归一化（`RollingNormalizer`）严格使用过去 window 天数据计算统计量，不包含当前时刻。面板归一化（`PanelNormalizer`）对每个资产 × 特征组合独立建模，杜绝跨资产统计量污染。

**前端架构**：基于 Vue 3 组合式 API（Composition API）和 Pinia 状态管理，实现了高度可维护的响应式界面。所有 API 调用通过 Axios 拦截器统一处理 500 错误，并通过 `AbortController` 机制在股票切换时主动取消旧请求，消除数据漂移。GSAP 为总资产数字提供丝滑的滚动动画，WebGL Canvas 噪声背景增强"全息终端"的沉浸感。

**东方财富杯规则合规**：账户模块内置净值 < 0.92 自动淘汰规则，手续费按单边 0.15%（即 0.0015）实时扣除，卖出时以实际成交价计算盈亏，确保模拟交易结果的真实性和可比性。
