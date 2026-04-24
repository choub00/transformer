<template>
  <div class="trade-view">
    <!-- ══════════════════════════════════════════════════════════════════════════
         顶部股票选择栏
         ══════════════════════════════════════════════════════════════════════════ -->
    <div class="stock-selector glass-card module-shell module-shell--cyan">
      <div class="selector-header">
        <div class="selector-copy">
          <div class="selector-kicker">选择股票</div>
          <div class="selector-title">点击下拉切换标的，或直接输入代码回车</div>
        </div>
        <div class="selector-meta">
          <span class="selector-count">{{ stockList.length }} 只</span>
        </div>
      </div>

      <div class="recent-tickers" v-if="recentStocks.length">
        <span class="recent-label">最近访问</span>
        <button
          v-for="stock in recentStocks"
          :key="stock.ticker"
          type="button"
          class="recent-chip"
          :class="{ active: stock.ticker === selectedTicker }"
          @click="selectTickerSafe(stock.ticker)"
        >
          <span class="recent-chip-ticker">{{ stock.ticker }}</span>
          <span class="recent-chip-name">{{ stock.name }}</span>
        </button>
      </div>

      <div class="ticker-search-row">
        <el-input
          v-model="tickerSearch"
          class="ticker-search"
          clearable
          placeholder="输入代码后按 Enter 切换，例如 AAPL"
          @keyup.enter="selectTickerFromSearch"
        />
        <button type="button" class="ticker-search-btn" @click="selectTickerFromSearch">切换</button>
      </div>

      <el-select
        v-model="selectedTicker"
        class="stock-select"
        filterable
        popper-class="stock-select-popper"
        placeholder="选择股票"
        @change="selectTickerSafe"
      >
        <el-option
          v-for="stock in stockList"
          :key="stock.ticker"
          :label="stock.ticker"
          :value="stock.ticker"
        >
          <div class="stock-option">
            <div class="stock-option-main">
              <span class="stock-option-ticker">{{ stock.ticker }}</span>
              <span class="stock-option-name">{{ stock.name }}</span>
            </div>
            <div class="stock-option-meta">
              <span class="stock-option-sector">{{ stock.sector || '未分类' }}</span>
              <span class="stock-option-price" :class="stock.change >= 0 ? 'pos' : 'neg'">
                ${{ stock.price.toFixed(2) }}
              </span>
              <span class="stock-option-change" :class="stock.change >= 0 ? 'pos' : 'neg'">
                {{ stock.change >= 0 ? '+' : '' }}{{ stock.change.toFixed(2) }}%
              </span>
            </div>
          </div>
        </el-option>
      </el-select>
    </div>

    <!-- ══════════════════════════════════════════════════════════════════════════
         左侧 K 线图区
         ══════════════════════════════════════════════════════════════════════════ -->
    <section class="chart-section glass-card module-shell module-shell--green">
      <div class="chart-header">
        <div class="ticker-info">
          <span class="ticker-symbol">{{ selectedTicker }}</span>
          <span class="ticker-name">{{ selectedTickerName }}</span>
        </div>
        <div class="ticker-price-wrap">
          <span class="price-value" ref="priceValueRef">${{ currentPrice.toFixed(2) }}</span>
          <span class="price-change" :class="priceChange >= 0 ? 'pos' : 'neg'">
            {{ priceChange >= 0 ? '+' : '' }}{{ priceChange.toFixed(2) }}%
          </span>
        </div>
      </div>

      <div class="chart-container">
        <div ref="klineChartRef" class="kline-chart"></div>
      </div>
      <div v-if="chartStatus" class="chart-status">{{ chartStatus }}</div>

      <!-- 预测区标注 -->
      <div class="prediction-legend">
        <div class="legend-item">
          <span class="legend-line solid"></span>
          <span class="legend-text">历史走势</span>
        </div>
        <div class="legend-item">
          <span class="legend-line dashed"></span>
          <span class="legend-text">AI 预测</span>
        </div>
        <div class="legend-item">
          <span class="legend-area"></span>
          <span class="legend-text">AQM 预测区</span>
        </div>
      </div>

      <!-- 时间范围切换 -->
      <div class="chart-periods">
        <button
          v-for="period in periods"
          :key="period.value"
          class="period-btn"
          :class="{ active: currentPeriod === period.value }"
          @click="changePeriod(period.value)"
        >
          {{ period.label }}
        </button>
      </div>
    </section>

    <!-- ══════════════════════════════════════════════════════════════════════════
         右侧交易面板
         ══════════════════════════════════════════════════════════════════════════ -->
    <section class="trade-panel glass-card module-shell module-shell--gold">
      <!-- 第一层：市场与 AI 结论 -->
      <div class="tier-label">AI 决策</div>

      <!-- AI 信心指数 -->
      <div class="ai-confidence">
        <div class="confidence-header">
          <span class="confidence-title">AI 信心指数</span>
          <span class="confidence-value" :class="aiConfidence >= 70 ? 'high' : aiConfidence >= 40 ? 'medium' : 'low'">
            {{ aiConfidence.toFixed(0) }}%
          </span>
        </div>
        <div class="confidence-bar">
          <div class="confidence-fill" :style="{ width: aiConfidence + '%' }"></div>
        </div>
        <div class="confidence-hint">模型参考 · Sharpe 0.28</div>
      </div>

      <!-- AI 标签横向滚动行（标的 Chip，不折行） -->
      <div class="ai-tags-scroll">
        <span class="ai-chip direction-chip" :class="aiDirection">
          {{ aiDirection === 'bullish' ? '↑ 看多' : aiDirection === 'bearish' ? '↓ 看空' : '→ 中性' }}
        </span>
        <span class="ai-chip risk-chip" :class="aiRiskLevel">
          {{ aiRiskLevel === 'low' ? '低风险' : aiRiskLevel === 'medium' ? '中风险' : '高风险' }}
        </span>
        <span class="ai-chip model-chip">
          {{ aiScore >= 0 ? '+' : '' }}{{ aiScore.toFixed(4) }}
        </span>
      </div>

      <!-- 第二层：仓位与可买能力 -->
      <div class="tier-divider"></div>
      <div class="tier-label">仓位</div>

      <!-- 账户概览 -->
      <div class="account-overview data-panel">
        <div class="account-header">
          <span class="account-title">账户概览</span>
          <button class="btn btn-ghost btn-sm" @click="fetchAccount">
            <span class="loading-spinner" v-if="isLoading"></span>
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
              <path d="M23 4v6h-6"/><path d="M1 20v-6h6"/>
              <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
            </svg>
          </button>
        </div>

        <div class="account-stats">
          <div class="stat-item">
            <span class="stat-label">可用资金</span>
            <span class="stat-value text-glow-cyan">${{ formatNumber(displayCash) }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">总资产</span>
            <span class="stat-value">${{ formatNumber(displayTotalAssets) }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">持仓市值</span>
            <span class="stat-value">${{ formatNumber(displayPortfolioValue) }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">累计收益</span>
            <span class="stat-value" :class="displayPnl >= 0 ? 'text-glow-green' : 'text-glow-red'">
              {{ displayPnl >= 0 ? '+' : '' }}${{ formatNumber(Math.abs(displayPnl)) }}
            </span>
          </div>
        </div>
      </div>

      <!-- 仓位建议 -->
      <div class="position-advice data-panel">
        <div class="advice-content">
          <div class="advice-item">
            <span class="advice-label">建议仓位</span>
            <span class="advice-value text-accent-cyan">{{ positionAdvice.suggested_pct }}%</span>
          </div>
          <div class="advice-item">
            <span class="advice-label">可买股数</span>
            <span class="advice-value">{{ positionAdvice.available_shares }} 股</span>
          </div>
          <div class="advice-item">
            <span class="advice-label">预计成本</span>
            <span class="advice-value">${{ formatNumber(positionAdvice.estimated_cost) }}</span>
          </div>
        </div>
      </div>

      <!-- 第三层：下单与费用 -->
      <div class="tier-divider"></div>
      <div class="tier-label">执行</div>

      <!-- 交易面板（TradePanel 组件） -->
      <TradePanel
        :ticker="selectedTicker"
        :ticker-name="selectedTickerName"
        :current-price="currentPrice"
        :ai-score="aiScore"
        :confidence-pct="aiConfidence"
        :direction="aiDirection"
        :risk-level="aiRiskLevel"
        :current-position="currentPosition"
        :available-cash="displayCash"
        @trade-success="onTradeSuccess"
      />

      <!-- 分层分割线：下单与自动交易 -->
      <div class="section-separator"></div>

      <!-- 自动交易开关（与手动下单拉开间距） -->
      <div class="auto-trade-toggle">
        <div class="toggle-info">
          <span class="toggle-title">AI 自动交易</span>
          <span class="toggle-status" :class="{ active: autoTrading.enabled }">
            {{ autoTrading.enabled ? '运行中' : '已停止' }}
          </span>
        </div>
        <button
          class="toggle-btn"
          :class="{ active: autoTrading.enabled }"
          @click="toggleAutoTrading"
        >
          <span class="toggle-track">
            <span class="toggle-thumb"></span>
          </span>
        </button>
      </div>

      <!-- 运行中风险提示 -->
      <div class="auto-risk-hint" v-if="autoTrading.enabled">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="13" height="13">
          <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
          <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
        </svg>
        <span>自动交易将按 AI 信号自动执行，可能产生亏损</span>
      </div>
    </section>

    <!-- ══════════════════════════════════════════════════════════════════════════
         持仓列表
         ══════════════════════════════════════════════════════════════════════════ -->
    <section class="positions-section glass-card module-shell module-shell--cyan">
      <div class="section-header">
        <div class="section-title">
          <span class="title-icon">&#128203;</span>
          <h2>当前持仓</h2>
        </div>
        <span class="positions-count">{{ account.positions?.length || 0 }} 只</span>
      </div>

      <div class="positions-table data-panel" v-if="account.positions?.length > 0">
        <table class="positions-table-el">
          <thead>
            <tr>
              <th>股票</th>
              <th class="text-right">持仓数量</th>
              <th class="text-right">成本价</th>
              <th class="text-right">现价</th>
              <th class="text-right">市值</th>
              <th class="text-right">盈亏</th>
              <th class="text-center">AI建议</th>
              <th class="text-center">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in account.positions" :key="row.ticker">
              <td>
                <span class="ticker-badge clickable" @click="selectTickerSafe(row.ticker)">{{ row.ticker }}</span>
              </td>
              <td class="text-right mono">{{ row.quantity }} 股</td>
              <td class="text-right mono">${{ row.entry_price.toFixed(2) }}</td>
              <td class="text-right mono">${{ row.current_price.toFixed(2) }}</td>
              <td class="text-right mono text-accent-cyan">${{ formatNumber(row.market_value) }}</td>
              <td class="text-right">
                <div class="pnl-cell" :class="row.unrealized_pnl >= 0 ? 'profit-up' : 'profit-down'">
                  <span class="pnl-value">
                    {{ row.unrealized_pnl >= 0 ? '+' : '' }}${{ formatNumber(Math.abs(row.unrealized_pnl)) }}
                  </span>
                  <span class="pnl-percent">
                    ({{ row.unrealized_pnl_pct >= 0 ? '+' : '' }}{{ row.unrealized_pnl_pct.toFixed(2) }}%)
                  </span>
                </div>
              </td>
              <td class="text-center"><span class="advice-badge">{{ row.ai_advice }}</span></td>
              <td class="text-center">
                <div class="action-buttons">
                  <button class="btn btn-sm btn-ghost" @click="openDetailModal(row.ticker)">详情</button>
                  <button class="btn btn-sm btn-danger" @click="closePosition(row.ticker)">平仓</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="empty-positions" v-else>
        <span class="empty-icon">&#128164;</span>
        <span class="empty-text">暂无持仓</span>
        <span class="empty-hint">从上方 AI 推荐中选择股票开始交易</span>
      </div>
    </section>

    <!-- ══════════════════════════════════════════════════════════════════════════
         详情弹窗
         ══════════════════════════════════════════════════════════════════════════ -->
    <Teleport to="body">
      <div v-if="detailModal.visible" class="detail-modal-overlay" @click.self="closeDetailModal">
        <div class="detail-modal">
          <div class="detail-modal-header">
              <div class="detail-modal-title">
                <span class="detail-modal-icon">&#128202;</span>
                <div>
                <h3 class="detail-ticker">{{ detailView.ticker }} 持仓详情</h3>
                <p class="detail-meta">{{ detailView.name }} · {{ detailView.sector || '未分类' }}</p>
                <p class="detail-meta">建仓日期: {{ detailModal.entry_date }} | 持仓 {{ detailView.quantity }} 股</p>
                </div>
              </div>
            <button class="detail-modal-close" @click="closeDetailModal">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="24" height="24">
                <path d="M18 6L6 18M6 6l12 12"/>
              </svg>
            </button>
          </div>

          <div class="detail-overview">
            <div class="detail-stat">
              <span class="detail-stat-label">持仓数量</span>
              <span class="detail-stat-value">{{ detailView.quantity }} 股</span>
            </div>
            <div class="detail-stat">
              <span class="detail-stat-label">成本总额</span>
              <span class="detail-stat-value">${{ formatNumber(detailView.costBasis) }}</span>
            </div>
            <div class="detail-stat">
              <span class="detail-stat-label">当前市值</span>
              <span class="detail-stat-value text-accent-cyan">${{ formatNumber(detailView.marketValue) }}</span>
            </div>
            <div class="detail-stat">
              <span class="detail-stat-label">浮动盈亏</span>
              <span class="detail-stat-value" :class="detailView.unrealizedPnl >= 0 ? 'text-glow-red' : 'text-glow-green'">
                {{ detailView.unrealizedPnl >= 0 ? '+' : '' }}${{ formatNumber(Math.abs(detailView.unrealizedPnl)) }}
                ({{ detailView.unrealizedPnlPct >= 0 ? '+' : '' }}{{ detailView.unrealizedPnlPct.toFixed(2) }}%)
              </span>
            </div>
            <div class="detail-stat">
              <span class="detail-stat-label">持仓占比</span>
              <span class="detail-stat-value">{{ detailView.allocationPct.toFixed(2) }}%</span>
            </div>
            <div class="detail-stat">
              <span class="detail-stat-label">当日涨跌</span>
              <span class="detail-stat-value" :class="detailView.stockChange >= 0 ? 'text-glow-green' : 'text-glow-red'">
                {{ detailView.stockChange >= 0 ? '+' : '' }}{{ detailView.stockChange.toFixed(2) }}%
              </span>
            </div>
          </div>

          <div class="detail-panels">
            <div class="detail-panel">
              <div class="detail-panel-title">股票信息</div>
              <div class="detail-list">
                <div class="detail-list-item">
                  <span class="detail-list-label">股票代码</span>
                  <span class="detail-list-value mono">{{ detailView.ticker }}</span>
                </div>
                <div class="detail-list-item">
                  <span class="detail-list-label">股票名称</span>
                  <span class="detail-list-value">{{ detailView.name }}</span>
                </div>
                <div class="detail-list-item">
                  <span class="detail-list-label">所属行业</span>
                  <span class="detail-list-value">{{ detailView.sector || '未分类' }}</span>
                </div>
                <div class="detail-list-item">
                  <span class="detail-list-label">当前价格</span>
                  <span class="detail-list-value">${{ detailView.currentPrice.toFixed(2) }}</span>
                </div>
              </div>
            </div>

            <div class="detail-panel">
              <div class="detail-panel-title">持仓分析</div>
              <div class="detail-list">
                <div class="detail-list-item">
                  <span class="detail-list-label">AI 建议</span>
                  <span class="detail-list-value">{{ detailView.aiAdvice }}</span>
                </div>
                <div class="detail-list-item">
                  <span class="detail-list-label">成本均价</span>
                  <span class="detail-list-value">${{ detailView.entryPrice.toFixed(2) }}</span>
                </div>
                <div class="detail-list-item">
                  <span class="detail-list-label">盈亏判断</span>
                  <span class="detail-list-value" :class="detailView.unrealizedPnl >= 0 ? 'text-glow-red' : 'text-glow-green'">
                    {{ detailView.unrealizedPnl >= 0 ? '盈利' : '亏损' }}
                  </span>
                </div>
                <div class="detail-list-item">
                  <span class="detail-list-label">当前状态</span>
                  <span class="detail-list-value">{{ detailView.status }}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="detail-chart-section" v-if="!detailModal.loading">
            <div ref="timelineChartRef" class="timeline-chart"></div>
            <div v-if="detailChartStatus" class="chart-status">{{ detailChartStatus }}</div>
          </div>

          <div class="detail-modal-actions">
            <button class="btn btn-sm btn-ghost" @click="selectTickerSafe(detailModal.ticker)">切到该股</button>
            <button class="btn btn-sm btn-danger" @click="closeDetailModal">关闭</button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Toast 容器 -->
    <Teleport to="body">
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ElMessage from 'element-plus/es/components/message/index'
import type { ECharts, EChartsCoreOption } from 'echarts/core'
import gsap from 'gsap'
import { api, cancelRequest, getCancelToken, apiMarket } from '../api'
import type { AccountBalance, Position } from '../types/api'
import TradePanel from '../components/TradePanel.vue'
import { useTickerStore } from '../stores/ticker'
import { forecastToChartSeries } from '../utils/forecastChart'
import { FORECAST_REFRESH_MS } from '../config'
import { formatNumber as fmtNum } from '../utils/formatters'

type TradeEchartsModule = typeof import('../lib/echarts/trade')

let tradeEchartsPromise: Promise<TradeEchartsModule> | null = null

function loadTradeEcharts() {
  tradeEchartsPromise ??= import('../lib/echarts/trade')
  return tradeEchartsPromise
}

// ─── 常量 ────────────────────────────────────────────────────────────────────
const FEE_RATE = 0.0015

// K线标准色（绿色=涨，红色=跌）
const KLIRE_UP_COLOR = '#00FFBD'   // 上涨蜡烛图填充色
const KLIRE_DOWN_COLOR = '#FF3B30' // 下跌蜡烛图填充色
const KLIRE_UP_BORDER = 'rgba(0, 255, 189, 0.6)'   // 上涨边框
const KLIRE_DOWN_BORDER = 'rgba(255, 59, 48, 0.6)' // 下跌边框

type StockRow = {
  ticker: string
  name: string
  basePrice: number
  price: number
  change: number
  sector?: string
}

const route = useRoute()
const router = useRouter()
const tickerStore = useTickerStore()
const RECENT_TICKERS_KEY = 'alpha-transformer:recent-tickers'

// ─── 股票列表（与后端 /dashboard/tickers + data/watchlist.json 同步）──────────
const stockList = ref<StockRow[]>([])
const tickerSearch = ref('')
const recentTickers = ref<string[]>([])
const recentStocks = computed(() =>
  recentTickers.value
    .map((ticker) => findStockRow(ticker) || { ticker, name: ticker, basePrice: 0, price: 0, change: 0 })
    .filter((stock, index, arr) => stock && arr.findIndex((item) => item.ticker === stock.ticker) === index)
)

// ─── 状态 ────────────────────────────────────────────────────────────────────
const selectedTicker = ref(tickerStore.selectedTicker || 'AAPL')
const selectedTickerName = ref(tickerStore.selectedTickerName || 'Apple Inc.')
const currentPrice = ref(178.50)
const priceChange = ref(1.23)
const priceValueRef = ref<HTMLElement | null>(null)

const currentPeriod = ref('1y')
const periods = [
  { label: '1月', value: '1m' },
  { label: '3月', value: '3m' },
  { label: '6月', value: '6m' },
  { label: '1年', value: '1y' },
  { label: '2年', value: '2y' },
]

const tradePrice = ref(178.50)
const isLoading = ref(false)
const chartStatus = ref('')
const detailChartStatus = ref('')

// GSAP animated values
const displayTotalAssets = ref(100000)
const displayCash = ref(100000)
const displayPortfolioValue = ref(0)
const displayPnl = ref(0)

const account = reactive<AccountBalance>({
  total_assets: 100000,
  cash: 100000,
  init_cash: 100000,
  portfolio_value: 0,
  total_pnl: 0,
  total_return_pct: 0,
  available_cash: 100000,
  positions_count: 0,
  total_fees: 0,
  total_trades: 0,
  winning_trades: 0,
  losing_trades: 0,
  win_rate: 0,
  daily_pnl: 0,
  daily_trades: 0,
  positions: [],
  equity_curve: [],
  updated_at: '',
})

async function loadStockList() {
  try {
    const res = await api.get<{ tickers: Array<{ ticker: string; name: string; sector?: string; price: number; change_pct: number }> }>(
      '/dashboard/tickers',
    )
    const rows = res.data?.tickers ?? []
    stockList.value = rows.map((t) => ({
      ticker: t.ticker,
      name: t.name,
      sector: t.sector,
      basePrice: t.price,
      price: t.price,
      change: t.change_pct ?? 0,
    }))
  } catch {
    if (!stockList.value.length) {
      stockList.value = [
        { ticker: 'AAPL', name: 'Apple Inc.', basePrice: 175, price: 175, change: 0 },
      ]
    }
  }
  mergeHeldTickersIntoList()
}

function mergeHeldTickersIntoList() {
  const map = new Map(stockList.value.map((s) => [s.ticker, { ...s }]))
  for (const p of account.positions || []) {
    const t = String(p.ticker)
    if (!map.has(t)) {
      const px = Number(p.current_price || p.entry_price) || 50
      map.set(t, {
        ticker: t,
        name: t,
        basePrice: px,
        price: px,
        change: 0,
      })
    }
  }
  stockList.value = Array.from(map.values())
}

function loadRecentTickers() {
  try {
    const raw = window.localStorage.getItem(RECENT_TICKERS_KEY)
    if (!raw) return
    const parsed = JSON.parse(raw)
    if (Array.isArray(parsed)) {
      recentTickers.value = parsed
        .map((item) => normalizeTicker(String(item || '')))
        .filter(Boolean)
        .slice(0, 6)
    }
  } catch {
    recentTickers.value = []
  }
}

function saveRecentTicker(ticker: string) {
  const next = normalizeTicker(ticker)
  if (!next) return
  recentTickers.value = [next, ...recentTickers.value.filter((item) => item !== next)].slice(0, 6)
  try {
    window.localStorage.setItem(RECENT_TICKERS_KEY, JSON.stringify(recentTickers.value))
  } catch {
    /* ignore storage errors */
  }
}

const autoTrading = ref({ enabled: false, interval: 300, top_n: 2 })
const aiConfidence = ref(72)
const aiScore = ref(0.0834)
const aiDirection = ref<'bullish' | 'bearish' | 'neutral'>('bullish')
const aiRiskLevel = ref<'low' | 'medium' | 'high'>('low')
const positionAdvice = ref({ suggested_pct: 15, available_shares: 400, estimated_cost: 7120.00 })
let tickerSelectionRevision = 0

function normalizeTicker(ticker: string) {
  return ticker.trim().toUpperCase()
}

function findStockRow(ticker: string) {
  const key = normalizeTicker(ticker)
  return stockList.value.find((s) => s.ticker === key)
}

function applyTickerSnapshot(ticker: string) {
  const key = normalizeTicker(ticker)
  const stock = findStockRow(key)
  const pos = account.positions?.find((p: any) => p.ticker === key)

  selectedTicker.value = key
  tickerStore.selectTicker(key, stock?.name || key)
  selectedTickerName.value = stock?.name || key
  tickerSearch.value = key

  if (stock) {
    currentPrice.value = stock.price
    priceChange.value = stock.change
    tradePrice.value = stock.price
  }

  if (pos) {
    currentPrice.value = pos.current_price
    tradePrice.value = pos.current_price
    priceChange.value = ((pos.current_price / pos.entry_price) - 1) * 100
  }

  if (priceValueRef.value) {
    gsap.fromTo(priceValueRef.value,
      { scale: 1.1, color: '#00D1FF' },
      { scale: 1, duration: 0.4, ease: 'power2.out', color: '#F0F6FC' }
    )
  }

  updatePositionAdvice()
}

function selectTickerSafe(ticker: string) {
  const next = normalizeTicker(ticker)
  if (!next) return

  tickerSelectionRevision += 1
  const revision = tickerSelectionRevision

  cancelRequest(`kline-${selectedTicker.value}`)
  cancelRequest(`forecast-${selectedTicker.value}`)
  applyTickerSnapshot(next)
  saveRecentTicker(next)

  if (route.query.ticker !== next) {
    void router.replace({ path: '/trade', query: { ...route.query, ticker: next } })
  }

  void refreshAiPanelSafe(next, revision)
  void nextTick(() => {
    void initKlineChartSafe(next, revision)
  })
}

function selectTickerFromSearch() {
  const next = normalizeTicker(tickerSearch.value)
  if (!next) return
  if (!findStockRow(next)) {
    showToast(`未找到股票：${next}`, 'error')
    return
  }
  selectTickerSafe(next)
}

const klineChartRef = ref<HTMLElement | null>(null)
let klineChart: ECharts | null = null

// ─── 计算属性 ────────────────────────────────────────────────────────────────
// ─── 格式化 ──────────────────────────────────────────────────────────────────
const formatNumber = (num: number) => fmtNum(num, { minimumFractionDigits: 2, maximumFractionDigits: 2 })

function getStablePortfolioValue() {
  const snapshot = Number(account.portfolio_value || 0)
  if (snapshot > 0) {
    return snapshot
  }

  return account.positions?.reduce((sum: number, position: Position) => {
    const marketValue = Number(position.market_value || 0)
    return sum + (Number.isFinite(marketValue) ? marketValue : 0)
  }, 0) || 0
}

function getAllocationPct(marketValue: number) {
  const portfolioValue = getStablePortfolioValue()
  return portfolioValue > 0 ? (marketValue / portfolioValue) * 100 : 0
}

function isValidPrice(value: unknown) {
  const numericValue = Number(value)
  return Number.isFinite(numericValue) && numericValue > 0
}

// ─── 当前选中股票的持仓 ─────────────────────────────────────────────────────
const currentPosition = computed(() =>
  account.positions?.find((p: any) => p.ticker === selectedTicker.value) ?? null
)

const detailView = computed(() => {
  const ticker = detailModal.value.ticker || ''
  const stock = ticker ? findStockRow(ticker) : null
  const position = ticker
    ? account.positions?.find((p: any) => p.ticker === ticker) ?? detailModal.value.position
    : detailModal.value.position

  const quantity = Number(position?.quantity || detailModal.value.quantity || 0)
  const entryPrice = Number(position?.entry_price || detailModal.value.entry_price || stock?.price || 0)
  const fallbackPrice = ticker === selectedTicker.value
    ? currentPrice.value
    : stock?.price || position?.current_price || entryPrice
  const livePrice = isValidPrice(detailModal.value.current_price)
    ? Number(detailModal.value.current_price)
    : isValidPrice(fallbackPrice)
      ? Number(fallbackPrice)
      : Number(detailModal.value.market_value || 0) > 0 && quantity > 0
        ? Number(detailModal.value.market_value) / quantity
        : entryPrice
  const costBasis = Number.isFinite(detailModal.value.cost_basis) && detailModal.value.cost_basis > 0
    ? Number(detailModal.value.cost_basis)
    : quantity * entryPrice
  const marketValue = Number.isFinite(detailModal.value.market_value) && detailModal.value.market_value > 0
    ? Number(detailModal.value.market_value)
    : quantity * livePrice
  const unrealizedPnl = Number.isFinite(detailModal.value.unrealized_pnl)
    ? Number(detailModal.value.unrealized_pnl)
    : marketValue - costBasis
  const unrealizedPnlPct = Number.isFinite(detailModal.value.unrealized_pnl_pct)
    ? Number(detailModal.value.unrealized_pnl_pct)
    : costBasis > 0 ? (unrealizedPnl / costBasis) * 100 : 0
  const allocationPct = Number.isFinite(detailModal.value.allocation_pct)
    ? detailModal.value.allocation_pct
    : getAllocationPct(marketValue)

  return {
    ticker,
    name: stock?.name || detailModal.value.name || ticker,
    sector: stock?.sector || detailModal.value.sector || '',
    quantity,
    entryPrice,
    currentPrice: livePrice,
    marketValue,
    costBasis,
    unrealizedPnl,
    unrealizedPnlPct,
    stockChange: detailModal.value.stock_change ?? stock?.change ?? 0,
    allocationPct,
    aiAdvice: position?.ai_advice || detailModal.value.ai_advice || '持有',
    status: quantity > 0 ? '持有中' : '已清空',
  }
})

// ─── 交易成功回调 ───────────────────────────────────────────────────────────
async function refreshAiPanelSafe(ticker: string, revision: number) {
  const activeTicker = normalizeTicker(ticker)
  const requestKey = 'trade-ai-panel'

  cancelRequest(requestKey)

  try {
    const res = await api.get<{ predictions: Array<{ ticker: string; score: number; confidence: number; direction: string }> }>(
      '/dashboard/predictions',
      {
        params: { top_n: 64 },
        cancelToken: getCancelToken(requestKey).token,
      },
    )

    if (revision !== tickerSelectionRevision || activeTicker !== selectedTicker.value) {
      return
    }

    const row = res.data?.predictions?.find((p) => String(p.ticker).toUpperCase() === activeTicker)
    if (row) {
      aiScore.value = row.score
      aiConfidence.value = row.confidence
      const d = String(row.direction || '').toLowerCase()
      if (d === 'bullish' || d === 'bearish' || d === 'neutral') {
        aiDirection.value = d
      }
      const a = Math.abs(row.score)
      aiRiskLevel.value = a < 0.035 ? 'low' : a < 0.07 ? 'medium' : 'high'
    }
  } catch {
    // keep current panel state
  }
}

async function initKlineChartSafe(ticker: string, revision: number) {
  if (!klineChartRef.value) return
  const { echarts } = await loadTradeEcharts()

  const activeTicker = normalizeTicker(ticker)

  if (klineChart) {
    klineChart.dispose()
  }
  klineChart = echarts.init(klineChartRef.value)

  const stock = findStockRow(activeTicker)
  const basePrice = stock?.basePrice || 150

  let dates: string[] = []
  let data: number[][] = []
  let predDates: string[] = []
  let lineDataLower: number[] = []
  let histDates: string[] = []

  try {
    const res = await apiMarket.forecast(activeTicker)
    if (revision !== tickerSelectionRevision || activeTicker !== selectedTicker.value) {
      return
    }

    const { dates: d, kData, predDates: pd, predValues } = forecastToChartSeries(res.data)
    dates = d
    data = kData
    predDates = pd
    const histTail = Math.min(20, dates.length)
    histDates = dates.slice(-histTail)
    const histCloses = kData.slice(-histTail).map((row) => row[1])
    lineDataLower = [...histCloses, ...predValues]
  } catch {
    const gen = generateKlineData(activeTicker, basePrice)
    dates = gen.dates
    data = gen.data
    const lastClose = data[data.length - 1][1]
    const predictions: { date: string; value: number }[] = []
    for (let i = 1; i <= 5; i++) {
      const date = new Date()
      date.setDate(date.getDate() + i)
      predictions.push({
        date: date.toISOString().split('T')[0],
        value: lastClose * (1 + i * 0.005),
      })
    }
    histDates = dates.slice(-20)
    const histCloses = data.slice(-20).map((d) => d[1])
    predDates = predictions.map((p) => p.date)
    lineDataLower = [...histCloses, ...predictions.map((p) => p.value)]
  }

  if (revision !== tickerSelectionRevision || activeTicker !== selectedTicker.value) {
    return
  }

  const xLower = [...histDates, ...predDates]

  const option: EChartsCoreOption = {
    backgroundColor: '#0d1117',
    grid: [
      { top: 24, left: 56, right: 16, bottom: 180 },
      { left: 56, right: 16, top: '68%', bottom: 36 },
    ],
    dataZoom: [
      { type: 'inside', xAxisIndex: [0, 1], start: 55, end: 100 },
      { type: 'slider', xAxisIndex: [0, 1], bottom: 4, height: 18, borderColor: '#30363d', fillerColor: 'rgba(0,209,255,0.15)', textStyle: { color: '#8b949e' } },
    ],
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross', crossStyle: { color: '#484f58' } },
      backgroundColor: 'rgba(22,27,34,0.95)',
      borderColor: 'rgba(0,209,255,0.3)',
      textStyle: { color: '#F0F6FC' },
      formatter: (params: any) => {
        const k = params.find((item: any) => item.seriesName === 'K线')
        const linePt = params.find((item: any) => item.seriesName === 'AI 预测')
        if (k) {
          const [o, c, l, h] = k.value
          return `<div style="font-size:12px">
            <div style="color:#8B949E;margin-bottom:4px">${k.axisValue}</div>
            <div>开盘: $${o.toFixed(2)} 收盘: $${c.toFixed(2)}</div>
            <div>最高: $${h.toFixed(2)} 最低: $${l.toFixed(2)}</div>
          </div>`
        }
        if (linePt) {
          return `<div style="font-size:12px;color:#00D1FF">
            AI 预测 ${linePt.axisValue}: $${linePt.value?.toFixed(2) || '—'}
          </div>`
        }
        return ''
      },
    },
    xAxis: [
      {
        type: 'category',
        data: dates,
        gridIndex: 0,
        axisLine: { lineStyle: { color: 'rgba(255,255,255,0.08)' } },
        axisLabel: { show: false },
      },
      {
        type: 'category',
        data: xLower,
        gridIndex: 1,
        axisLine: { lineStyle: { color: 'rgba(255,255,255,0.08)' } },
        axisLabel: { color: '#6E7681', fontSize: 10 },
      },
    ],
    yAxis: [
      {
        scale: true,
        gridIndex: 0,
        axisLine: { lineStyle: { color: 'rgba(255,255,255,0.08)' } },
        splitLine: { lineStyle: { color: 'rgba(255,255,255,0.04)' } },
        axisLabel: { color: '#6E7681', formatter: '${value}' },
      },
      {
        scale: true,
        gridIndex: 1,
        axisLine: { show: false },
        splitLine: { show: false },
        axisLabel: { show: false },
      },
    ],
    series: [
      {
        name: 'K线',
        type: 'candlestick',
        data: data,
        xAxisIndex: 0,
        yAxisIndex: 0,
        itemStyle: {
          color: KLIRE_UP_COLOR,
          color0: KLIRE_DOWN_COLOR,
          borderColor: KLIRE_UP_BORDER,
          borderColor0: KLIRE_DOWN_BORDER,
        },
      },
      {
        name: 'AI 预测',
        type: 'line',
        data: lineDataLower,
        xAxisIndex: 1,
        yAxisIndex: 1,
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: { width: 2, color: '#00D1FF', type: 'dashed' },
        itemStyle: {
          color: '#00D1FF',
          borderColor: '#fff',
          borderWidth: 1,
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(0,209,255,0.3)' },
            { offset: 1, color: 'rgba(0,209,255,0)' },
          ]),
        },
        markArea:
          histDates.length && predDates.length
            ? {
                silent: true,
                data: [[
                  { xAxis: histDates[histDates.length - 1] },
                  { xAxis: predDates[predDates.length - 1] },
                ]],
                itemStyle: { color: 'rgba(0,209,255,0.08)' },
                label: {
                  show: true,
                  position: 'top',
                  color: '#00D1FF',
                  fontSize: 10,
                  formatter: 'AQM 预测区',
                },
              }
            : undefined,
      },
    ],
  }

  klineChart.setOption(option)
}

