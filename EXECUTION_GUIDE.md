# AlphaTransformer - Agent Execution Instructions

## Project Overview

AlphaTransformer is a quantitative stock alpha prediction system.
- **Backend**: Python/FastAPI at `D:/transformer/Stock Forecast/`
- **Frontend**: Vue 3 at `D:/transformer/frontend/` (to be created)
- **API Port**: 8000
- **Frontend Port**: 5173 (Vite default)

---

## Priority Task: Fix Trading Simulation (HIGHEST)

### Problems to Fix

1. **Random buy prices (50~549 RMB)** - Does not reflect real stock prices
2. **top_stocks validation error** - ticker returns null
3. **Missing elimination rules** - Should follow East Money competition rules

### Fix 1: Realistic Price Mapping

**File**: `D:/transformer/Stock Forecast/api/account_manager.py`

Find `get_mock_price` method around line 560, replace with:

```python
# Realistic price reference table
_REALISTIC_PRICES = {
    # A-shares (沪深A股)
    "600000": 8.52, "600036": 35.80, "600519": 1680.0, "601318": 48.25,
    "601888": 68.50, "000001": 12.35, "000002": 10.82, "000858": 180.50,
    "000876": 22.40, "002594": 245.60, "300750": 265.80, "300059": 18.92,
    "002415": 42.50, "600900": 22.80, "601166": 18.25, "600016": 4.85,
    "600028": 6.20, "601398": 5.45, "601939": 6.80, "600050": 5.20,
    "601012": 28.50, "002230": 45.20, "300033": 32.80, "300015": 38.50,
    "300122": 88.60, "300124": 125.30, "688981": 52.40, "688008": 78.20,
    # US stocks
    "AAPL": 178.50, "MSFT": 378.20, "GOOGL": 141.80, "AMZN": 185.60,
    "NVDA": 495.20, "META": 505.80, "TSLA": 248.50, "NFLX": 628.90,
    "AMD": 162.30, "INTC": 42.80, "ORCL": 128.50, "CRM": 295.40,
    "ADBE": 578.20, "PYPL": 62.50, "COIN": 185.60, "JPM": 198.40,
}

def _get_realistic_price(ticker: str) -> float:
    """Get realistic price with small daily fluctuation (±2%)"""
    import time
    base = _REALISTIC_PRICES.get(ticker.upper(), 50.0)
    day_factor = (int(time.time()) // 86400) % 100
    volatility = (day_factor - 50) / 2500.0
    return round(base * (1 + volatility), 2)

@staticmethod
def get_mock_price(ticker: str) -> float:
    return _get_realistic_price(ticker)
```

### Fix 2: Add Elimination Rules

In `AccountStats` dataclass, add:
```python
@dataclass
class AccountStats:
    # ... existing fields ...
    eliminated: bool = False
    elimination_reason: Optional[str] = None
```

In `get_stats` method, before returning:
```python
# Check elimination (net value < 0.92 = eliminated)
net_value = total_assets / self._init_cash if self._init_cash else 1.0
eliminated = net_value < 0.92
```

### Fix 3: Filter Invalid Tickers

**File**: `D:/transformer/Stock Forecast/api/predictor.py`

In `rank_stocks` method, before returning predictions:
```python
predictions = [
    p for p in predictions
    if p.get("ticker") and str(p.get("ticker")).strip()
]
```

### Fix 4: Feature Alignment Check

**File**: `D:/transformer/Stock Forecast/api/predictor.py`

In `_run_model` method:
```python
def _run_model(self, features: np.ndarray) -> np.ndarray:
    # Feature dimension validation
    expected = self.expected_features
    if features.shape[1] != expected:
        raise ModelShapeError(
            message=f"Feature dimension mismatch: expected {expected}, got {features.shape[1]}"
        )
    # ... remaining inference logic
```

---

## Task 2: Create Vue 3 Frontend

### 2.1 Initialize Project

```bash
# 进入项目根目录
cd D:/transformer

# 创建 Vite + Vue 3 + TypeScript 项目（使用 --yes 跳过交互式选择）
npm create vite@latest frontend -- --template vue-ts --yes

# 进入前端目录
cd frontend

# 安装依赖（统一使用 npm，与后端保持一致）
# 核心依赖：路由、状态管理、UI 组件库、图表、HTTP 客户端、工具函数
npm install vue-router@4 pinia element-plus echarts axios @vueuse/core

# 开发依赖：SASS 预处理器
npm install -D sass

# （可选）安装 Element Plus 图标（推荐）
npm install @element-plus/icons-vue
```

