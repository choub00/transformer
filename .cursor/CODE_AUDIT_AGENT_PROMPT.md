# AlphaTransformer 代码审计 Agent 指令

> 你是一名高级量化研究员 + 系统架构师。请完整阅读 AlphaTransformer 全栈项目所有代码，
> 并按照以下顺序和维度进行系统性审计，不遗漏任何细节。

---

## 第一步：项目结构扫描

请先全局扫描整个项目，建立完整的文件清单和依赖关系图。

**执行命令：**
```bash
# 列出所有核心 Python 文件及其行数
find . -name "*.py" -not -path "*/node_modules/*" -not -path "*/__pycache__/*" -not -path "*/.venv/*" | xargs wc -l | sort -rn

# 列出所有前端文件
find ./frontend/src -name "*.vue" -o -name "*.ts" | xargs wc -l | sort -rn
```

**审计要点：**
1. 是否有文件循环依赖（A 导入 B，B 导入 A）？
2. 是否有孤岛代码（定义了但从未被调用）？
3. 是否存在同名函数/类在不同模块中冲突？
4. API 路由和服务是否完整对应（每个前端 API 调用都有后端实现）？

---

## 第二步：数据流链路审计（最重要）

请从数据源头到模型输出，完整追踪每一条数据流路径。

### 2.1 数据加载 → 预处理 → 模型 → 推理 → 回测

**读取文件：**
- `data/loader.py`
- `utils/normalization.py`
- `models/alpha_transformer.py`
- `models/alpha_transformer_2026.py`
- `trainer/trainer.py`
- `evaluation/backtest.py`
- `api/predictor.py`
- `api/dashboard.py`

**必须回答的问题：**

#### 问题 1：特征 lag-1 是否真正执行？

```python
# 在 data/loader.py 中找到所有 shift 操作，逐行检查：
log_returns = ...
target = ...
```

**正确做法**：所有因子必须 `shift(-1)` 或更早（只用过去）。
**常见错误**：`rolling().mean()` 在 `shift(-1)` 后会引入未来信息。

**检查方法**：在 `loader.py` 中搜索 `shift`、`rolling`、`mean`，确认没有组合错误。

#### 问题 2：标准化是否只用过去数据？

```python
# 在 utils/normalization.py 中确认：
# RollingNormalizer._compute_rolling_stats() 只用 x[t-window:t]
# 而不是 x[:t]（包含当前）或 x[t-window:t+1]（包含未来）
```

#### 问题 3：数据划分是否打乱？

```python
# 确认 DataLoader 中 shuffle=False
# 确认没有使用 train_test_split 的 random_state 参数
# 确认时序顺序：train → val → test（按时间顺序 70/15/15）
```

#### 问题 4：回测信号对齐是否正确？

```python
# 在 evaluation/backtest.py 中确认：
# 预测信号 Signal[t-1]  ×  真实收益 Return[t]
# 而不是 Signal[t] × Return[t]（这会导致泄露）

# 检查方法：找到 prev_preds 相关代码，确认：
# 1. predictions_df 的索引与 returns_df 的索引关系
# 2. 是否正确取前一天的预测值
```

#### 问题 5：多头注意力是否正确？

```python
# 在 models/alpha_transformer.py 中：
# TemporalBlock.forward() 残差连接必须：
#   x = residual + attn_out  # ← attn_out 必须参与残差！
# 常见错误：x = attn_out（无残差）→ 深层网络退化

# SparseCrossAssetAttention 中方向遮罩：
# mask = tril(ones)  # 下三角 = 只看自己和过去，不看未来
# attn_scores.masked_fill(mask.bool(), -inf)  # 上三角置负无穷
```

---

## 第三步：模型架构逻辑审计

### 3.1 alpha_transformer.py（V1/V2）

**逐模块检查：**

#### GatedResidualNetwork