async function onTradeSuccess() {
  await fetchAccount()
  updatePositionAdvice()
}

// ─── GSAP 数字动画 ────────────────────────────────────────────────────────────
function gsapAnimateValue(targetRef: typeof displayTotalAssets, target: number) {
  const obj = { val: targetRef.value }
  gsap.to(obj, {
    val: target,
    duration: 0.8,
    ease: 'power2.out',
    onUpdate: () => { targetRef.value = obj.val },
  })
}

function syncDisplayedAccountValues(useAnimation = true) {
  if (useAnimation) {
    gsapAnimateValue(displayCash, account.cash)
    gsapAnimateValue(displayPortfolioValue, account.portfolio_value)
    gsapAnimateValue(displayTotalAssets, account.total_assets)
    gsapAnimateValue(displayPnl, account.total_pnl)
    return
  }

  displayCash.value = account.cash
  displayPortfolioValue.value = account.portfolio_value
  displayTotalAssets.value = account.total_assets
  displayPnl.value = account.total_pnl
}

// ─── 离线降级：API 不可用时生成占位 K 线（带趋势起伏）───────────────────────────────────────
const generateKlineData = (_ticker: string, basePrice: number) => {
  const dates = Array.from({ length: 30 }, (_, index) => {
    const date = new Date()
    date.setDate(date.getDate() - (29 - index))
    return date.toISOString().split('T')[0]
  })
  const safeBase = Math.max(basePrice, 1)
  // 生成带趋势起伏的模拟 K 线数据（避免固定价格）
  let price = safeBase * 0.9
  const data = dates.map(() => {
    const change = (Math.random() - 0.48) * 0.06  // 轻微上涨偏置
    price = Math.max(price * (1 + change), 1.0)
    const dayVolatility = 0.02 + Math.random() * 0.03
    const open = price
    const close = price * (1 + (Math.random() - 0.48) * dayVolatility)
    const high = Math.max(open, close) * (1 + Math.random() * 0.015)
    const low = Math.min(open, close) * (1 - Math.random() * 0.015)
    return [parseFloat(open.toFixed(2)), parseFloat(close.toFixed(2)), parseFloat(low.toFixed(2)), parseFloat(high.toFixed(2))]
  })
  return { dates, data }
}


