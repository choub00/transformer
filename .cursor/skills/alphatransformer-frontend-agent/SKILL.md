---
name: alphatransformer-frontend-agent
description: AlphaTransformer 前端重构 Agent 指令集。用于按照工业级标准重构 Vue 3 前端页面与交互逻辑，包含 Dashboard、Analysis、Trade 三个核心页面，并修复模拟交易真实化问题（参考东方财富杯规则）。
origin: AlphaTransformer
tags: [vue3, frontend, quantitative, trading, dashboard]
---

# AlphaTransformer 前端重构 Agent 完整指令

## 项目背景

AlphaTransformer 是一个量化股票 Alpha 预测系统，当前项目状态：
- **后端**：Python/FastAPI，位于 `D:/transformer/Stock Forecast/`
- **前端**：尚未创建，需要从零构建 Vue 3 前端
- **目标**：创建工业级 Dashboard，参考 Bloomberg Terminal 风格

---

## 核心参考文件

在执行任务前，Agent 必须阅读以下文件以获取完整上下文：

### 后端 API 文档
1. **`D:/transformer/Stock Forecast/api/server.py`** - FastAPI 主服务，API 路由定义
2. **`D:/transformer/Stock Forecast/api/dashboard.py`** - Dashboard API 端点（为 Vue 前端设计）
3. **`D:/transformer/Stock Forecast/api/trading.py`** - 交易 API 端点
4. **`D:/transformer/Stock Forecast/api/schemas.py`** - Pydantic 数据模型
5. **`D:/transformer/Stock Forecast/api/predictor.py`** - 模型推理引擎（需修复 500 错误）

### 项目规范
6. **`D:/transformer/.cursor/skills/frontend-patterns/SKILL.md`** - Vue/React 前端开发模式
7. **`D:/transformer/.cursor/skills/tdd-workflow/SKILL.md`** - 测试驱动开发工作流
8. **`D:/transformer/.cursor/skills/coding-standards/SKILL.md`** - 编码标准

---

## 功能模块规范

### 模块一：Dashboard 首页

```
路径: src/views/DashboardView.vue
```

**功能需求**：
1. **指标卡片**（全中文）
   - 夏普率 (Sharpe Ratio)
   - 年化收益率 (Annual Return)
   - 最大回撤 (Max Drawdown)
   - 胜率 (Win Rate)

2. **权益曲线图**
   - 调用 `GET /api/v1/dashboard/equity-curve`
   - ECharts 折线图
   - 显示策略收益 vs 基准收益

3. **特征重要性条形图**
   - 调用 `GET /api/v1/dashboard/feature-importance`
   - ECharts 水平条形图
   - Top 10 特征展示

**API 响应示例**：
```typescript
// GET /api/v1/dashboard/equity-curve
{
  "dates": ["2024-01-01", "2024-01-02", ...],
  "strategy_equity": [100000, 100500, ...],
  "benchmark_equity": [100000, 99900, ...]
}

// GET /api/v1/dashboard/feature-importance
{
  "features": [
    { "name": "momentum_5", "importance": 0.085 },
    { "name": "rsi", "importance": 0.072 },
    ...
  ]
}
```

---

### 模块二：Analysis 智能预测页

```
路径: src/views/AnalysisView.vue
```

**功能需求**：

1. **左侧股票排名列表**
   - 调用 `GET /api/v1/dashboard/predictions`
   - 16 只股票实时排名
   - AI 评分趋势 sparkline
   - 点击选择 `selectedTicker` 触发右侧图表刷新

2. **右侧 K 线+预测图表**
   - 调用 `GET /api/v1/forecast/{ticker}`
   - 实线：历史 K 线数据
   - 虚线：未来 5 日 Transformer 预测走势
   - `watch(selectedTicker)` 自动重新获取数据

**API 响应示例**：
```typescript
// GET /api/v1/forecast/AAPL
{
  "ticker": "AAPL",
  "dates": ["2024-01-01", "2024-01-02", ..., "2024-01-08"],
  "historical": {
    "open": [185.5, 186.2, ...],
    "high": [187.0, 188.1, ...],
    "low": [184.8, 185.5, ...],
    "close": [186.5, 187.2, ...],
    "volume": [50000000, 48000000, ...]
  },
  "prediction": {
    "dates": ["2024-01-09", ..., "2024-01-13"],
    "predicted_close": [188.5, 189.2, 190.1, 191.0, 192.5],
    "confidence_upper": [...],
    "confidence_lower": [...]
  }
}
```

