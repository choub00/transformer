---
source_file: "d:\transformer\utils\normalization.py"
type: "code"
community: "AlphaTransformer Core Models"
location: "L140"
tags:
  - graphify/code
  - graphify/INFERRED
  - community/AlphaTransformer_Core_Models
---

# PanelNormalizer

## Connections
- [[.__init__()_61]] - `method` [EXTRACTED]
- [[.fit_transform_panel()]] - `method` [EXTRACTED]
- [[.process_raw_data()]] - `calls` [INFERRED]
- [[.transform_panel()]] - `method` [EXTRACTED]
- [[AlphaDataset]] - `uses` [INFERRED]
- [[AlphaPredictor - AI 预测器  这是一个模拟的 AI 预测器，用于在没有真实模型的情况下提供预测信号。 在生产环境中应替换为真实的 Alpha]] - `uses` [INFERRED]
- [[Args             features  num_samples, num_assets, history_len, num_feature]] - `uses` [INFERRED]
- [[DataProcessor]] - `uses` [INFERRED]
- [[InferenceError]] - `uses` [INFERRED]
- [[ModelRegistry]] - `uses` [INFERRED]
- [[normalization.py]] - `contains` [EXTRACTED]
- [[创建 PyTorch DataLoader         注意：shuffle=False（时间序列绝对不打乱！）]] - `uses` [INFERRED]
- [[加载模型检查点到指定设备         健壮性保证：           - map_location 强制 CPU（防止 CUDA OOM 导致 500]] - `uses` [INFERRED]
- [[处理原始价格数据，生成模型输入          Args             price_df  Date, Asset 收盘价（Raw C]] - `uses` [INFERRED]
- [[多资产时间序列数据集      数据格式：         features  num_samples, num_assets, history_le]] - `uses` [INFERRED]
- [[多资产面板数据的滚动归一化      数据格式：Date, Asset, Features     对每个 Asset × Feature 组合独立做]] - `rationale_for` [EXTRACTED]
- [[执行推理，返回预测数组          Args             features  num_assets, history_len, n]] - `uses` [INFERRED]
- [[按时间顺序划分数据集（绝对不打乱！）          Returns             {'train' (X, y), 'val' (X,]] - `uses` [INFERRED]
- [[推理异常：携带错误码和上下文，不抛出 500]] - `uses` [INFERRED]
- [[数据加载与预处理模块（严格 Anti-Leakage）  核心原则：   1. 所有未来数据不得进入当前时间点的特征   2. 目标值使用显式 shif]] - `uses` [INFERRED]
- [[数据预处理流水线（Anti-Leakage 版本）      处理步骤（严格时序）：         1. 计算对数收益率（shift(-1) 构造）]] - `uses` [INFERRED]
- [[生成合成价格数据用于测试      Args         num_dates  交易日数量         num_assets 资产数量]] - `uses` [INFERRED]

#graphify/code #graphify/INFERRED #community/AlphaTransformer_Core_Models