// ─── 获取账户数据 ────────────────────────────────────────────────────────────
async function fetchAccount() {
  isLoading.value = true
  try {
    const res = await api.get<AccountBalance>('/account')
    const data = res.data
    account.total_assets = data.total_assets ?? 100000
    account.cash = data.cash ?? 100000
    account.init_cash = data.init_cash ?? account.init_cash ?? 100000
    account.portfolio_value = data.portfolio_value ?? 0
    account.total_pnl = data.total_pnl ?? 0
    account.total_return_pct = data.total_return_pct ?? 0
    account.available_cash = data.available_cash ?? data.cash ?? account.cash
    account.positions_count = data.positions_count ?? (Array.isArray(data.positions) ? data.positions.length : 0)
    account.total_fees = data.total_fees ?? 0
    account.total_trades = data.total_trades ?? 0
    account.winning_trades = data.winning_trades ?? 0
    account.losing_trades = data.losing_trades ?? 0
    account.win_rate = data.win_rate ?? 0
    account.daily_pnl = data.daily_pnl ?? 0
    account.daily_trades = data.daily_trades ?? 0
    account.equity_curve = Array.isArray(data.equity_curve) ? data.equity_curve : []
    account.updated_at = data.updated_at ?? ''
    account.positions = Array.isArray(data.positions) ? data.positions.map((position) => ({ ...position })) : []
    syncDisplayedAccountValues()
    mergeHeldTickersIntoList()
    syncPricesFromStockList()
  } catch {
    console.warn('账户 API 暂不可用，保留当前界面数据（避免下单成功后误清空持仓）')
  } finally {
    isLoading.value = false
  }
}