```python
# 检查以下 5 点：
# 1. 激活函数：SiLU（推荐）还是 ReLU（差）？
# 2. 门控机制：sigmoid 门控是否在 (0,1) 范围？
# 3. 残差连接：x + GRN_out 还是直接 GRN_out？
# 4. 输出门控：gate_out 是否有 bias=False（否则输出不稳定）？
# 5. bias 初始化：fc_out.bias 是否置零（避免初始偏移）？
```

#### MultiHeadAttention

```python
# 检查以下 3 点：
# 1. Scale：d_head 的平方根是否正确？
# 2. 因果遮罩：masked_fill(..., -inf) 还是其他方式？
# 3. 维度变换：transpose(1,2) 后是否 .contiguous()（避免 view 错误）？
```

#### PatchTSTEncoder

```python
# 检查：
# 1. num_patches = history_len // patch_size（是否整除？）
# 2. causal_mask 长度是否匹配 num_patches？
# 3. CLS token 的 causal_mask 是否正确扩展？
# 4. Mean Pooling over patches 后是否接 norm？
```

#### AlphaTransformer.forward()

```python
# 逐行追踪数据流维度：
# [B, A, T, F]
#     ↓ feature_proj (F → d_model)
# [B, A, T, d_model]
#     ↓ view(B*A, T, -1)
# [B*A, T, d_model]
#     ↓ PatchTST
# [B*A, d_model]
#     ↓ view(B, A, -1)
# [B, A, d_model]
#     ↓ CrossAssetAttention
# [B, A, d_model]
#     ↓ output_grn
# [B, A, 1]
#     ↓ squeeze
# [B, A]

# 审计：每一步的 view/reshape/squeeze 是否安全？是否丢失维度信息？
```

### 3.2 alpha_transformer_2026.py（2026 SOTA）

**逐模块检查：**

#### AdaptiveLayerNorm

```python
# 检查：
# 1. norm(x) 的 elementwise_affine=False（只用学习的 gamma/beta）
# 2. scale_proj 和 bias_proj 是否从 stats 生成正确的 γ/β？
# 3. 残差是否正确：gamma * norm(x) + beta？
```

#### TemporalEncoder 多尺度

```python
# 检查：
# 1. low_patch_size = max(history_len // 3, 5)
#    high_patch_size = max(history_len // 12, 3)
#    这两个值是否合理（high 应该小于 low）？
# 2. 各自的 num_patches = history_len // patch_size
# 3. 两个分支分别通过 TemporalBlock 后，GRN 门控融合：
#    gate = sigmoid(W * [out_low; out_high])
#    fused = gate * low + (1-gate) * high
#    融合是否正确？
```

#### SparseCrossAssetAttention

```python
# 检查：
# 1. Top-K 稀疏化后是否重新做 softmax（否则注意力权重不归一）？
# 2. 方向遮罩是否正确（下三角 = 可以看过去）？
# 3. asset_role_emb 是否截取到实际资产数量 [A]？
```

#### SpatioTemporalBlock

```python
# 检查交替顺序：
# 1. Temporal Encoder 在前（提取时间模式）
# 2. Cross-Asset Attention 在后（建模资产相关性）
# 3. 每一步是否更新了正确的维度？
```

---

## 第四步：训练逻辑审计

### 4.1 损失函数

```python
# MixedHuberLoss
# 检查：
# 1. delta = 1.0 是否适合对数收益率尺度（通常 1.0 偏大）？
#    建议：对数收益率通常在 [-0.1, 0.1] 范围，delta=0.01 可能更合适
# 2. torch.clamp(abs_error, max=delta) 是否正确？
# 3. 返回值是否 .mean()（而非 .sum()）？
```

### 4.2 学习率调度

```python
# CosineAnnealingWarmRestarts
# 检查：
# 1. warmup_steps 是否正确（warmup_epochs × steps_per_epoch）？
# 2. Cosine 衰减公式是否正确：
#    eta_t = eta_min + 0.5 * (eta_max - eta_min) * (1 + cos(π * t/T))
# 3. min_lr 限制是否生效？
```

### 4.3 梯度裁剪

