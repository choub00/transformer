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
cd D:/transformer
npm create vite@latest frontend -- --template vue-ts
cd frontend
pnpm add vue-router pinia element-plus echarts axios @vueuse/core
pnpm add -D sass
```

### 2.2 File Structure

```
frontend/src/
├── main.ts
├── App.vue
├── router/index.ts
├── stores/
│   ├── ticker.ts      # selectedTicker state
│   └── account.ts     # account state
├── api/
│   └── index.ts       # Axios with cancel logic
├── views/
│   ├── DashboardView.vue
│   ├── AnalysisView.vue
│   └── TradeView.vue
└── styles/
    └── BloombergTheme.scss
```

### 2.3 Axios with Request Cancellation

```typescript
// src/api/index.ts
import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  timeout: 30000
})

// Request interceptor - AbortController for cancel
api.interceptors.request.use((config) => {
  const controller = new AbortController()
  config.signal = controller.signal
  ;(config as any)._controller = controller
  return config
})

// Response interceptor - Error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (!axios.isCancel(error)) {
      const message = error.response?.data?.error?.message ||
                      error.response?.data?.detail || 'Request failed'
      console.error('API Error:', message)
    }
    return Promise.reject(error)
  }
)

export default api
```

### 2.4 Pinia Store

```typescript
// src/stores/ticker.ts
import { defineStore } from 'pinia'

export const useTickerStore = defineStore('ticker', () => {
  const selectedTicker = ref<string>('AAPL')

  function selectTicker(ticker: string) {
    selectedTicker.value = ticker
  }

  return { selectedTicker, selectTicker }
})
```

### 2.5 Router

```typescript
// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from '../views/DashboardView.vue'
import AnalysisView from '../views/AnalysisView.vue'
import TradeView from '../views/TradeView.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: DashboardView },
    { path: '/analysis', component: AnalysisView },
    { path: '/trade', component: TradeView },
  ]
})
```

### 2.6 Bloomberg Dark Theme

```scss
// src/styles/BloombergTheme.scss
$bg-primary: #0a1628;
$bg-secondary: #132743;
$bg-card: #1a3050;
$accent-gold: #d4af37;
$accent-green: #00ff88;
$accent-red: #ff4444;

body {
  background: $bg-primary;
  color: #e8e8e8;
}
```

### 2.7 App.vue

```vue
<template>
  <el-config-provider :locale="zhCn">
    <router-view />
  </el-config-provider>
</template>

<script setup>
import { ElConfigProvider } from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
</script>
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

1. Start backend: `cd D:/transformer/Stock Forecast && uvicorn api.server:app --reload --port 8000`
2. Start frontend: `cd D:/transformer/frontend && pnpm dev`
3. Test buy stock - price should reflect realistic value (e.g., 贵州茅台 ~1680 RMB)
4. Test `/api/v1/positions` - no ticker=null errors
5. Verify all three pages load correctly

---

## Success Criteria

1. Buy prices reflect real stock prices (e.g., 贵州茅台 ~1680 RMB)
2. No ticker=null validation errors
3. Frontend three pages work correctly
4. Stock switch triggers chart refresh