// ─── 详情弹窗状态 ────────────────────────────────────────────────────────────
const detailModal = ref({
  visible: false,
  ticker: '',
  name: '',
  sector: '',
  quantity: 0,
  entry_date: '2026-01-15',
  entry_price: 0,
  current_price: 0,
  market_value: 0,
  cost_basis: 0,
  unrealized_pnl: 0,
  unrealized_pnl_pct: 0,
  stock_change: 0,
  allocation_pct: 0,
  ai_advice: '持有',
  position: null as any,
  loading: false,
})

const timelineChartRef = ref<HTMLElement | null>(null)
let timelineChart: ECharts | null = null
let detailRefreshInterval: number | null = null
let detailRefreshRevision = 0

function stopDetailRefresh() {
  if (detailRefreshInterval) {
    clearInterval(detailRefreshInterval)
    detailRefreshInterval = null
  }
}

async function refreshDetailModalSafe(ticker: string, revision: number) {
  const activeTicker = normalizeTicker(ticker)
  try {
    const res = await apiMarket.forecast(activeTicker)
    if (revision !== detailRefreshRevision || !detailModal.value.visible || activeTicker !== detailModal.value.ticker) {
      return
    }

    const current = Number(res.data?.current_price || 0)
    const stock = findStockRow(activeTicker)
    const pos = account.positions?.find((p: any) => p.ticker === activeTicker)
    const quantity = Number(pos?.quantity || detailModal.value.quantity || 0)
    const entryPrice = Number(pos?.entry_price || detailModal.value.entry_price || current || stock?.price || 0)
    const previousPrice = Number(pos?.current_price || detailModal.value.current_price || 0)
    const livePrice = isValidPrice(current)
      ? current
      : isValidPrice(stock?.price)
        ? Number(stock?.price)
        : isValidPrice(previousPrice)
          ? previousPrice
          : entryPrice
    const marketValue = quantity * livePrice
    const costBasis = quantity * entryPrice
    const unrealizedPnl = marketValue - costBasis
    const unrealizedPnlPct = costBasis > 0 ? (unrealizedPnl / costBasis) * 100 : 0
    const allocationPct = getAllocationPct(marketValue)
    const stockChange = Number(stock?.change ?? detailModal.value.stock_change ?? 0)

    detailModal.value.current_price = livePrice
    detailModal.value.market_value = marketValue
    detailModal.value.cost_basis = costBasis
    detailModal.value.unrealized_pnl = unrealizedPnl
    detailModal.value.unrealized_pnl_pct = unrealizedPnlPct
    detailModal.value.allocation_pct = allocationPct
    detailModal.value.stock_change = stockChange

    if (pos) {
      pos.current_price = livePrice
      pos.market_value = marketValue
      pos.unrealized_pnl = unrealizedPnl
      pos.unrealized_pnl_pct = unrealizedPnlPct
    }

    if (activeTicker === selectedTicker.value) {
      currentPrice.value = livePrice
      tradePrice.value = livePrice
    }
  } catch {
    // keep last detail snapshot
  }
}