> **注意**：项目路径 `D:/transformer` 包含空格时，所有路径操作都需要正确引用。

### 2.2 File Structure

```bash
# 创建目录结构
mkdir -p frontend/src/{router,stores,api,views,styles,components,types,utils}

# 创建文件（按依赖顺序）
touch frontend/src/types/api.d.ts
touch frontend/src/api/index.ts
touch frontend/src/stores/{ticker,account}.ts
touch frontend/src/router/index.ts
touch frontend/src/styles/BloombergTheme.scss
touch frontend/src/views/{DashboardView,AnalysisView,TradeView}.vue
touch frontend/src/components/{MetricsCard,StockList,KLineChart}.vue
touch frontend/src/main.ts
touch frontend/src/App.vue
```

### 2.3 TypeScript 类型定义

```typescript
// src/types/api.d.ts

// 统一 API 错误格式
export interface ApiError {
  error: {
    code: string
    message: string
    details?: Record<string, unknown>
    request_id?: string
  }
}

// Dashboard 相关
export interface DashboardStatus {
  model_status: 'ready' | 'loading'
  risk_level: 'low' | 'medium' | 'high'
  last_update: string
}

export interface DashboardMetrics {
  annual_return: number
  sharpe_ratio: number
  max_drawdown: number
}

export interface StockPrediction {
  symbol: string
  score: number
  price: number
  signal: 'buy' | 'hold' | 'sell'
}

// 交易相关
export interface Position {
  ticker: string
  quantity: number
  entry_price: number
  current_price: number
  market_value: number
  unrealized_pnl: number
  unrealized_pnl_pct: number
  entry_date: string
  highest_price: number
  lowest_price: number
  ai_advice: string
  ai_score: number
  confidence: number
}

export interface AccountBalance {
  cash: number
  init_cash: number
  total_assets: number
  total_pnl: number
  total_return_pct: number
  available_cash: number
  total_fees: number
  total_trades: number
  winning_trades: number
  losing_trades: number
  win_rate: number
  daily_pnl: number
  daily_trades: number
  positions: Position[]
  updated_at: string
}

export interface OrderResult {
  order_id: string
  ticker: string
  side: 'buy' | 'sell'
  price: number
  quantity: number
  fee: number
  total_amount: number
  status: string
  timestamp: string
  position_after?: Position | null
  ai_score?: number
  realized_pnl: number
}

// K线数据
export interface OHLCItem {
  date: string
  open: number
  high: number
  low: number
  close: number
  volume: number
}

export interface ForecastPoint {
  date: string
  predicted_return_pct: number
  confidence: number
}

export interface ForecastResponse {
  ticker: string
  historical: OHLCItem[]
  forecast: ForecastPoint[]
  current_price: number
  ai_score: number
  direction: string
  updated_at: string
}
```

### 2.4 Axios 封装（带取消、错误处理、重试）

```typescript
// src/api/index.ts
import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosError } from 'axios'
import type { ApiError } from '../types/api'

// 创建实例
const api: AxiosInstance = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器：添加 AbortController
api.interceptors.request.use((config) => {
  const controller = new AbortController()
  config.signal = controller.signal
  ;(config as AxiosRequestConfig & { _controller: AbortController })._controller = controller
  return config
})

// 响应拦截器：统一错误处理
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError<ApiError>) => {
    if (axios.isCancel(error)) {
      console.warn('Request cancelled')
      return Promise.reject(error)
    }

    const apiError = error.response?.data?.error
    const message = apiError?.message ||
                     error.response?.data?.detail ||
                     error.message ||
                     'Request failed'

    // 格式化错误
    const formattedError = new Error(message)
    ;(formattedError as any).code = apiError?.code || 'UNKNOWN_ERROR'
    ;(formattedError as any).request_id = apiError?.request_id

    console.error(`[API Error] ${message}`, {
      code: (formattedError as any).code,
      url: error.config?.url,
    })

    return Promise.reject(formattedError)
  }
)

// 导出带类型的 API 实例
export default api

// 常用请求封装
export const apiDashboard = {
  full: () => api.get('/dashboard/full'),
  equityCurve: () => api.get('/dashboard/equity-curve'),
  featureImportance: () => api.get('/dashboard/feature-importance'),
  metrics: () => api.get('/dashboard/metrics'),
  predictions: () => api.get('/dashboard/predictions'),
  topBottom: () => api.get('/dashboard/top-bottom'),
}

export const apiTrading = {
  balance: () => api.get('/account/balance'),
  positions: () => api.get('/positions'),
  history: (limit = 50) => api.get('/trade/history', { params: { limit } }),
  manualOrder: (data: { ticker: string; price: number; quantity: number; side: 'buy' | 'sell' }) =>
    api.post('/trade/manual', data),
  closePosition: (ticker: string) => api.post('/trade/close-position', { ticker }),
  aiInsights: (data: any) => api.post('/dashboard/ai-insights', data),
}

export const apiForecast = {
  get: (ticker: string) => api.get(`/forecast/${encodeURIComponent(ticker)}`),
}
```