---

### 模块三：Trade 模拟交易页

```
路径: src/views/TradeView.vue
```

**功能需求**：

1. **账户看板**
   - 总资产、盈亏、手续费支出
   - 调用 `GET /api/v1/account/balance`

2. **持仓列表**
   - 调用 `GET /api/v1/positions`
   - 显示每只持仓的浮动盈亏

3. **AI 交易助手抽屉**
   - 调用 `POST /api/v1/dashboard/ai-insights`
   - 选中股票的买入信心指数
   - El-Drawer 抽屉组件

4. **下单面板**
   - 买入/卖出切换
   - 数量输入 + 手续费预览
   - 调用 `POST /api/v1/trade/manual`
   - 手续费率：0.0015 (0.15%)

**API 响应示例**：
```typescript
// GET /api/v1/account/balance
{
  "total_assets": 125000.00,
  "cash": 45000.00,
  "market_value": 80000.00,
  "total_pnl": 25000.00,
  "total_pnl_pct": 25.0,
  "total_fees": 185.50,
  "positions": [
    {
      "ticker": "AAPL",
      "quantity": 100,
      "avg_price": 175.50,
      "current_price": 180.25,
      "market_value": 18025.00,
      "unrealized_pnl": 475.00,
      "unrealized_pnl_pct": 2.71
    }
  ]
}

// POST /api/v1/trade/manual
{
  "ticker": "AAPL",
  "direction": "buy",
  "quantity": 10,
  "price": 180.25
}
```

---

## 技术规范

### 1. 请求取消逻辑（防止数据覆盖）

```typescript
// src/api/index.ts
import axios, { AxiosInstance } from 'axios'

class APIClient {
  private client: AxiosInstance
  private abortControllers: Map<string, AbortController> = new Map()

  constructor() {
    this.client = axios.create({
      baseURL: 'http://localhost:8000/api/v1',
      timeout: 30000
    })
  }

  async get<T>(url: string, key?: string): Promise<T> {
    // 取消相同 key 的旧请求
    if (key && this.abortControllers.has(key)) {
      this.abortControllers.get(key)?.abort()
    }

    const controller = new AbortController()
    if (key) {
      this.abortControllers.set(key, controller)
    }

    try {
      const response = await this.client.get<T>(url, {
        signal: controller.signal
      })
      return response.data
    } finally {
      if (key) {
        this.abortControllers.delete(key)
      }
    }
  }
}

export const apiClient = new APIClient()
```

**使用场景**：用户快速切换股票时，确保旧请求被取消

```typescript
// 在 Analysis 页面中使用
const tickerStore = useTickerStore()

watch(() => tickerStore.selectedTicker, async (newTicker) => {
  const data = await apiClient.get<ForecastResponse>(
    `/forecast/${newTicker}`,
    `forecast-${newTicker}`  // 请求 key，用于取消
  )
  forecastData.value = data
})
```

### 2. 全局状态管理（Pinia）

```typescript
// src/stores/ticker.ts
import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useTickerStore = defineStore('ticker', () => {
  const selectedTicker = ref<string>('AAPL')
  const tickerHistory = ref<string[]>([])

  function selectTicker(ticker: string) {
    tickerHistory.value.push(ticker)
    if (tickerHistory.value.length > 10) {
      tickerHistory.value.shift()
    }
    selectedTicker.value = ticker
  }

  return { selectedTicker, tickerHistory, selectTicker }
})

// src/stores/account.ts
export const useAccountStore = defineStore('account', () => {
  const balance = ref<BalanceResponse | null>(null)
  const loading = ref(false)

  async function fetchBalance() {
    loading.value = true
    try {
      balance.value = await apiClient.get<BalanceResponse>('/account/balance')
    } finally {
      loading.value = false
    }
  }

  return { balance, loading, fetchBalance }
})
```

### 3. 暗黑主题（Bloomburg Terminal 风格）