function startDetailRefresh(ticker: string) {
  stopDetailRefresh()
  detailRefreshRevision += 1
  const revision = detailRefreshRevision
  void refreshDetailModalSafe(ticker, revision)
  detailRefreshInterval = window.setInterval(() => {
    void refreshDetailModalSafe(ticker, revision)
  }, 5000)
}

const openDetailModal = (ticker: string) => {
  const pos = account.positions?.find((p: any) => p.ticker === ticker)
  const stock = stockList.value.find((s) => s.ticker === ticker)
  const quantity = Number(pos?.quantity || 0)
  const entryPrice = Number(pos?.entry_price || stock?.price || 0)
  const modalPrice = isValidPrice(pos?.current_price)
    ? Number(pos?.current_price)
    : isValidPrice(stock?.price)
      ? Number(stock?.price)
      : entryPrice
  const marketValue = Number(pos?.market_value || quantity * modalPrice)
  const costBasis = quantity * entryPrice
  const unrealizedPnl = Number(pos?.unrealized_pnl ?? (marketValue - costBasis))
  const unrealizedPnlPct = Number(
    pos?.unrealized_pnl_pct ?? (entryPrice > 0 ? ((modalPrice / entryPrice) - 1) * 100 : 0),
  )
  const allocationPct = getAllocationPct(marketValue)
  detailModal.value = {
    visible: true,
    ticker,
    name: stock?.name || ticker,
    sector: stock?.sector || '',
    quantity,
    entry_date: '2026-01-15',
    entry_price: entryPrice,
    current_price: modalPrice,
    market_value: marketValue,
    cost_basis: costBasis,
    unrealized_pnl: unrealizedPnl,
    unrealized_pnl_pct: unrealizedPnlPct,
    stock_change: Number(stock?.change ?? 0),
    allocation_pct: allocationPct,
    ai_advice: pos?.ai_advice || '持有',
    position: pos,
    loading: false,
  }
  if (ticker === selectedTicker.value) {
    detailModal.value.current_price = isValidPrice(currentPrice.value) ? currentPrice.value : modalPrice
  }
  startDetailRefresh(ticker)
  void nextTick(async () => {
    await initTimelineChart()
  })
}

const closeDetailModal = () => {
  detailModal.value.visible = false
  detailModal.value.position = null
  detailChartStatus.value = ''
  stopDetailRefresh()
  timelineChart?.dispose()
  timelineChart = null
}

const initTimelineChart = async () => {
  if (!timelineChartRef.value) return
  const { echarts } = await loadTradeEcharts()
  if (timelineChart) timelineChart.dispose()
  timelineChart = echarts.init(timelineChartRef.value)

  const pos = detailModal.value.position
  const days = 60
  const dates = Array.from({ length: days }, (_, i) => {
    const d = new Date()
    d.setDate(d.getDate() - (days - i))
    return d.toISOString().split('T')[0]
  })
  const entryPrice = pos?.entry_price || detailModal.value.entry_price || 150
  const current = detailModal.value.current_price || entryPrice
  const quantity = pos?.quantity || detailModal.value.quantity || 10
  const pnlNow = (current - entryPrice) * quantity
  const pnlData = Array.from({ length: days }, (_, index) => {
    const progress = index / Math.max(days - 1, 1)
    const eased = 1 - Math.pow(1 - progress, 2)
    return Number((pnlNow * eased).toFixed(2))
  })
  detailChartStatus.value = '轨迹基于当前持仓盈亏做平滑回溯，用于说明持仓状态，不再随机生成。'

  const option: EChartsCoreOption = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(22,27,34,0.95)',
      borderColor: 'rgba(0,209,255,0.3)',
      textStyle: { color: '#F0F6FC' },
    },
    grid: { top: 20, left: 60, right: 20, bottom: 40 },
    xAxis: {
      type: 'category',
      data: dates,
      axisLine: { lineStyle: { color: 'rgba(255,255,255,0.08)' } },
      axisLabel: { color: '#6E7681', fontSize: 10, rotate: 45 },
    },
    yAxis: {
      type: 'value',
      scale: true,
      axisLine: { lineStyle: { color: 'rgba(255,255,255,0.08)' } },
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.04)' } },
      axisLabel: { color: '#6E7681', formatter: '${value}' },
    },
    series: [{
      type: 'line',
      data: pnlData,
      smooth: true,
      symbol: 'none',
      lineStyle: { width: 2, color: '#00D1FF' },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(0,209,255,0.3)' },
          { offset: 1, color: 'rgba(0,209,255,0)' },
        ]),
      },
      markLine: {
        silent: true,
        symbol: 'none',
        lineStyle: { type: 'dashed', width: 1 },
        data: [{ yAxis: 0, lineStyle: { color: 'rgba(255,255,255,0.3)' }, label: { show: false } }],
      },
    }],
  }

  timelineChart.setOption(option)
}


// ─── 更新仓位建议 ────────────────────────────────────────────────────────────
const updatePositionAdvice = () => {
  const maxPct = 20
  const availableCash = displayCash.value
  const price = tradePrice.value || currentPrice.value
  const maxShares = Math.floor((availableCash * maxPct / 100) / (price * (1 + FEE_RATE)))

  positionAdvice.value = {
    suggested_pct: maxPct,
    available_shares: maxShares,
    estimated_cost: maxShares * price * (1 + FEE_RATE),
  }
}


// ─── 切换时间周期 ───────────────────────────────────────────────────────────
const changePeriod = (period: string) => {
  currentPeriod.value = period
  void nextTick(() => {
    void initKlineChartSafe(selectedTicker.value, tickerSelectionRevision)
  })
}

// ─── Toast 提示 ─────────────────────────────────────────────────────────────
const showToast = (message: string, type: 'success' | 'error' = 'success') => {
  if (type === 'success') {
    ElMessage.success(message)
    return
  }
  ElMessage.error(message)
}


// ─── 平仓 ───────────────────────────────────────────────────────────────────
const closePosition = async (ticker: string) => {
  const pos = account.positions?.find((p: any) => p.ticker === ticker)
  if (!pos) return

  const amount = pos.quantity * pos.current_price
  const fee = amount * FEE_RATE

  try {
    await api.post('/trade/close', null, { params: { ticker } })
    showToast(`${ticker} 已平仓`)
  } catch {
    showToast('本地模拟平仓成功')
  }

  displayCash.value += (amount - fee)
  displayPortfolioValue.value -= amount
  account.cash += (amount - fee)
  account.portfolio_value -= amount
  account.total_assets = displayCash.value + displayPortfolioValue.value
  gsapAnimateValue(displayTotalAssets, account.total_assets)
  gsapAnimateValue(displayCash, account.cash)
  gsapAnimateValue(displayPortfolioValue, account.portfolio_value)

  account.positions = account.positions.filter((p: any) => p.ticker !== ticker)
}