```python
# 检查：
# 1. clip_grad_norm_ 还是 clip_grad_value_？
#    clip_grad_norm_（按范数）更稳定，推荐
# 2. 裁剪阈值 1.0 是否合理（0.5~2.0 均可）？
```

### 4.4 早停

```python
# 检查：
# 1. delta 阈值是否合理（1e-4 对 loss 在 0.01 级别太严格）？
# 2. patience 是否与数据规模匹配（数据多则 patience 可设大）？
# 3. 最佳模型保存逻辑：是否只在改进时保存？
```

---

## 第五步：回测引擎审计

### 5.1 信号对齐

```python
# 在 evaluation/backtest.py 中找到：
# prev_preds 和 returns_df 的索引关系

# 核心原则：Signal[t-1] * Return[t]
# 验证方法：
#   1. 打印 predictions_df 和 returns_df 的前几个索引
#   2. 确认 predictions_df 的日期比 returns_df 的日期早 1 天
```

### 5.2 集合差集逻辑（Anti-Churn v3）

```python
# 检查：
long_to_sell  = current_long_set - set(target_long)   # 应该在哪只？
long_to_buy   = set(target_long) - current_long_set   # 应该买哪些？
short_to_cover = current_short_set - set(target_short)
short_to_sell  = set(target_short) - current_short_set

# 验证：假设昨日持仓 {A, B}，今日目标 {A, C}（A 仍在）
# long_to_sell = {A, B} - {A, C} = {B}  ← 正确（卖 B）
# long_to_buy  = {A, C} - {A, B} = {C}  ← 正确（买 C）
```

### 5.3 对数收益率累加

```python
# 检查：
# ✅ 正确：
equity[-1] * np.exp(daily_net_ret)  # 对数域加法，数值稳定

# ❌ 错误：
equity[-1] * (1 + daily_net_ret)     # 线性乘法，长期数值爆炸
```

### 5.4 交易成本扣除

```python
# 检查：
# ✅ 正确：在对数域做减法
daily_net_ret = daily_ret - num_trades * transaction_cost

# ❌ 错误：在复利域做乘法
daily_net_ret = daily_ret * (1 - num_trades * transaction_cost)

# 另外确认：单边还是双边收费？
# 东方财富杯 = 单边 0.15%（只在卖出时收）
```

### 5.5 最大回撤计算

```python
# 检查：
# cumulative = np.cumsum(log_returns)  # 对数域累积
# peak = np.maximum.accumulate(cumulative)  # 历史最高点
# drawdowns = cumulative - peak  # 当前点与历史最高的差
# max_drawdown = np.min(drawdowns)  # 最深的回撤

# 常见错误：
# peak = cumulative.exp().cummax() - cumulative.exp()  # 复杂但正确
# 但如果直接用 cumulative - cummax() 则是对数域回撤，需要检查这是否符合预期
```

---

## 第六步：API 服务审计

### 6.1 推理降级策略

```python
# 在 api/predictor.py 中：
# ModelRegistry 加载模型时，如果文件不存在或 CUDA OOM，
# 是否正确降级到演示数据（而不是崩溃）？

# 检查：
# 1. try-except 是否包裹 torch.load()？
# 2. 降级后 _fallback_mode = True ？
# 3. predict() 方法在降级模式下是否返回合理的演示数据？
```

### 6.2 全局异常处理

```python
# 在 api/server.py 中：
# 所有未捕获的异常是否被转换为 200 响应（而不是 500）？
# 检查：@app.exception_handler 是否覆盖了所有端点？

# 审计：
# 1. 遍历所有路由，手动检查 try-except 覆盖
# 2. 特别是 trading.py 中的 execute_order()
# 3. 特别是 dashboard.py 中的所有 API 调用
```

### 6.3 hashlib 导入问题

```python
# 在 api/account_manager.py 中：
# execute_order() 内使用了 hashlib.md5() 产生 order_id
# 检查：
# 1. 文件顶部是否有 import hashlib？
# 2. hashlib.md5() 是否在正确的位置调用？
# 3. order_id 的用途是什么（幂等性？幂等键？）？
```