### 2.5 Pinia Store（带 TypeScript 类型）

```typescript
// src/stores/ticker.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useTickerStore = defineStore('ticker', () => {
  // 状态
  const selectedTicker = ref<string>('AAPL')
  const isLoading = ref(false)

  // 计算属性
  const tickerDisplay = computed(() => selectedTicker.value.toUpperCase())

  // Actions
  function selectTicker(ticker: string) {
    selectedTicker.value = ticker.toUpperCase().trim()
  }

  function setLoading(loading: boolean) {
    isLoading.value = loading
  }

  return {
    selectedTicker,
    isLoading,
    tickerDisplay,
    selectTicker,
    setLoading,
  }
})
```

```typescript
// src/stores/account.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiTrading } from '../api'
import type { AccountBalance, Position } from '../types/api'

export const useAccountStore = defineStore('account', () => {
  // 状态
  const balance = ref<AccountBalance | null>(null)
  const positions = ref<Position[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // 计算属性
  const totalValue = computed(() => balance.value?.total_assets ?? 0)
  const dailyPnL = computed(() => balance.value?.daily_pnl ?? 0)
  const winRate = computed(() => balance.value?.win_rate ?? 0)

  // Actions
  async function fetchBalance() {
    isLoading.value = true
    error.value = null
    try {
      const response = await apiTrading.balance()
      balance.value = response.data
      positions.value = response.data.positions || []
    } catch (e: any) {
      error.value = e.message
      console.error('Failed to fetch balance:', e)
    } finally {
      isLoading.value = false
    }
  }

  async function placeOrder(params: {
    ticker: string
    price: number
    quantity: number
    side: 'buy' | 'sell'
  }) {
    isLoading.value = true
    error.value = null
    try {
      const response = await apiTrading.manualOrder(params)
      await fetchBalance() // 刷新账户状态
      return response.data
    } catch (e: any) {
      error.value = e.message
      throw e
    } finally {
      isLoading.value = false
    }
  }

  return {
    balance,
    positions,
    isLoading,
    error,
    totalValue,
    dailyPnL,
    winRate,
    fetchBalance,
    placeOrder,
  }
})
```

### 2.6 Router（带导航守卫）

```typescript
// src/router/index.ts
import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import DashboardView from '../views/DashboardView.vue'
import AnalysisView from '../views/AnalysisView.vue'
import TradeView from '../views/TradeView.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Dashboard',
    component: DashboardView,
    meta: { title: '仪表盘' },
  },
  {
    path: '/analysis',
    name: 'Analysis',
    component: AnalysisView,
    meta: { title: '股票分析' },
  },
  {
    path: '/trade',
    name: 'Trade',
    component: TradeView,
    meta: { title: '模拟交易' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 导航守卫：更新页面标题
router.beforeEach((to, _from, next) => {
  document.title = `${to.meta.title || 'AlphaTransformer'} - AlphaTransformer`
  next()
})

export default router
```

### 2.7 Bloomberg Dark Theme（完整版）

```scss
// src/styles/BloombergTheme.scss

// === 颜色变量 ===
$bg-primary: #0a1628;
$bg-secondary: #132743;
$bg-card: #1a3050;
$bg-hover: #213a5c;

$text-primary: #e8e8e8;
$text-secondary: #a0aec0;
$text-muted: #718096;

$accent-gold: #d4af37;
$accent-green: #00ff88;
$accent-red: #ff4444;
$accent-blue: #4299e1;

// === 全局样式 ===
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  width: 100%;
  height: 100%;
  background: $bg-primary;
  color: $text-primary;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  font-size: 14px;
  line-height: 1.5;
}

// === Element Plus 主题覆盖 ===
:root {
  --el-bg-color: #{$bg-card};
  --el-bg-color-overlay: #{$bg-secondary};
  --el-text-color-primary: #{$text-primary};
  --el-text-color-regular: #{$text-secondary};
  --el-border-color: #{$bg-hover};
  --el-fill-color-blank: #{$bg-secondary};
}

// === 滚动条样式 ===
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: $bg-secondary;
}

::-webkit-scrollbar-thumb {
  background: $bg-hover;
  border-radius: 4px;

  &:hover {
    background: lighten($bg-hover, 10%);
  }
}

// === 工具类 ===
.text-gain {
  color: $accent-green;
}

.text-loss {
  color: $accent-red;
}

.text-gold {
  color: $accent-gold;
}

.bg-card {
  background: $bg-card;
  border-radius: 8px;
  padding: 16px;
}
```