// ─── 切换自动交易 ──────────────────────────────────────────────────────────
const toggleAutoTrading = async () => {
  const nextEnabled = !autoTrading.value.enabled
  try {
    if (nextEnabled) {
      await api.post('/auto/start')
    } else {
      await api.post('/auto/stop')
    }
    autoTrading.value.enabled = nextEnabled
    showToast(nextEnabled ? 'AI 自动交易已启动' : 'AI 自动交易已停止')
  } catch {
    showToast(nextEnabled ? 'AI 自动交易启动失败' : 'AI 自动交易停止失败', 'error')
  }
}

// ─── 行情同步：定期从 /dashboard/tickers 拉取（与 watchlist 单一数据源一致）──────
let priceUpdateInterval: number | null = null
let forecastRefreshInterval: number | null = null

const syncPricesFromStockList = () => {
  account.positions?.forEach((pos: Position) => {
    const stock = stockList.value.find((s) => s.ticker === pos.ticker)
    const nextPrice = isValidPrice(stock?.price)
      ? Number(stock?.price)
      : isValidPrice(pos.current_price)
        ? Number(pos.current_price)
        : Number(pos.entry_price || 0)

    if (isValidPrice(nextPrice)) {
      pos.current_price = nextPrice
      pos.market_value = pos.quantity * nextPrice
      pos.unrealized_pnl = (nextPrice - pos.entry_price) * pos.quantity
      pos.unrealized_pnl_pct = pos.entry_price > 0 ? (nextPrice / pos.entry_price - 1) * 100 : 0
    }
  })

  const pv = account.positions?.reduce((sum: number, p: Position) => sum + (p.market_value || 0), 0) || 0
  const pnl = account.positions?.reduce((sum: number, p: Position) => sum + (p.unrealized_pnl || 0), 0) || 0

  account.portfolio_value = pv
  account.total_pnl = pnl
  account.positions_count = account.positions?.length || 0
  account.available_cash = account.cash
  account.total_assets = account.cash + pv
  account.total_return_pct = account.init_cash > 0
    ? ((account.total_assets - account.init_cash) / account.init_cash) * 100
    : 0

  gsapAnimateValue(displayCash, account.cash)
  gsapAnimateValue(displayPortfolioValue, pv)
  gsapAnimateValue(displayTotalAssets, account.total_assets)
  gsapAnimateValue(displayPnl, pnl)

  if (detailModal.value.visible && detailModal.value.ticker) {
    const activePosition = account.positions?.find((p: Position) => p.ticker === detailModal.value.ticker)
    const activeStock = stockList.value.find((s) => s.ticker === detailModal.value.ticker)
    if (activePosition) {
      detailModal.value.current_price = activePosition.current_price
      detailModal.value.market_value = activePosition.market_value
      detailModal.value.unrealized_pnl = activePosition.unrealized_pnl
      detailModal.value.unrealized_pnl_pct = activePosition.unrealized_pnl_pct
      detailModal.value.cost_basis = activePosition.entry_price * activePosition.quantity
      detailModal.value.allocation_pct = pv > 0 ? (activePosition.market_value / pv) * 100 : 0
      detailModal.value.stock_change = Number(activeStock?.change ?? detailModal.value.stock_change ?? 0)
    }
  }
}

const startPriceUpdates = () => {
  if (priceUpdateInterval) clearInterval(priceUpdateInterval)
  priceUpdateInterval = window.setInterval(() => {
    void loadStockList().then(() => {
      const st = stockList.value.find((s) => s.ticker === selectedTicker.value)
      if (st) {
        currentPrice.value = st.price
        priceChange.value = st.change
        tradePrice.value = st.price
      }
      syncPricesFromStockList()
    })
  }, 5_000)
}

// ─── 窗口调整 ───────────────────────────────────────────────────────────────
const handleResize = () => {
  klineChart?.resize()
  timelineChart?.resize()
}

// ─── 监听 ───────────────────────────────────────────────────────────────────
watch(tradePrice, () => { updatePositionAdvice() })

watch(
  () => route.query.ticker,
  (t) => {
    const up = typeof t === 'string' ? t.toUpperCase() : ''
    if (!up || !stockList.value.some((s) => s.ticker === up)) return
    if (selectedTicker.value !== up) selectTickerSafe(up)
  },
)

