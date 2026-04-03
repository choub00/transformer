# AlphaTransformer Agent 执行包

## 快速开始

### 1. 项目概览（必读）

AlphaTransformer 是一个**量化股票 alpha 预测系统**，核心功能：

| 模块 | 技术栈 | 位置 |
|------|--------|------|
| 后端 API | Python + FastAPI | `D:/transformer/Stock Forecast/` |
| 模型推理 | PyTorch + LightGBM | `api/predictor.py` |
| 账户管理 | 单例模式 | `api/account_manager.py` |
| 前端 | Vue 3 + TypeScript | `D:/transformer/frontend/` (待创建) |

**关键 API 端点**:
- `GET /api/v1/health` — 健康检查
- `POST /api/v1/predict` — 股票预测
- `GET /api/v1/account/balance` — 账户余额
- `POST /api/v1/trade/manual` — 手动下单

**已知问题（需修复）**:
1. `get_mock_price()` 生成不真实价格 (50~549 RMB)
2. 预测结果可能返回 null ticker
3. 前端尚未创建

---

### 2. 立即执行命令

#### 步骤 1: 创建前端项目

```bash
# 进入项目目录
cd D:/transformer

# 创建 Vite + Vue 3 + TypeScript 项目
npm create vite@latest frontend -- --template vue-ts --yes

# 进入前端目录
cd frontend

# 安装依赖
npm install vue-router@4 pinia element-plus echarts axios @vueuse/core @element-plus/icons-vue
npm install -D sass
```

#### 步骤 2: 创建目录结构

```bash
# 在 frontend/src/ 下创建
mkdir -p router stores api views styles components types utils

# 创建类型定义文件
cat > src/types/api.d.ts << 'EOF'
export interface ApiError {
  error: { code: string; message: string; details?: any; request_id?: string }
}

export interface DashboardMetrics { annual_return: number; sharpe_ratio: number; max_drawdown: number }
export interface Position { ticker: string; quantity: number; entry_price: number; current_price: number; market_value: number; unrealized_pnl: number; unrealized_pnl_pct: number; ai_advice: string; ai_score: number; }
export interface AccountBalance { cash: number; total_assets: number; total_pnl: number; total_fees: number; total_trades: number; positions: Position[]; }
export interface StockPrediction { symbol: string; score: number; price: number; signal: string; }
EOF
```

#### 步骤 3: 创建 API 层

```bash
cat > src/api/index.ts << 'EOF'
import axios, { type AxiosInstance, type AxiosError } from 'axios'
import type { ApiError } from '../types/api'

export const api: AxiosInstance = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  timeout: 30000,
})

api.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiError>) => {
    if (!axios.isCancel(error)) {
      const msg = error.response?.data?.error?.message || error.response?.data?.detail || error.message
      console.error('[API Error]', msg)
    }
    return Promise.reject(error)
  }
)

export const apiDashboard = {
  full: () => api.get('/dashboard/full'),
  metrics: () => api.get('/dashboard/metrics'),
  predictions: () => api.get('/dashboard/predictions'),
  equityCurve: () => api.get('/dashboard/equity-curve'),
  featureImportance: () => api.get('/dashboard/feature-importance'),
}

export const apiTrading = {
  balance: () => api.get('/account/balance'),
  positions: () => api.get('/positions'),
  history: (limit = 50) => api.get('/trade/history', { params: { limit } }),
  manualOrder: (data: any) => api.post('/trade/manual', data),
}
EOF
```

#### 步骤 4: 创建 Pinia Store

```bash
cat > src/stores/ticker.ts << 'EOF'
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useTickerStore = defineStore('ticker', () => {
  const selectedTicker = ref<string>('AAPL')
  function selectTicker(ticker: string) {
    selectedTicker.value = ticker.toUpperCase().trim()
  }
  return { selectedTicker, selectTicker }
})
EOF

cat > src/stores/account.ts << 'EOF'
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { apiTrading } from '../api'

export const useAccountStore = defineStore('account', () => {
  const balance = ref<any>(null)
  const positions = ref<any[]>([])
  const isLoading = ref(false)

  async function fetchBalance() {
    isLoading.value = true
    try {
      const res = await apiTrading.balance()
      balance.value = res.data
      positions.value = res.data.positions || []
    } finally {
      isLoading.value = false
    }
  }

  return { balance, positions, isLoading, fetchBalance }
})
EOF
```

#### 步骤 5: 创建 Router

```bash
cat > src/router/index.ts << 'EOF'
import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from '../views/DashboardView.vue'
import AnalysisView from '../views/AnalysisView.vue'
import TradeView from '../views/TradeView.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: DashboardView, meta: { title: '仪表盘' } },
    { path: '/analysis', component: AnalysisView, meta: { title: '股票分析' } },
    { path: '/trade', component: TradeView, meta: { title: '模拟交易' } },
  ],
})
EOF
```

#### 步骤 6: 创建样式

