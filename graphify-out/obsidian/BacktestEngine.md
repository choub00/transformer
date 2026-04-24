---
source_file: "d:\transformer\evaluation\backtest.py"
type: "code"
community: "AlphaTransformer Core Models"
location: "L37"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/AlphaTransformer_Core_Models
---

# BacktestEngine

## Connections
- [[.__init__()_3]] - `method` [EXTRACTED]
- [[._compute_benchmark_return()]] - `method` [EXTRACTED]
- [[._compute_metrics()]] - `method` [EXTRACTED]
- [[._compute_portfolio_return()]] - `method` [EXTRACTED]
- [[._compute_target_positions()]] - `method` [EXTRACTED]
- [[._reset()]] - `method` [EXTRACTED]
- [[.get_equity_curves()]] - `method` [EXTRACTED]
- [[.get_trade_log()_1]] - `method` [EXTRACTED]
- [[.print_summary()]] - `method` [EXTRACTED]
- [[.run()]] - `method` [EXTRACTED]
- [[AlphaTransformerTrainer]] - `uses` [INFERRED]
- [[HuberLoss]] - `uses` [INFERRED]
- [[Mixed Huber Loss 结合 MSE 和 MAE 的优点      当 error = delta 时使用 MSE（平滑梯度）]] - `uses` [INFERRED]
- [[MixedHuberLoss]] - `uses` [INFERRED]
- [[backtest.py]] - `contains` [EXTRACTED]
- [[run_backtest_from_predictions()]] - `calls` [INFERRED]
- [[从模型预测结果运行完整回测的便捷函数      Args         predictions num_samples, num_assets]] - `uses` [INFERRED]
- [[回测引擎      核心逻辑（方案 C - 集合差集替换）：         1. 每日计算预测截面排名         2. 确定今日目标做多 Top2 和做]] - `rationale_for` [EXTRACTED]
- [[完整训练循环          Returns             {'train_loss' ..., 'val_loss' ...}]] - `uses` [INFERRED]
- [[对数据生成预测          Returns             (predictions, targets) 均为 numpy 数组]] - `uses` [INFERRED]
- [[训练器模块（AlphaTransformer） 支持：多阶段训练、早停、梯度裁剪、学习率调度、TensorBoard 日志]] - `uses` [INFERRED]

#graphify/code #graphify/EXTRACTED #community/AlphaTransformer_Core_Models