### 6.4 线程安全

```python
# AccountManager 使用了 threading.Lock
# 检查：
# 1. 哪些操作被锁保护？execute_order？fetch_account？
# 2. 是否所有修改账户状态的操作都需要锁？
# 3. 是否有可能在锁外部读取到不一致的账户状态？
```

### 6.5 T+1 延迟单

```python
# 检查 trading.py 中：
# POST /trade/delayed 端点
# 1. 是否正确存储了 pending 状态？
# 2. 是否有定时任务在次日 9:30 执行？
# 3. 执行时是否再次检查资金/持仓是否足够？
```

---

## 第七步：前端代码审计

### 7.1 API 调用链路

```bash
# 检查前端 API 调用是否与后端端点一一对应：
# 读取 frontend/src/api/index.ts
# 对每个 apiXxx() 函数，找到对应的后端路由

# 常见问题：
# 1. 前端请求路径拼写错误（如 /trade/order vs /trade/orders）
# 2. 请求方法错误（GET vs POST）
# 3. 请求体格式不匹配（数组 vs 对象）
```

### 7.2 深色主题一致性

```bash
# 检查所有 Vue 文件中的颜色使用：
# 读取 frontend/src/style.css
grep -r "#[0-9A-Fa-f]\{6\}" frontend/src/views/
grep -r "#[0-9A-Fa-f]\{6\}" frontend/src/components/

# 检查原则：
# ✅ 正确：使用 CSS 变量 var(--text-secondary)
# ❌ 错误：硬编码 #484F58（对比度不足）
# ❌ 错误：硬编码 #8B949E（对比度不足）
# ✅ 正确：硬编码 accent 色 #00FFBD（语义色，可以接受）
```

### 7.3 ECharts 配置中的颜色

```bash
# ECharts tooltip/formatter 中的颜色是硬编码的 JS 字符串
# 这些可以接受（ECharts API 不支持 CSS 变量）
# 但应检查：
# 1. tooltip 中的颜色是否与整体主题一致？
# 2. chart backgroundColor 是否为 #0d1117（与 --bg-primary 一致）？
```

### 7.4 交易面板审计（TradePanel.vue）

```bash
# 检查：
# 1. 主 CTA 按钮对比度：文字 vs 背景是否符合 WCAG AA（4.5:1）？
#    买入：#F0F6FC on #0D1117 = ✓ 极高对比度
#    卖出：#3D1800 on #FF9500 = ✓ 高对比度
# 2. 步进器按钮：宽高是否 ≥44px？
# 3. 快捷胶囊：是否有 hover/active 状态反馈？
# 4. 手续费 tooltip：hover 显示是否正常？
# 5. "满仓"文案：是否弱化为"按可买上限"（降低误触风险）？
```

### 7.5 三层面板层级

```bash
# 检查 TradeView.vue：
# 1. 是否有 .tier-label 标签（AI 决策 / 仓位 / 执行）？
# 2. 是否有 .tier-divider 分割线？
# 3. 自动交易开关是否与下单区有足够间距（section-separator）？
```

### 7.6 Pinia 状态管理

```bash
# 检查 frontend/src/stores/
# 账户数据更新后，UI 是否同步刷新？
# 检查 watch/debounce：
# 1. fetchAccount() 后是否立即更新 store？
# 2. 连续快速下单时是否有竞态条件？
```

---

## 第八步：数值稳定性审计

### 8.1 梯度检查

```python
# 在训练循环中打印梯度范数：
for name, param in model.named_parameters():
    if param.grad is not None:
        grad_norm = param.grad.norm().item()
        if grad_norm > 10:
            print(f"⚠️  {name}: grad_norm = {grad_norm:.2f}")

# 检查：哪些层的梯度容易爆炸？
# 常见问题：最后一层 output_grn 的梯度过大
```

### 8.2 损失值尺度