### 2.8 App.vue（完整版 + 导航）

```vue
<!-- src/App.vue -->
<template>
  <el-config-provider :locale="zhCn">
    <div class="app-container">
      <!-- 顶部导航 -->
      <header class="app-header">
        <div class="logo">
          <span class="logo-icon">α</span>
          <span class="logo-text">AlphaTransformer</span>
        </div>
        <nav class="nav-links">
          <router-link to="/" class="nav-link" :class="{ active: $route.path === '/' }">
            <span>📊</span> 仪表盘
          </router-link>
          <router-link to="/analysis" class="nav-link" :class="{ active: $route.path === '/analysis' }">
            <span>📈</span> 股票分析
          </router-link>
          <router-link to="/trade" class="nav-link" :class="{ active: $route.path === '/trade' }">
            <span>💹</span> 模拟交易
          </router-link>
        </nav>
        <div class="header-status">
          <span class="status-dot" :class="{ online: isHealthy }"></span>
          <span class="status-text">{{ isHealthy ? '在线' : '离线' }}</span>
        </div>
      </header>

      <!-- 主内容区 -->
      <main class="app-main">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </el-config-provider>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { ElConfigProvider } from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import api from './api'

const isHealthy = ref(false)
let healthInterval: number | null = null

async function checkHealth() {
  try {
    const response = await api.get('/health', { timeout: 5000 })
    isHealthy.value = response.data?.status === 'healthy'
  } catch {
    isHealthy.value = false
  }
}

onMounted(() => {
  checkHealth()
  healthInterval = window.setInterval(checkHealth, 30000)
})

onUnmounted(() => {
  if (healthInterval) clearInterval(healthInterval)
})
</script>

<style lang="scss">
@import './styles/BloombergTheme.scss';

.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 60px;
  background: $bg-secondary;
  border-bottom: 1px solid $bg-hover;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;

  .logo-icon {
    font-size: 24px;
    color: $accent-gold;
    font-weight: bold;
  }

  .logo-text {
    font-size: 18px;
    font-weight: 600;
  }
}

.nav-links {
  display: flex;
  gap: 8px;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 6px;
  color: $text-secondary;
  text-decoration: none;
  transition: all 0.2s;

  &:hover {
    background: $bg-hover;
    color: $text-primary;
  }

  &.active {
    background: $bg-card;
    color: $accent-gold;
  }
}

.header-status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: $text-muted;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: $accent-red;

  &.online { background: $accent-green; }
}

.app-main {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
```

### 2.9 main.ts（入口文件）

```typescript
// src/main.ts
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(ElementPlus)

// 注册所有 Element Plus 图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.mount('#app')
```

---

## Task 3: Dashboard Page

**File**: `src/views/DashboardView.vue`

- Metrics cards: Sharpe Ratio, Annual Return, Max Drawdown, Win Rate
- Equity curve chart (ECharts line chart)
- Feature importance bar chart

API endpoints:
- `GET /api/v1/dashboard/equity-curve`
- `GET /api/v1/dashboard/feature-importance`
- `GET /api/v1/dashboard/metrics`

---

## Task 4: Analysis Page

**File**: `src/views/AnalysisView.vue`

- Left: 16 stock ranking list with AI scores and sparklines
- Right: K-line chart with Transformer predictions (dashed lines)

API endpoints:
- `GET /api/v1/dashboard/predictions`
- `GET /api/v1/forecast/{ticker}`

Key behavior: `watch(selectedTicker)` auto-refreshes chart

---

## Task 5: Trade Page

**File**: `src/views/TradeView.vue`

- Account board: total assets, P&L, fees
- Position list
- AI trading assistant drawer
- Order panel with 0.0015 fee calculation

API endpoints:
- `GET /api/v1/account/balance`
- `GET /api/v1/positions`
- `POST /api/v1/trade/manual`
- `POST /api/v1/dashboard/ai-insights`

---

