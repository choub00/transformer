---
source_file: "d:\transformer\models\alpha_transformer.py"
type: "code"
community: "AlphaTransformer Core Models"
location: "L561"
tags:
  - graphify/code
  - graphify/INFERRED
  - community/AlphaTransformer_Core_Models
---

# AlphaTransformerV2

## Connections
- [[.__init__()_31]] - `method` [EXTRACTED]
- [[._build_causal_mask()_1]] - `method` [EXTRACTED]
- [[.forward()_7]] - `method` [EXTRACTED]
- [[AlphaPredictor - AI 预测器  这是一个模拟的 AI 预测器，用于在没有真实模型的情况下提供预测信号。 在生产环境中应替换为真实的 Alpha]] - `uses` [INFERRED]
- [[AlphaTransformer V2 支持动态资产数的版本      与 V1 的区别：         1. 不硬编码 num_assets，通过 x.s]] - `rationale_for` [EXTRACTED]
- [[AlphaTransformerTrainer]] - `uses` [INFERRED]
- [[HuberLoss]] - `uses` [INFERRED]
- [[InferenceError]] - `uses` [INFERRED]
- [[Mixed Huber Loss 结合 MSE 和 MAE 的优点      当 error = delta 时使用 MSE（平滑梯度）]] - `uses` [INFERRED]
- [[MixedHuberLoss]] - `uses` [INFERRED]
- [[ModelRegistry]] - `uses` [INFERRED]
- [[alpha_transformer.py]] - `contains` [EXTRACTED]
- [[从模型预测结果运行完整回测的便捷函数      Args         predictions num_samples, num_assets]] - `uses` [INFERRED]
- [[加载模型检查点到指定设备         健壮性保证：           - map_location 强制 CPU（防止 CUDA OOM 导致 500]] - `uses` [INFERRED]
- [[完整训练循环          Returns             {'train_loss' ..., 'val_loss' ...}]] - `uses` [INFERRED]
- [[对数据生成预测          Returns             (predictions, targets) 均为 numpy 数组]] - `uses` [INFERRED]
- [[执行推理，返回预测数组          Args             features  num_assets, history_len, n]] - `uses` [INFERRED]
- [[推理异常：携带错误码和上下文，不抛出 500]] - `uses` [INFERRED]
- [[训练器模块（AlphaTransformer） 支持：多阶段训练、早停、梯度裁剪、学习率调度、TensorBoard 日志]] - `uses` [INFERRED]

#graphify/code #graphify/INFERRED #community/AlphaTransformer_Core_Models