```scss
// src/styles/BloombergTheme.scss

// 主色调
$bg-primary: #0a1628;
$bg-secondary: #132743;
$bg-card: #1a3050;
$bg-hover: #243654;

// 强调色
$accent-gold: #d4af37;     // 标题、重要数值
$accent-green: #00ff88;    // 上涨、正收益
$accent-red: #ff4444;      // 下跌、负收益
$accent-blue: #4a9eff;      // 交互元素

// 文字色
$text-primary: #e8e8e8;
$text-secondary: #8899aa;
$text-muted: #5a6a7a;

// Element Plus 暗黑覆盖
.el-theme-dark {
  --el-bg-color: #{$bg-primary};
  --el-bg-color-overlay: #{$bg-secondary};
  --el-card-bg: #{$bg-card};
  --el-text-color-primary: #{$text-primary};
  --el-text-color-regular: #{$text-secondary};
}
```

```typescript
// src/App.vue
import { ElConfigProvider } from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'

<el-config-provider :locale="zhCn">
  <router-view />
</el-config-provider>
```

### 4. 加载体验

```vue
<template>
  <div v-loading="loading" element-loading-text="数据加载中...">
    <!-- 内容 -->
  </div>
</template>
```

```typescript
// 全局错误通知
import { ElNotification } from 'element-plus'

apiClient.client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (axios.isCancel(error)) {
      return Promise.reject(error)
    }

    const message = error.response?.data?.error?.message ||
                    error.response?.data?.detail ||
                    '请求失败，请稍后重试'

    ElNotification({
      title: '错误',
      message,
      type: 'error',
      duration: 5000
    })

    return Promise.reject(error)
  }
)
```

---

## 模拟交易真实化（参考东方财富杯规则）

### 问题诊断

**问题 1: top_stocks 验证错误**
```json
{ "type": "string_type", "loc": ["body", "top_stocks", 0], "msg": "Input should be a valid string", "input": null }
```
原因：`rank_stocks` 返回的 predictions 中 ticker 可能为 null 或空值。

**问题 2: 随机买入价格无底线**
当前 `get_mock_price()` 生成的价格完全随机，基于 ticker hash 生成 50~549 之间的值，无法反映真实股价。

### 东方财富杯规则参考