## Verification Steps

1. **启动后端服务**（注意路径包含空格需要引号）:
   ```bash
   cd "D:/transformer/Stock Forecast"
   python -m uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload
   # 或使用快捷脚本：
   python run_api.py
   ```

2. **启动前端服务**:
   ```bash
   cd D:/transformer/frontend
   npm run dev
   # 或使用 pnpm：
   # pnpm dev
   ```

3. **验证后端 API**:
   ```bash
   curl http://localhost:8000/api/v1/health
   ```

4. **测试功能**:
   - 打开浏览器访问 `http://localhost:5173`
   - 测试买入股票 - 价格应反映真实值（如贵州茅台 ~1680 RMB）
   - 测试 `/api/v1/positions` - 不应有 ticker=null 错误
   - 验证三个页面正确加载
   - 切换股票应触发图表刷新

---

## Quick Commands Reference

```bash
# === 后端命令 ===
cd "D:/transformer/Stock Forecast"

# 启动 API 服务（开发模式）
python -m uvicorn api.server:app --reload --port 8000

# 训练模型
python run_lightgbm.py

# 运行回测
python run_backtest_raw.py

# === 前端命令 ===
cd D:/transformer/frontend

# 安装依赖
npm install

# 开发模式
npm run dev

# 构建生产版本
npm run build

# === 常用端口 ===
# 后端 API:  http://localhost:8000
# 前端:      http://localhost:5173
# API Docs:  http://localhost:8000/docs
```

---

## Success Criteria

1. Buy prices reflect real stock prices (e.g., 贵州茅台 ~1680 RMB)
2. No ticker=null validation errors
3. Frontend three pages work correctly
4. Stock switch triggers chart refresh

---

## Additional Configurations

### tsconfig.json（推荐配置）

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "module": "ESNext",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "preserve",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  },
  "include": ["src/**/*.ts", "src/**/*.d.ts", "src/**/*.tsx", "src/**/*.vue"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

### vite.config.ts（代理配置）

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        // 可选：重写路径
        // rewrite: (path) => path.replace(/^\/api/, '/api/v1')
      }
    }
  }
})
```

### 常用组件模板

#### MetricsCard.vue（指标卡片）

```vue
<!-- src/components/MetricsCard.vue -->
<template>
  <div class="metrics-card" :class="{ positive: value > 0, negative: value < 0 }">
    <div class="card-label">{{ label }}</div>
    <div class="card-value">
      <span class="value-number">{{ formattedValue }}</span>
      <span v-if="unit" class="value-unit">{{ unit }}</span>
    </div>
    <div v-if="change !== undefined" class="card-change">
      <span :class="change >= 0 ? 'text-gain' : 'text-loss'">
        {{ change >= 0 ? '↑' : '↓' }} {{ Math.abs(change).toFixed(2) }}%
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  label: string
  value: number
  unit?: string
  decimals?: number
  change?: number
}>()

const formattedValue = computed(() => {
  const dec = props.decimals ?? 2
  if (Math.abs(props.value) >= 1000) {
    return props.value.toLocaleString('zh-CN', {
      minimumFractionDigits: dec,
      maximumFractionDigits: dec
    })
  }
  return props.value.toFixed(dec)
})
</script>

<style lang="scss" scoped>
.metrics-card {
  background: $bg-card;
  border-radius: 8px;
  padding: 20px;

  .card-label {
    font-size: 12px;
    color: $text-muted;
    margin-bottom: 8px;
  }

  .card-value {
    font-size: 24px;
    font-weight: 600;

    .value-unit {
      font-size: 14px;
      color: $text-secondary;
    }
  }

  &.positive .card-value { color: $accent-green; }
  &.negative .card-value { color: $accent-red; }
}
</style>
```

---

## Troubleshooting

### 常见问题

1. **CORS 跨域错误**
   - 后端已配置 CORS 中间件（允许所有来源）
   - 检查浏览器控制台 Network 面板

2. **API 请求超时**
   - 默认超时 30 秒，可通过 `api` 实例调整
   - 检查后端服务是否正常运行

3. **前端无法连接后端**
   - 确认后端端口 8000 未被占用
   - Windows: `netstat -ano | findstr :8000`

4. **Element Plus 图标不显示**
   - 确保已注册图标: `npm install @element-plus/icons-vue`
   - 检查 main.ts 中的图标注册代码

5. **TypeScript 编译错误**
   - 运行 `npm install` 确认依赖安装完整
   - 删除 `node_modules` 和 `package-lock.json`，重新安装