```python
# 打印训练开始和结束时的 loss 数量级：
print(f"Epoch {epoch} train_loss: {train_loss:.6f}")
print(f"Epoch {epoch} val_loss:   {val_loss:.6f}")

# 检查：
# 1. loss 是否在合理范围（如 0.001 ~ 1.0）？
# 2. 如果 loss > 10，可能是数据尺度问题
# 3. 如果 loss 在训练过程中 NaN，检查梯度或激活函数
```

### 8.3 模型输出尺度

```python
# 打印模型输出的分布：
preds = trainer.predict(test_loader)
print(f"Preds: min={preds.min():.4f}, max={preds.max():.4f}, mean={preds.mean():.4f}")
print(f"Targets: min={targets.min():.4f}, max={targets.max():.4f}, mean={targets.mean():.4f}")

# 对数收益率通常在 [-0.1, 0.1] 范围
# 如果预测值在 [1.0, 10.0]，说明输出层激活函数错误（应该是线性）
```

---

## 第九步：边界条件与异常处理

### 9.1 模型推理边界

```python
# 检查 api/predictor.py 中：
# 1. 如果 features 为空数组，模型是否会崩溃？
# 2. 如果 batch_size=1，模型的 squeeze 操作是否安全？
# 3. 如果 num_assets 与训练时不同，asset_emb 是否越界？
```

### 9.2 交易边界

```python
# 在 account_manager.py 中检查：
# 1. quantity = 0 时是否被拦截？
# 2. price = 0 或负数时是否被拦截？
# 3. 资金不足时是否返回明确的错误信息（而不是静默失败）？
# 4. 持仓不足时卖出是否被拦截？
# 5. 淘汰线 0.92 是否被严格检查（在每次下单前）？
```

### 9.3 前端边界

```vue
<!-- 检查 Vue 模板中的边界处理 -->
<!-- 例如：positions.length === 0 时是否显示空状态？ -->
<div v-if="account.positions?.length > 0">
  <!-- 表格内容 -->
</div>
<div v-else class="empty-positions">
  <!-- 空状态 -->
</div>

<!-- 检查： -->
<!-- 1. 所有 v-if/v-show 是否正确（避免空指针） -->
<!-- 2. 所有 ?. 可选链是否覆盖了所有可能的空值 -->
<!-- 3. 数字格式化：NaN、Infinity 是否被处理？ -->
```

---

## 第十步：输出审计报告

完成所有审计后，请输出以下格式的报告：

```markdown
# AlphaTransformer 代码审计报告

## 审计摘要
- 审计时间：
- 审计范围：
- 发现问题数：X 个（严重 Y 个 / 中等 Z 个 / 轻微 W 个）
- 建议优先修复：

## 🔴 严重问题（立即修复）

### 问题 X.1：[标题]
**位置**：`path/to/file.py:行号`
**描述**：
```python
# 有问题的代码
```
**影响**：会导致 [具体后果]
**建议修复**：
```python
# 修复后
```

## 🟡 中等问题（尽快修复）

...

## 🟢 轻微问题（可选修复）

...

## ✅ 已验证正确的部分

1. **[模块名称]**：确认 [验证方法和结果]
2. ...

## 📋 检查清单完成情况

- [x] 数据流链路追踪（特征 lag-1）
- [x] 标准化 Anti-Leakage
- [x] 时序数据划分
- [x] 回测信号对齐
- [x] 模型维度追踪
- [x] 注意力残差连接
- [x] 损失函数正确性
- [x] 梯度裁剪配置
- [x] API 降级策略
- [x] 线程安全
- [x] 前端颜色一致性
- [x] 交易边界条件
- [x] 数值稳定性
```

---

## 特别提示

1. **不要猜测**：所有结论必须有代码依据，引用具体的文件路径和行号
2. **追踪完整链路**：从数据到输出，不遗漏任何中间步骤
3. **优先级排序**：严重问题（数据泄露、崩溃、错误交易）优先于代码风格
4. **提供修复代码**：每个问题附上具体的修复建议，不要只描述问题
5. **验证修复**：如果可能，提供验证修复后是否正确的方法