| 规则项 | 说明 |
|--------|------|
| 交易品种 | 沪深A股（主板、中小板、创业板） |
| ST/*ST股 | 可交易但不计入成绩 |
| 新股 | 上市不足3个月可交易但不计入成绩 |
| 淘汰规则 | 净值 < 0.92（亏损 > 8%）失去资格 |
| 收益率算法 | Modified Dietz：\((1+r_1)(1+r_2)...(1+r_n)-1\) |

### 修复方案

#### 修复 1: `api/account_manager.py` - 引入真实价格映射

```python
# 添加真实股价参考表
_REALISTIC_PRICES = {
    # 沪深主板
    "600000": 8.52,   # 浦发银行
    "600036": 35.80,  # 招商银行
    "600519": 1680.0, # 贵州茅台
    "601318": 48.25,  # 中国平安
    "601888": 68.50,  # 中国中免
    "000001": 12.35,  # 平安银行
    "000002": 10.82,  # 万科A
    "000858": 180.50, # 五粮液
    "000876": 22.40,  # 新希望
    "002594": 245.60, # 比亚迪
    "300750": 265.80, # 宁德时代
    "300059": 18.92,  # 东方财富
    # AI 预测相关
    "AAPL": 178.50,
    "MSFT": 378.20,
    "GOOGL": 141.80,
    "NVDA": 495.20,
}

def get_realistic_price(ticker: str) -> float:
    """获取贴近真实的价格，带小范围波动"""
    base = _REALISTIC_PRICES.get(ticker.upper(), 50.0)
    import time
    day_factor = (int(time.time()) // 86400) % 100
    volatility = (day_factor - 50) / 2500.0  # -0.02 ~ +0.02
    return round(base * (1 + volatility), 2)

@staticmethod
def get_mock_price(ticker: str) -> float:
    return get_realistic_price(ticker)
```

#### 修复 2: `api/trading.py` - 过滤无效 ticker

```python
# 在 rank_stocks 返回处添加过滤
predictions = [
    p for p in predictions
    if p.get("ticker") and str(p.get("ticker")).strip()
]
```

#### 修复 3: `api/account_manager.py` - 添加淘汰规则

```python
@dataclass
class AccountStats:
    # ... 现有字段 ...
    eliminated: bool = False
    elimination_reason: Optional[str] = None

def check_elimination(self) -> bool:
    """检查是否触发淘汰规则（净值 < 0.92）"""
    with self._lock:
        total_assets = self._cash + sum(p.market_value for p in self._positions.values())
        net_value = total_assets / self._init_cash
        return net_value < 0.92
```

---

## 后端 500 错误修复

### 文件：`D:/transformer/Stock Forecast/api/predictor.py`

**问题**：模型推理可能因特征维度不匹配导致 500 错误

**修复方案**：

```python
def _run_model(self, features: np.ndarray) -> np.ndarray:
    """执行模型推理（强制 CPU）"""
    # 特征维度校验
    if features.shape[1] != self.expected_features:
        raise ModelShapeError(
            message=f"特征维度不匹配: 期望 {self.expected_features} 维, 获得 {features.shape[1]} 维",
            details={
                "expected_features": self.expected_features,
                "actual_features": features.shape[1]
            }
        )

    # 强制 CPU 推理
    device = torch.device('cpu')

    with torch.no_grad():
        input_tensor = torch.from_numpy(features.astype(np.float32)).to(device)

        if self.model_type == 'patchtst':
            output = self._run_patchtst(input_tensor)
        elif self.model_type == 'lightgbm':
            output = self._run_lightgbm(features)
        else:
            raise APIError(f"未知模型类型: {self.model_type}")

    return output.cpu().numpy()
```

---

## 文件结构清单

```
D:/transformer/frontend/
├── package.json                    # 依赖管理
├── vite.config.ts                 # Vite 配置
├── tsconfig.json                  # TypeScript 配置
├── index.html
└── src/
    ├── main.ts                    # 入口
    ├── App.vue                    # 根组件
    ├── router/
    │   └── index.ts               # 路由配置
    ├── stores/
    │   ├── index.ts               # Pinia 初始化
    │   ├── ticker.ts              # 选中股票状态
    │   ├── account.ts             # 账户状态
    │   └── dashboard.ts           # Dashboard 数据
    ├── api/
    │   ├── index.ts               # Axios 实例 + 取消逻辑
    │   ├── dashboard.ts           # Dashboard API
    │   ├── trading.ts             # 交易 API
    │   └── predictor.ts           # 预测 API
    ├── components/
    │   ├── charts/
    │   │   ├── EquityCurve.vue
    │   │   ├── FeatureImportance.vue
    │   │   ├── KLineChart.vue
    │   │   └── AIGauge.vue
    │   ├── dashboard/
    │   │   ├── MetricsCard.vue
    │   │   ├── StockRanking.vue
    │   │   └── MonthlyHeatmap.vue
    │   ├── trade/
    │   │   ├── AccountBoard.vue
    │   │   ├── PositionList.vue
    │   │   ├── TradePanel.vue
    │   │   └── AITradingDrawer.vue
    │   └── common/
    │       └── DarkContainer.vue
    ├── views/
    │   ├── DashboardView.vue
    │   ├── AnalysisView.vue
    │   └── TradeView.vue
    ├── styles/
    │   ├── variables.scss
    │   └── BloombergTheme.scss
    └── types/
        └── index.ts
```

---

## 执行检查清单

### 阶段一：项目初始化
- [ ] 创建 `frontend/` 目录结构
- [ ] 初始化 Vite + Vue 3 + TypeScript 项目
- [ ] 安装依赖：vue-router, pinia, element-plus, echarts, axios, @vueuse/core
- [ ] 配置 Element Plus 中文语言包
- [ ] 应用 Bloomberg 暗黑主题

### 阶段二：核心配置
- [ ] 实现 Axios 请求取消逻辑
- [ ] 创建 Pinia stores (ticker, account, dashboard)
- [ ] 配置 Vue Router（/, /analysis, /trade）
- [ ] 全局错误拦截和中文通知

### 阶段三：Dashboard 页面
- [ ] MetricsCard 组件（夏普率、年化收益、最大回撤、胜率）
- [ ] EquityCurve 组件（ECharts 权益曲线）
- [ ] FeatureImportance 组件（ECharts 条形图）
- [ ] DashboardView 整合

### 阶段四：Analysis 页面
- [ ] StockRanking 组件（16 只股票排名 + sparkline）
- [ ] KLineChart 组件（K 线 + 预测虚线）
- [ ] AnalysisView 左右布局
- [ ] watch(selectedTicker) 自动刷新

### 阶段五：Trade 页面
- [ ] AccountBoard 组件（账户看板）
- [ ] PositionList 组件（持仓列表）
- [ ] TradePanel 组件（下单面板 + 手续费计算）
- [ ] AITradingDrawer 组件（AI 交易助手）
- [ ] TradeView 整合

### 阶段六：后端修复
- [ ] 修复 predictor.py 特征对齐校验
- [ ] 确保 CPU 推理执行
- [ ] 增强错误信息（中文友好）

### 阶段七：后端修复
- [ ] 修复 `account_manager.py` 真实价格映射
- [ ] 添加东方财富杯淘汰规则（净值 < 0.92）
- [ ] 修复 `predictor.py` 特征对齐校验
- [ ] 修复 `predictor.py` 返回过滤无效 ticker
- [ ] 增强错误信息（中文友好）

### 阶段八：验证
- [ ] 启动后端服务 `uvicorn api.server:app`
- [ ] 启动前端 `pnpm dev`
- [ ] 验证 Dashboard 页面数据加载
- [ ] 验证股票切换图表刷新
- [ ] 验证交易下单功能（价格是否符合真实股价范围）
- [ ] 验证买入股票时显示真实股价（如贵州茅台 ~1680元）

---

## TypeScript 类型定义

```typescript
// src/types/index.ts

// Dashboard
interface DashboardMetrics {
  sharpe_ratio: number
  annual_return: number
  max_drawdown: number
  win_rate: number
}

interface EquityCurve {
  dates: string[]
  strategy_equity: number[]
  benchmark_equity: number[]
}

interface FeatureImportance {
  name: string
  importance: number
}

// Prediction
interface StockPrediction {
  ticker: string
  rank: number
  score: number
  trend: number[]
}

interface ForecastData {
  ticker: string
  dates: string[]
  historical: {
    open: number[]
    high: number[]
    low: number[]
    close: number[]
    volume: number[]
  }
  prediction: {
    dates: string[]
    predicted_close: number[]
    confidence_upper: number[]
    confidence_lower: number[]
  }
}

// Trading
interface Balance {
  total_assets: number
  cash: number
  market_value: number
  total_pnl: number
  total_pnl_pct: number
  total_fees: number
  positions: Position[]
}

interface Position {
  ticker: string
  quantity: number
  avg_price: number
  current_price: number
  market_value: number
  unrealized_pnl: number
  unrealized_pnl_pct: number
}

interface TradeRequest {
  ticker: string
  direction: 'buy' | 'sell'
  quantity: number
  price: number
}

interface AIInsight {
  ticker: string
  confidence: number
  recommendation: 'buy' | 'sell' | 'hold'
  reason: string
}
```

---

## API 端点速查表

| 功能 | 端点 | 方法 |
|------|------|------|
| 完整 Dashboard | `/api/v1/dashboard/full` | GET |
| 权益曲线 | `/api/v1/dashboard/equity-curve` | GET |
| 特征重要性 | `/api/v1/dashboard/feature-importance` | GET |
| 股票预测 | `/api/v1/dashboard/predictions` | GET |
| AI 投资建议 | `/api/v1/dashboard/ai-insights` | POST |
| 股票预测 K 线 | `/api/v1/forecast/{ticker}` | GET |
| 账户余额 | `/api/v1/account/balance` | GET |
| 当前持仓 | `/api/v1/positions` | GET |
| 手动下单 | `/api/v1/trade/manual` | POST |

---

## 成功标准

1. **功能完整性**：三个页面（Dashboard/Analysis/Trade）所有功能正常
2. **交互流畅**：股票切换时无数据覆盖，加载状态友好
3. **暗黑主题**：Bloomberg Terminal 风格，深蓝/金/绿配色
4. **错误处理**：后端 500 错误有中文提示，不假死
5. **类型安全**：TypeScript 严格模式，无 any 类型
6. **响应式**：移动端适配
7. **交易真实化**：买入价格贴近真实股价（如茅台 ~1680元），符合东方财富杯规则

---

## 参考文档

- [Vue 3 文档](https://vuejs.org/)
- [Element Plus 文档](https://element-plus.org/)
- [ECharts 文档](https://echarts.apache.org/)
- [Pinia 文档](https://pinia.vuejs.org/)
- [Vue Router 文档](https://router.vuejs.org/)