```bash
cat > src/styles/BloombergTheme.scss << 'EOF'
$bg-primary: #0a1628;
$bg-secondary: #132743;
$bg-card: #1a3050;
$accent-gold: #d4af37;
$accent-green: #00ff88;
$accent-red: #ff4444;

body { background: $bg-primary; color: #e8e8e8; font-family: 'Inter', sans-serif; }
.text-gain { color: $accent-green; }
.text-loss { color: $accent-red; }
.text-gold { color: $accent-gold; }
EOF
```

#### 步骤 7: 创建 main.ts

```bash
cat > src/main.ts << 'EOF'
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

for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.mount('#app')
EOF
```

#### 步骤 8: 创建 App.vue

```bash
cat > src/App.vue << 'EOF'
<template>
  <el-config-provider :locale="zhCn">
    <div class="app-container">
      <header class="app-header">
        <div class="logo"><span class="logo-icon">α</span> AlphaTransformer</div>
        <nav class="nav-links">
          <router-link to="/" class="nav-link">📊 仪表盘</router-link>
          <router-link to="/analysis" class="nav-link">📈 股票分析</router-link>
          <router-link to="/trade" class="nav-link">💹 模拟交易</router-link>
        </nav>
      </header>
      <main class="app-main">
        <router-view />
      </main>
    </div>
  </el-config-provider>
</template>

<script setup lang="ts">
import { ElConfigProvider } from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
</script>

<style lang="scss">
@import './styles/BloombergTheme.scss';
.app-container { display: flex; flex-direction: column; min-height: 100vh; }
.app-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 24px; height: 60px; background: $bg-secondary;
}
.logo { font-size: 18px; font-weight: 600; .logo-icon { color: $accent-gold; font-size: 24px; } }
.nav-links { display: flex; gap: 8px; }
.nav-link {
  padding: 8px 16px; border-radius: 6px; color: #a0aec0; text-decoration: none;
  &:hover, &.router-link-active { background: $bg-card; color: $accent-gold; }
}
.app-main { flex: 1; padding: 24px; }
</style>
EOF
```

#### 步骤 9: 创建 View 页面（基础版）