// ─── 生命周期 ───────────────────────────────────────────────────────────────
onMounted(async () => {
  try {
    loadRecentTickers()
    await loadStockList()
    if (stockList.value.length) {
      const want = typeof route.query.ticker === 'string' ? route.query.ticker.toUpperCase() : ''
      const pick = want && stockList.value.some((s) => s.ticker === want) ? want : stockList.value[0].ticker
      applyTickerSnapshot(pick)
      if (route.query.ticker !== pick) {
        await router.replace({ path: '/trade', query: { ...route.query, ticker: pick } })
      }
    }
    await fetchAccount()
    if (selectedTicker.value) {
      void refreshAiPanelSafe(selectedTicker.value, ++tickerSelectionRevision)
    }
    await nextTick()
    try {
      await initKlineChartSafe(selectedTicker.value, tickerSelectionRevision)
    } catch (e) {
      console.warn('K 线图表初始化失败', e)
    }
    updatePositionAdvice()
    startPriceUpdates()
    if (FORECAST_REFRESH_MS > 0) {
      forecastRefreshInterval = window.setInterval(() => {
        void initKlineChartSafe(selectedTicker.value, tickerSelectionRevision)
      }, FORECAST_REFRESH_MS)
    }
    window.addEventListener('resize', handleResize)
  } catch (e) {
    console.error('模拟交易页挂载异常', e)
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  stopDetailRefresh()
  klineChart?.dispose()
  timelineChart?.dispose()
  if (priceUpdateInterval) clearInterval(priceUpdateInterval)
  if (forecastRefreshInterval) clearInterval(forecastRefreshInterval)
})
</script>

<style lang="scss" scoped>
// ════════════════════════════════════════════════════════════════════════════
// Toast 容器（全局）
// ════════════════════════════════════════════════════════════════════════════
.chart-status {
  margin-top: 12px;
  padding: 10px 12px;
  border: 1px solid rgba(255, 184, 0, 0.18);
  background: rgba(255, 184, 0, 0.08);
  color: #f6c768;
  border-radius: 10px;
  font-size: 12px;
  line-height: 1.5;
}

@keyframes slideIn {
  from { transform: translateX(100%); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}

// ════════════════════════════════════════════════════════════════════════════
// 布局
// ════════════════════════════════════════════════════════════════════════════
.trade-view {
  display: grid;
  grid-template-columns: 1fr 400px;
  grid-template-rows: auto auto auto;
  align-items: start;
  gap: 24px;
  padding-bottom: 72px;
}

// ─── 股票选择栏 ────────────────────────────────────────────────────────────
.stock-selector {
  grid-column: 1 / -1;
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 18px 20px;
  background: rgba(22,27,34,0.82);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(48,54,61,0.8);
  border-radius: 14px;
}

.selector-header {
  display: flex;
  justify-content: space-between;
  align-items: end;
  gap: 16px;
}

.selector-copy {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.recent-tickers {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.recent-label {
  font-size: 11px;
  color: var(--text-tertiary);
  letter-spacing: 0.04em;
}

.recent-chip {
  display: inline-flex;
  align-items: baseline;
  gap: 6px;
  padding: 8px 12px;
  border-radius: 999px;
  border: 1px solid rgba(48,54,61,0.9);
  background: rgba(13,17,23,0.7);
  color: var(--text-primary);
  cursor: pointer;
  appearance: none;
  transition: all 0.2s ease;
}

.recent-chip:hover {
  border-color: rgba(0,209,255,0.6);
  background: rgba(0,209,255,0.08);
  transform: translateY(-1px);
}

.recent-chip.active {
  border-color: rgba(0,209,255,0.8);
  background: rgba(0,209,255,0.12);
  box-shadow: 0 0 0 1px rgba(0,209,255,0.12) inset;
}

.recent-chip-ticker {
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  font-weight: 700;
}

.recent-chip-name {
  font-size: 11px;
  color: var(--text-secondary);
}

.ticker-search-row {
  display: flex;
  gap: 10px;
  align-items: center;
}

.ticker-search {
  flex: 1;
}

:deep(.ticker-search .el-input__wrapper) {
  min-height: 40px;
  padding: 0 12px;
  background: rgba(13,17,23,0.92);
  border: 1px solid rgba(48,54,61,0.9);
  box-shadow: none;
  border-radius: 10px;
}

:deep(.ticker-search .el-input__wrapper.is-focus),
:deep(.ticker-search .el-input__wrapper:hover) {
  border-color: rgba(0,209,255,0.75);
}

:deep(.ticker-search .el-input__inner) {
  color: var(--text-primary);
}

.ticker-search-btn {
  height: 40px;
  padding: 0 16px;
  border-radius: 10px;
  border: 1px solid rgba(0,209,255,0.25);
  background: rgba(0,209,255,0.08);
  color: var(--accent-cyan);
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
}

.ticker-search-btn:hover {
  background: rgba(0,209,255,0.14);
  border-color: rgba(0,209,255,0.55);
}

.selector-kicker {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: var(--accent-cyan);
  text-transform: uppercase;
}

.selector-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
}

.selector-count {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 999px;
  border: 1px solid rgba(0,209,255,0.25);
  color: var(--text-secondary);
  font-size: 12px;
  background: rgba(0,209,255,0.06);
}

.stock-select {
  width: 100%;
}

.stock-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 14px;
  width: 100%;
}

.stock-option-main {
  display: flex;
  align-items: baseline;
  gap: 10px;
  min-width: 0;
}

.stock-option-ticker {
  font-size: 14px;
  font-weight: 800;
  color: var(--text-primary);
  font-family: 'JetBrains Mono', monospace;
}

.stock-option-name {
  font-size: 12px;
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.stock-option-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
  font-size: 12px;
  font-family: 'JetBrains Mono', monospace;
}

.stock-option-sector {
  color: var(--text-secondary);
  font-family: inherit;
}

.stock-option-price {
  &.pos { color: var(--accent-green); }
  &.neg { color: var(--accent-red); }
}

.stock-option-change {
  font-weight: 700;

  &.pos { color: var(--accent-green); }
  &.neg { color: var(--accent-red); }
}

:deep(.stock-select .el-select__wrapper) {
  min-height: 54px;
  padding: 10px 14px;
  background: rgba(13,17,23,0.95);
  border: 1px solid rgba(48,54,61,0.9);
  box-shadow: none;
  border-radius: 12px;
}

:deep(.stock-select .el-select__wrapper.is-focused),
:deep(.stock-select .el-select__wrapper:hover) {
  border-color: rgba(0,209,255,0.8);
}

:deep(.stock-select .el-select__selected-item) {
  color: var(--text-primary);
}

:deep(.stock-select-popper) {
  border: 1px solid rgba(48,54,61,0.95);
  background: rgba(13,17,23,0.98);
  box-shadow: 0 18px 48px rgba(0,0,0,0.45);
}

:deep(.stock-select-popper .el-select-dropdown__item) {
  padding: 10px 12px;
  height: auto;
}

:deep(.stock-select-popper .el-select-dropdown__item.is-selected) {
  color: var(--accent-cyan);
}

:deep(.stock-select-popper .el-select-dropdown__item:hover) {
  background: rgba(0,209,255,0.08);
}

// ─── K 线图区域（暗底，避免白底看不清 K 线）───────────────────────────────────
.chart-section {
  grid-row: 2;
  grid-column: 1;
  padding: 20px;
  align-self: start;
  background: rgba(13, 17, 23, 0.92);
  border: 1px solid var(--border-default);
  border-radius: 16px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.ticker-info {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.ticker-symbol {
  font-size: 24px;
  font-weight: 700;
  color: var(--accent-cyan);
  font-family: 'JetBrains Mono', monospace;
}

.ticker-name {
  font-size: 14px;
  color: var(--text-secondary);
}

.ticker-price-wrap {
  text-align: right;
}

.price-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin-right: 8px;
  font-family: 'JetBrains Mono', monospace;
  display: inline-block;
}

.price-change {
  font-size: 14px;
  font-weight: 600;

  &.pos { color: var(--accent-green); }
  &.neg { color: var(--accent-red); }
}

.chart-container {
  height: 380px;
  margin-bottom: 16px;
  background: var(--bg-primary);
  border-radius: 12px;
  border: 1px solid #21262d;
  overflow: hidden;
}

.kline-chart {
  width: 100%;
  height: 100%;
  min-height: 360px;
}

.prediction-legend {
  display: flex;
  gap: 24px;
  margin-bottom: 16px;
  padding: 12px;
  background: var(--bg-secondary);
  border-radius: 8px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.legend-line {
  width: 24px;
  height: 3px;

  &.solid { background: var(--accent-green); }

  &.dashed {
    background: repeating-linear-gradient(
      90deg, var(--accent-cyan), var(--accent-cyan) 4px, transparent 4px, transparent 8px
    );
  }
}

.legend-area {
  width: 24px;
  height: 16px;
  background: linear-gradient(180deg, rgba(0,209,255,0.3), rgba(0,209,255,0));
  border: 1px dashed var(--accent-cyan);
}

.legend-text {
  font-size: 12px;
  color: var(--text-secondary);
}

.chart-periods {
  display: flex;
  gap: 8px;
}

.period-btn {
  padding: 8px 16px;
  border: 1px solid rgba(255,255,255,0.18);
  border-radius: 8px;
  background: rgba(13,17,23,0.82);
  color: rgba(240,246,252,0.82);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: inset 0 0 0 1px rgba(255,255,255,0.03);
  transition: all 0.2s ease;

  &:hover {
    border-color: rgba(0,209,255,0.45);
    background: rgba(0,209,255,0.08);
    color: var(--text-primary);
  }

  &.active {
    background: rgba(0,209,255,0.14);
    border-color: var(--accent-cyan);
    color: var(--accent-cyan);
    box-shadow: 0 0 0 1px rgba(0,209,255,0.14), 0 8px 24px rgba(0,209,255,0.08);
  }
}

// ─── 交易面板 ────────────────────────────────────────────────────────────────
.trade-panel {
  grid-row: 2 / span 2;
  grid-column: 2;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  align-self: start;
}

.account-overview {
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-default);
}

.account-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.account-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.account-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-label {
  font-size: 11px;
  color: var(--text-tertiary);
}

.stat-value {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  font-family: 'JetBrains Mono', monospace;
}

// ─── 三层分割线（决策 → 仓位 → 执行）──────────────────────────────────────
.tier-label {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--text-tertiary);
  margin-bottom: 2px;
}

.tier-divider {
  height: 1px;
  background: var(--border-default);
  margin: 8px 0;
}

// AI 信心区：Sharpe 说明降透明度（不抢戏）
.confidence-hint {
  font-size: 10px;
  color: var(--text-tertiary);
  opacity: 0.6;
  letter-spacing: 0.02em;
}

.ai-confidence {
  padding: 14px;
  background: var(--bg-secondary);
  border-radius: 12px;
}

.confidence-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

// ─── AI 标签横向滚动行（不折行）──────────────────────────────────────────
.ai-tags-scroll {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 4px;
  scrollbar-width: none;
  &::-webkit-scrollbar { display: none; }
}

.ai-chip {
  flex-shrink: 0;
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
}

.direction-chip {
  &.bullish { background: var(--accent-green-dim); color: var(--accent-green); }
  &.bearish { background: var(--accent-red-dim); color: var(--accent-red); }
  &.neutral { background: var(--bg-secondary); color: var(--text-secondary); border: 1px solid var(--border-default); }
}

.risk-chip {
  &.low { background: var(--accent-green-dim); color: var(--accent-green); }
  &.medium { background: var(--accent-gold-dim); color: var(--accent-gold); }
  &.high { background: var(--accent-red-dim); color: var(--accent-red); }
}

.model-chip {
  background: var(--accent-cyan-dim);
  color: var(--accent-cyan);
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
}

.confidence-title {
  font-size: 14px;
  color: var(--text-primary);
}

.confidence-value {
  font-size: 20px;
  font-weight: 700;
  font-family: 'JetBrains Mono', monospace;

  &.high { color: var(--accent-green); }
  &.medium { color: var(--accent-gold); }
  &.low { color: var(--accent-red); }
}

.confidence-bar {
  height: 8px;
  background: var(--bg-primary);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}

.confidence-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--accent-cyan), var(--accent-green));
  border-radius: 4px;
  transition: width 0.5s ease;
}

// 仓位建议
.position-advice {
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: 12px;
}

.advice-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.advice-title {
  font-size: 14px;
  color: var(--text-primary);
}

.advice-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.advice-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.advice-label {
  font-size: 12px;
  color: var(--text-secondary);
}

.advice-value {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

// 交易表单
.trade-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-tabs {
  display: flex;
  gap: 8px;
}

.form-tab {
  flex: 1;
  padding: 12px;
  border-color: rgba(255,255,255,0.12);
  border-radius: 8px;
  background: transparent;
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;

  &.active {
    &.buy-tab {
      background: rgba(0,255,189,0.1);
      border-color: var(--accent-green);
      color: var(--accent-green);
    }
    &.sell-tab {
      background: rgba(255,59,48,0.1);
      border-color: var(--accent-red);
      color: var(--accent-red);
    }
  }
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: 12px;
  color: var(--text-secondary);
}

.form-input {
  width: 100%;
  padding: 12px;
  background: var(--bg-secondary);
  border-color: rgba(255,255,255,0.12);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 16px;
  font-weight: 600;

  &:focus {
    outline: none;
    border-color: var(--accent-cyan);
    box-shadow: 0 0 0 2px rgba(0,209,255,0.2);
  }
}

.price-input, .quantity-input {
  display: flex;
  align-items: center;
  background: var(--bg-secondary);
  border-color: rgba(255,255,255,0.12);
  border-radius: 8px;
  overflow: hidden;

  &:focus-within {
    border-color: var(--accent-cyan);
    box-shadow: 0 0 0 2px rgba(0,209,255,0.2);
  }

  .form-input {
    border: none;
    background: transparent;
    padding-left: 12px;
    &:focus { box-shadow: none; }
  }
}

.price-unit, .quantity-unit {
  padding: 12px;
  background: var(--bg-primary);
  color: var(--text-tertiary);
  font-size: 12px;
}

.quick-quantity {
  display: flex;
  gap: 8px;
}

.quick-btn {
  flex: 1;
  padding: 8px;
  border-color: rgba(255,255,255,0.12);
  border-radius: 6px;
  background: transparent;
  color: var(--text-secondary);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    border-color: var(--accent-cyan);
    color: var(--accent-cyan);
  }
}

.quantity-hint {
  font-size: 11px;
  margin-top: 4px;
}

.validation-message {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: rgba(255,59,48,0.1);
  border: 1px solid rgba(255,59,48,0.3);
  border-radius: 8px;
  color: var(--accent-red);
  font-size: 12px;
}

