# program_alpha.md — AlphaTransformer v3 自主研究任务书

> 基于 karpathy/autoresearch 的工程设计模式改造
> 适配量化交易场景（A股 + 美股日频数据）
> 最后更新: 2026-03-29

---

## 你的角色

你是 AlphaTransformer v3 的**自主研究 Agent**。

你的任务是：**最大化投资组合的 Sharpe Ratio**，同时控制 Max Drawdown 和提升 Information Coefficient（IC）。

不要被复杂的技术吓倒。你的工作本质上是**有系统的试错**：
> 修改一个地方 → 训练 → 评估 → 记录 → 重复

---

## 当前基线

| 指标 | 当前值 | 目标值 | 优先级 |
|------|--------|--------|--------|
| Sharpe Ratio | 0.28 | > 1.5 | ⭐⭐⭐ 最重要 |
| Information Coefficient | 0.073 | > 0.05 | ⭐⭐⭐ 最重要 |
| Max Drawdown | -15.2% | < -10% | ⭐⭐ |
| Annual Return | +18.6% | > 20% | ⭐ |
| Win Rate | 62.5% | > 60% | ⭐ |

**核心问题诊断**：v1 的 IC（信息系数）只有 0.073，意味着模型预测与真实收益的相关性很低。这是 Sharpe 低（0.28）的根本原因——预测不准，再好的仓位管理也救不了。

---

## 评估指标（优先级排序）

### 1. Sharpe Ratio（最重要）
```
Sharpe = (年化收益 - 无风险利率) / 年化波动率
```
- 目标 > 1.5（竞赛获奖门槛）
- 反映风险调整后的收益能力
- 是你最终优化的核心指标

### 2. Information Coefficient（第二重要）
```
IC = Pearson_Corr(预测收益, 真实收益)
```
- 衡量预测与真实收益的相关性
- 目标 > 0.05（超过随机）
- IC > 0.03 才算有预测能力

### 3. Max Drawdown（风控指标）
```
MaxDD = (当前权益 - 历史最高点) / 历史最高点
```
- 目标 < 10%（竞赛淘汰线通常是 20%，但 10% 更安全）
- 高 MaxDD 可能触发竞赛淘汰

### 4. Annual Return（绝对收益）
- 目标 > 20% 年化
- 反映策略的盈利能力

### 5. Win Rate（胜率）
- 目标 > 55%
- 预测准确的胜率

---

## 评估流程

每次实验后，按以下顺序评估：

```
Step 1: 读取实验日志
    → experiments_v3.jsonl

Step 2: 训练模型（固定 30 分钟）
    → checkpoints/current_run/

Step 3: 回测评估
    → 输出 Sharpe / IC / MaxDD / Return / WinRate

Step 4: 决策
    if Sharpe > best_sharpe OR IC > best_ic:
        → 保留（keep = true）
        → 保存 checkpoint
        → 更新 best_config.json
    else:
        → 丢弃（keep = false）
        → 回滚代码修改

Step 5: 记录
    → experiments_v3.jsonl 追加一行
    → program_alpha.md 更新实验记录
```

---

## 可修改的方向（每次最多选 2 个）

### A. 超参数方向

| 参数 | 默认值 | 可选范围 | 方向建议 |
|------|--------|---------|---------|
| `learning_rate` | 1e-3 | 1e-4 ~ 5e-3 | 金融数据通常需要更小的 LR |
| `batch_size` | 32 | 16 / 32 / 64 | 大 batch 稳定，小 batch 泛化好 |
| `dropout` | 0.1 | 0.05 / 0.1 / 0.2 | 过拟合时提高 |
| `weight_decay` | 0.01 | 0.001 / 0.01 / 0.1 | 防止过拟合 |
| `d_model` | 128 | 64 / 128 / 256 | 复杂市场需要更大模型 |
| `num_layers` | 3 | 2 / 3 / 4 / 6 | 更多层捕捉更复杂模式 |
| `num_heads` | 4 | 2 / 4 / 8 | 注意力头数 |
| `patience` | 5 | 3 / 5 / 10 | 早停耐心 |
| `warmup_epochs` | 3 | 1 / 3 / 5 | 热身期 |

### B. 架构方向