```bash
# DashboardView
cat > src/views/DashboardView.vue << 'EOF'
<template>
  <div class="dashboard">
    <h1>📊 仪表盘</h1>
    <div class="metrics-grid">
      <div class="metric-card">
        <div class="label">年化收益率</div>
        <div class="value text-gain">{{ metrics.annual_return?.toFixed(2) || 0 }}%</div>
      </div>
      <div class="metric-card">
        <div class="label">夏普比率</div>
        <div class="value">{{ metrics.sharpe_ratio?.toFixed(3) || 0 }}</div>
      </div>
      <div class="metric-card">
        <div class="label">最大回撤</div>
        <div class="value text-loss">{{ metrics.max_drawdown?.toFixed(2) || 0 }}%</div>
      </div>
    </div>
    <div class="predictions-section">
      <h2>📈 AI 股票推荐</h2>
      <el-table :data="predictions" stripe>
        <el-table-column prop="symbol" label="股票代码" />
        <el-table-column prop="score" label="AI 分数">
          <template #default="{ row }">
            <span :class="row.score > 0 ? 'text-gain' : 'text-loss'">{{ row.score.toFixed(4) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="signal" label="信号" />
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { apiDashboard } from '../api'

const metrics = ref<any>({})
const predictions = ref<any[]>([])

onMounted(async () => {
  try {
    const [m, p] = await Promise.all([apiDashboard.metrics(), apiDashboard.predictions()])
    metrics.value = m.data
    predictions.value = p.data
  } catch (e) {
    console.error('Failed to load dashboard:', e)
  }
})
</script>

<style lang="scss" scoped>
@import '../styles/BloombergTheme.scss';
.dashboard { max-width: 1200px; margin: 0 auto; }
h1 { margin-bottom: 24px; }
.metrics-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 32px; }
.metric-card {
  background: $bg-card; border-radius: 8px; padding: 20px;
  .label { font-size: 12px; color: #718096; margin-bottom: 8px; }
  .value { font-size: 24px; font-weight: 600; }
}
.predictions-section h2 { margin-bottom: 16px; }
</style>
EOF

# AnalysisView
cat > src/views/AnalysisView.vue << 'EOF'
<template>
  <div class="analysis">
    <h1>📈 股票分析</h1>
    <div class="analysis-content">
      <div class="stock-list">
        <h3>股票列表</h3>
        <div v-for="stock in predictions" :key="stock.symbol"
             class="stock-item" :class="{ active: selectedTicker === stock.symbol }"
             @click="selectStock(stock.symbol)">
          <span class="symbol">{{ stock.symbol }}</span>
          <span :class="stock.score > 0 ? 'text-gain' : 'text-loss'">{{ stock.score.toFixed(4) }}</span>
        </div>
      </div>
      <div class="chart-area">
        <h3>{{ selectedTicker }} K线图</h3>
        <div v-if="loading" class="loading">加载中...</div>
        <div v-else class="placeholder-chart">[ECharts K线图区域]</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { apiDashboard } from '../api'
import { useTickerStore } from '../stores/ticker'

const tickerStore = useTickerStore()
const selectedTicker = ref(tickerStore.selectedTicker)
const predictions = ref<any[]>([])
const loading = ref(false)

function selectStock(symbol: string) {
  selectedTicker.value = symbol
  tickerStore.selectTicker(symbol)
}

onMounted(async () => {
  try {
    const res = await apiDashboard.predictions()
    predictions.value = res.data
  } catch (e) {
    console.error('Failed to load predictions:', e)
  }
})
</script>

<style lang="scss" scoped>
@import '../styles/BloombergTheme.scss';
.analysis-content { display: grid; grid-template-columns: 300px 1fr; gap: 24px; margin-top: 24px; }
.stock-list { background: $bg-card; border-radius: 8px; padding: 16px; }
.stock-item {
  display: flex; justify-content: space-between; padding: 12px;
  cursor: pointer; border-radius: 4px; margin-bottom: 4px;
  &:hover, &.active { background: $bg-hover; }
}
.chart-area { background: $bg-card; border-radius: 8px; padding: 16px; min-height: 400px; }
.placeholder-chart { display: flex; align-items: center; justify-content: center; height: 360px; color: #718096; }
</style>
EOF

# TradeView
cat > src/views/TradeView.vue << 'EOF'
<template>
  <div class="trade">
    <h1>💹 模拟交易</h1>
    <div class="trade-content">
      <div class="account-info">
        <h3>账户信息</h3>
        <div class="info-grid">
          <div class="info-item"><span>总资产</span><strong>{{ balance.total_assets?.toLocaleString() || 0 }}</strong></div>
          <div class="info-item"><span>可用资金</span><strong>{{ balance.cash?.toLocaleString() || 0 }}</strong></div>
          <div class="info-item"><span>总盈亏</span><strong :class="balance.total_pnl >= 0 ? 'text-gain' : 'text-loss'">{{ balance.total_pnl?.toLocaleString() || 0 }}</strong></div>
          <div class="info-item"><span>手续费</span><strong>{{ balance.total_fees?.toFixed(2) || 0 }}</strong></div>
        </div>
      </div>
      <div class="positions">
        <h3>当前持仓</h3>
        <el-table :data="positions" stripe>
          <el-table-column prop="ticker" label="股票" />
          <el-table-column prop="quantity" label="数量" />
          <el-table-column prop="entry_price" label="成本" />
          <el-table-column prop="current_price" label="现价" />
          <el-table-column label="盈亏">
            <template #default="{ row }">
              <span :class="row.unrealized_pnl >= 0 ? 'text-gain' : 'text-loss'">
                {{ row.unrealized_pnl.toFixed(2) }} ({{ row.unrealized_pnl_pct.toFixed(2) }}%)
              </span>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useAccountStore } from '../stores/account'
import { storeToRefs } from 'pinia'

const accountStore = useAccountStore()
const { balance, positions } = storeToRefs(accountStore)

onMounted(() => {
  accountStore.fetchBalance()
})
</script>

<style lang="scss" scoped>
@import '../styles/BloombergTheme.scss';
.trade-content { display: grid; grid-template-columns: 1fr 2fr; gap: 24px; margin-top: 24px; }
.account-info, .positions { background: $bg-card; border-radius: 8px; padding: 20px; }
.info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 16px; }
.info-item { display: flex; flex-direction: column; gap: 4px;
  span { font-size: 12px; color: #718096; }
  strong { font-size: 18px; }
}
</style>
EOF
```

#### 步骤 10: 启动服务

```bash
# 终端1: 启动后端
cd "D:/transformer/Stock Forecast"
python -m uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload

# 终端2: 启动前端
cd D:/transformer/frontend
npm run dev
```

---

### 3. 验证清单

- [ ] 后端启动成功: `curl http://localhost:8000/api/v1/health`
- [ ] 前端启动成功: `http://localhost:5173` 能打开
- [ ] Dashboard 页面显示指标数据
- [ ] Analysis 页面显示股票列表
- [ ] Trade 页面显示账户信息
- [ ] 三个页面之间可以正常切换导航

---

### 4. 完整文件清单

执行后应生成以下文件：

```
frontend/
├── src/
│   ├── main.ts
│   ├── App.vue
│   ├── api/
│   │   └── index.ts
│   ├── stores/
│   │   ├── ticker.ts
│   │   └── account.ts
│   ├── router/
│   │   └── index.ts
│   ├── styles/
│   │   └── BloombergTheme.scss
│   ├── types/
│   │   └── api.d.ts
│   └── views/
│       ├── DashboardView.vue
│       ├── AnalysisView.vue
│       └── TradeView.vue
├── package.json
├── tsconfig.json
├── vite.config.ts
└── index.html
```