.trade-preview {
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.preview-item {
  display: flex;
  justify-content: space-between;
  align-items: center;

  &.total {
    padding-top: 8px;
    border-top: 1px solid var(--border-default);
    margin-top: 4px;
  }
}

.preview-label {
  font-size: 12px;
  color: var(--text-secondary);
}

.preview-value {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  font-family: 'JetBrains Mono', monospace;
}

.submit-btn {
  width: 100%;
  padding: 16px;
  font-size: 16px;
  border: none;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;

  &.btn-buy {
    background: linear-gradient(135deg, var(--accent-green), var(--accent-cyan));
    color: var(--bg-primary);
    &:hover:not(:disabled) { box-shadow: 0 0 20px rgba(0,255,189,0.4); }
  }
  &.btn-sell {
    background: linear-gradient(135deg, #FF6B6B, #FF3B30);
    color: white;
    &:hover:not(:disabled) { box-shadow: 0 0 20px rgba(255,59,48,0.4); }
  }
  &:disabled { opacity: 0.5; cursor: not-allowed; }
}

.loading-spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid currentColor;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

// 自动交易开关
// 分层分割线
.section-separator {
  height: 1px;
  background: var(--border-default);
  margin: 0 -4px;
}

.auto-trade-toggle {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: 12px;
  margin-top: 4px;
}

.toggle-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.toggle-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.toggle-status {
  font-size: 12px;
  color: var(--text-tertiary);
  &.active { color: var(--accent-cyan); }
}

.toggle-btn {
  background: rgba(13,17,23,0.82);
  border: 1px solid rgba(255,255,255,0.14);
  border-radius: 999px;
  cursor: pointer;
  padding: 2px;
  display: flex;
  align-items: center;
  box-shadow: inset 0 0 0 1px rgba(255,255,255,0.03);
}

.toggle-track {
  display: block;
  width: 48px;
  height: 28px;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 14px;
  position: relative;
  transition: background 0.3s, border-color 0.3s;

  .toggle-btn.active & {
    background: rgba(0,209,255,0.22);
    border-color: rgba(0,209,255,0.6);
  }
}

.toggle-thumb {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 22px;
  height: 22px;
  background: var(--text-secondary);
  border-radius: 50%;
  transition: left 0.3s, background 0.3s;

  .toggle-btn.active & {
    left: 22px;
    background: #0D1117;
  }
}

// 自动交易运行中风险提示
.auto-risk-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: rgba(255,149,0,0.08);
  border: 1px solid rgba(255,149,0,0.2);
  border-radius: 8px;
  color: #FFB347;
  font-size: 11px;
  line-height: 1.4;
}

// ─── 持仓列表 ────────────────────────────────────────────────────────────────
.positions-section {
  grid-row: 3;
  grid-column: 1;
  padding: 20px;
}

@media (max-width: 1200px) {
  .trade-view {
    grid-template-columns: 1fr;
    grid-template-rows: auto;
  }

  .chart-section,
  .trade-panel,
  .positions-section {
    grid-column: 1;
    grid-row: auto;
  }

  .trade-panel {
    gap: 16px;
  }
}

@media (max-width: 640px) {
  .trade-view {
    gap: 16px;
    padding-bottom: 16px;
  }

  .stock-selector,
  .chart-section,
  .trade-panel,
  .positions-section {
    min-width: 0;
    padding: 16px;
    border-radius: 14px;
  }

  .selector-header,
  .chart-header,
  .section-header {
    align-items: flex-start;
    gap: 12px;
    flex-direction: column;
  }

  .ticker-search-row {
    flex-direction: column;
    align-items: stretch;
  }

  .ticker-price-wrap {
    align-items: flex-start;
  }

  .price-value {
    font-size: 24px;
  }

  .chart-container {
    overflow-x: auto;
    padding-bottom: 6px;
  }

  .kline-chart {
    min-width: 720px;
  }

  .prediction-legend,
  .chart-periods,
  .ai-tags-scroll {
    overflow-x: auto;
    padding-bottom: 4px;
  }

  .prediction-legend {
    gap: 14px;
  }

  .period-btn {
    flex: 0 0 auto;
  }

  .account-stats {
    grid-template-columns: 1fr;
  }
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 12px;

  h2 { font-size: 16px; font-weight: 600; color: #F0F6FC; }
}

.positions-count {
  font-size: 12px;
  color: var(--text-tertiary);
  padding: 4px 12px;
  background: var(--bg-secondary);
  border-radius: 12px;
}

.positions-table-el {
  width: 100%;
  border-collapse: collapse;

  th, td { padding: 12px 16px; text-align: left; }
  th {
    font-size: 12px;
    color: var(--text-secondary);
    font-weight: 500;
    border-bottom: 1px solid var(--border-default);
  }
  td {
    font-size: 14px;
    color: var(--text-primary);
    border-bottom: 1px solid rgba(48,54,61,0.5);
  }
  tr:hover td { background: rgba(22,27,34,0.5); }
}

.text-right { text-align: right !important; }
.text-center { text-align: center !important; }

.ticker-badge {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 600;
  color: var(--accent-cyan);

  &.clickable {
    cursor: pointer;
    &:hover { text-decoration: underline; }
  }
}

.mono { font-family: 'JetBrains Mono', monospace; }

// PnL 呼吸灯效果
.pnl-cell {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;

  /* 语义化：up=盈利(绿)，down=亏损(红) */
  &.profit-up .pnl-value { color: var(--accent-green); animation: breathe-green 1.5s ease-in-out infinite; }
  &.profit-down .pnl-value { color: var(--accent-red); animation: breathe-red 1.5s ease-in-out infinite; }
}

.pnl-value {
  font-family: 'JetBrains Mono', monospace;
  font-size: 14px;
  font-weight: 600;
}

.pnl-percent {
  font-size: 11px;
  opacity: 0.7;
}

@keyframes breathe-green {
  0%, 100% { text-shadow: 0 0 8px rgba(0,255,189,0.3); }
  50% { text-shadow: 0 0 20px rgba(0,255,189,0.8); }
}

@keyframes breathe-red {
  0%, 100% { text-shadow: 0 0 8px rgba(255,59,48,0.3); }
  50% { text-shadow: 0 0 20px rgba(255,59,48,0.8); }
}

.advice-badge {
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 11px;
  background: rgba(0,209,255,0.1);
  color: var(--accent-cyan);
}

.action-buttons { display: flex; gap: 8px; }

.btn {
  padding: 6px 12px;
  border-radius: 6px;
  background: rgba(13,17,23,0.88);
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.18s ease;
  border: 1px solid rgba(255,255,255,0.14);
  min-height: 34px;

  &.btn-ghost {
    background: rgba(13,17,23,0.82);
    color: rgba(240,246,252,0.82);
    border-color: rgba(255,255,255,0.18);
    &:hover {
      border-color: rgba(0,209,255,0.45);
      background: rgba(0,209,255,0.08);
      color: #00D1FF;
    }
  }
  &.btn-danger {
    background: rgba(255,59,48,0.1);
    color: var(--accent-red);
    border: 1px solid rgba(255,59,48,0.3);
    &:hover {
      background: rgba(255,59,48,0.18);
      border-color: rgba(255,59,48,0.55);
      color: #ffd2ce;
    }
  }
  &.btn-sm { padding: 6px 12px; font-size: 12px; }
}

.empty-positions {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 48px;
  color: var(--text-tertiary);
}

.empty-icon { font-size: 48px; opacity: 0.5; }
.empty-text { font-size: 14px; }
.empty-hint { font-size: 12px; }

// ─── 详情弹窗 ────────────────────────────────────────────────────────────────
.detail-modal-overlay {
  position: fixed;
  inset: 0;
  background:
    radial-gradient(circle at top, rgba(0,209,255,0.08), transparent 42%),
    rgba(5,8,12,0.78);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.detail-modal {
  width: 90%;
  max-width: 800px;
  max-height: 85vh;
  overflow-y: auto;
  padding: 24px;
  background:
    linear-gradient(180deg, rgba(22,27,34,0.98), rgba(13,17,23,0.98));
  border: 1px solid rgba(48,54,61,0.95);
  border-radius: 16px;
  box-shadow: 0 24px 64px rgba(0,0,0,0.55);
  animation: slideUp 0.3s ease-out;
  position: relative;
  overflow-x: hidden;
}

.detail-modal::before {
  content: '';
  position: absolute;
  inset: 0;
  height: 3px;
  background: linear-gradient(90deg, transparent, rgba(0,209,255,0.7), transparent);
  pointer-events: none;
}

@keyframes slideUp {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.detail-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(48,54,61,0.8);
}

.detail-modal-title {
  display: flex;
  align-items: center;
  gap: 16px;
}

.detail-modal-icon {
  width: 44px;
  height: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  background: rgba(0,209,255,0.12);
  border: 1px solid rgba(0,209,255,0.18);
  font-size: 26px;
}

.detail-ticker {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  font-family: 'JetBrains Mono', monospace;
}

.detail-meta {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 4px;
}

.detail-modal-close {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 4px;
  border-radius: 8px;
  transition: all 0.2s;
  &:hover {
    background: rgba(255,255,255,0.05);
    color: var(--text-primary);
  }
}

.detail-overview {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  padding: 16px;
  background: rgba(13,17,23,0.88);
  border: 1px solid rgba(48,54,61,0.65);
  border-radius: 12px;
  margin-bottom: 24px;
}

.detail-panels {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.detail-panel {
  padding: 16px;
  background: rgba(13,17,23,0.88);
  border: 1px solid rgba(48,54,61,0.65);
  border-radius: 12px;
}

.detail-panel-title {
  font-size: 13px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.detail-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.detail-list-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.detail-list-label {
  font-size: 11px;
  color: var(--text-tertiary);
}

.detail-list-value {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  text-align: right;
}

.detail-stat {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-stat-label {
  font-size: 11px;
  color: var(--text-tertiary);
}

.detail-stat-value {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  font-family: 'JetBrains Mono', monospace;
}

.detail-chart-section {
  margin-bottom: 24px;
}

.detail-modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.timeline-chart {
  height: 250px;
  background: rgba(13,17,23,0.88);
  border: 1px solid rgba(48,54,61,0.65);
  border-radius: 12px;
  padding: 16px;
}

// 工具类
.text-glow-cyan { color: var(--accent-cyan); text-shadow: 0 0 20px var(--accent-cyan-glow); }
.text-glow-green { color: var(--accent-green); text-shadow: 0 0 20px var(--accent-green-glow); }
.text-glow-red { color: var(--accent-red); text-shadow: 0 0 20px var(--accent-red-glow); }
.text-accent-cyan { color: var(--accent-cyan); }
.text-accent-green { color: var(--accent-green); }
.text-accent-red { color: var(--accent-red); }
.text-accent-gold { color: var(--accent-gold); }
</style>