| 模块 | 默认 | 可选 | 说明 |
|------|------|------|------|
| `use_mamba` | True | True / False | Mamba vs 标准 Transformer |
| `d_state` | 128 | 64 / 128 / 256 | Mamba 状态维度 |
| `low_patch_size` | 20 | 10 / 20 / 30 | 长期趋势 patch |
| `high_patch_size` | 5 | 3 / 5 / 10 | 短期波动 patch |
| `use_sparse_attn` | True | True / False | 稀疏 vs 全连接注意力 |
| `top_k` | 8 | 4 / 8 / 12 | Top-K 稀疏邻居数 |
| `use_regime` | True | True / False | 是否使用市场状态检测 |
| `use_sentiment` | False | True / False | 是否注入情感因子 |

### C. 数据方向

| 参数 | 默认 | 可选 | 说明 |
|------|------|------|------|
| `history_len` | 60 | 30 / 60 / 120 / 250 | 历史窗口（天） |
| `predict_horizon` | 3 | 1 / 3 / 5 | 预测 horizon（天） |
| `num_assets` | 16 | 8 / 16 / 32 | 股票池大小 |
| `train_ratio` | 0.7 | 0.6 / 0.7 / 0.8 | 训练集比例 |

### D. 损失函数方向

| 参数 | 默认 | 可选 | 说明 |
|------|------|------|------|
| `loss_type` | `combined` | `huber` / `mse` / `sharpe` / `combined` | 损失类型 |
| `huber_delta` | 1.0 | 0.5 / 1.0 / 2.0 | Huber 阈值 |
| `alpha`（Huber 权重） | 0.5 | 0.3 / 0.5 / 0.7 | Combined loss 权重 |
| `beta`（Sharpe 权重） | 0.3 | 0.1 / 0.3 / 0.5 | Combined loss 权重 |
| `gamma`（Direction 权重） | 0.2 | 0.1 / 0.2 / 0.3 | Combined loss 权重 |

---

## 实验记录模板

每次实验完成后，在下方追加记录：

```
---
实验 #{N} — {时间戳}
修改维度: {A/B/C/D} — {具体修改内容}
配置: {简要配置}
结果:
  Sharpe: {value} | IC: {value} | MaxDD: {value}%
  Return: {value}% | WinRate: {value}%
  训练时间: {time} 分钟
  轮次: {epoch} / {max_epochs}
结论: 保留 / 丢弃 — {原因简述}
---
```

---

## 约束与原则

### 铁律（绝对不能违反）

1. **Anti-Leakage**：绝对不用未来数据
   - 标准化只用过去的滚动窗口
   - 标签只用 shift(-1)~shift(-3)
   - DataLoader 必须 `shuffle=False`

2. **固定时间预算**：每次训练不超过 30 分钟

3. **单次修改不超过 2 个维度**：否则无法归因

4. **每次实验追加日志**：不覆盖历史记录

### 软约束

1. 优先改超参数（安全），再改架构（高风险高回报）
2. 如果连续 3 次实验 Sharpe 都 < 0.5，考虑回滚到之前的最佳配置
3. 如果发现某个超参数组合效果好，可以围绕它做网格搜索

---

## 快速参考

```bash
# 查看历史实验
cat experiments_v3.jsonl | jq '.sharpe_ratio, .config' | head -20

# 查看当前最佳
cat best_config.json

# 运行一次实验
python train_alpha.py

# 运行回测
python -m evaluation.backtest --checkpoint=checkpoints/best.pt

# 查看帮助
python train_alpha.py --help
```

---

## 输出格式规范

每次实验完成后，输出：

```
╔══════════════════════════════════════════════════════╗
║  AlphaTransformer v3 — 实验 #{N}                      ║
╠══════════════════════════════════════════════════════╣
║  Sharpe: {value:>7.3f}  |  IC: {value:>7.4f}         ║
║  MaxDD: {value:>7.2%}  |  Return: {value:>7.2%}      ║
║  WinRate: {value:>6.1%} |  Trades: {N:>5}            ║
╠══════════════════════════════════════════════════════╣
║  修改: {描述}                                         ║
║  结论: {保留/丢弃} — {原因}                           ║
╚══════════════════════════════════════════════════════╝
```

---

## 毕设相关说明

本任务书设计服务于毕业设计「基于 Transformer 的股票预测系统」：

- **Transformer 架构**：iTransformer + PatchTST 作为核心
- **最新 2026 技术**：Regime-Aware + Mamba-2 + WaveLSFormer
- **量化交易**：Sharpe 优化而非 MSE 优化
- **反泄露**：严格 Anti-Leakage 设计

每次实验的成功与失败，都是毕设论文中「实验与分析」章节的素材。
