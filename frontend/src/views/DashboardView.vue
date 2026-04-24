<template>
  <div class="dashboard">
    <!-- ══════════════════════════════════════════════════════════════════════
         资产总览区（权益曲线）
         ══════════════════════════════════════════════════════════════════════ -->
    <section class="equity-section glass-card module-shell module-shell--cyan">
      <div class="equity-header">
        <div class="equity-label">
          <span class="label-icon">&#9670;</span>
          <span>总资产 (USD)</span>
        </div>
        <div class="equity-actions">
          <button class="btn btn-ghost btn-sm" @click="refreshData" :disabled="isLoading">
            <span class="loading-spinner" v-if="isLoading"></span>
            <svg v-else class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
              <path d="M23 4v6h-6"/><path d="M1 20v-6h6"/>
              <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
            </svg>
            <span>刷新</span>
          </button>
        </div>
      </div>

      <div class="equity-value number-roll" ref="totalAssetsRef">
        <span class="currency">$</span>
        <span class="amount text-glow-cyan">{{ displayTotalAssets }}</span>
      </div>

      <div class="equity-change" :class="account.total_pnl >= 0 ? 'positive' : 'negative'">
        <span class="change-icon">{{ account.total_pnl >= 0 ? '&#8593;' : '&#8595;' }}</span>
        <span class="change-value">{{ (account.total_pnl >= 0 ? '+$' : '-$') }}{{ formatNumber(Math.abs(account.total_pnl)) }}</span>
        <span class="change-percent">({{ account.total_return_pct >= 0 ? '+' : '' }}{{ (account.total_return_pct || 0).toFixed(2) }}%)</span>
      </div>

      <!-- 权益曲线图 -->
      <div class="equity-chart" ref="equityChartRef">
        <div v-show="isLoading" class="chart-skeleton">
          <div class="skeleton-chart-bars">
            <div class="skeleton-bar" v-for="i in 12" :key="i" :style="{ height: `${30 + Math.random() * 60}%` }" />
          </div>
        </div>
        <div class="chart-container"></div>
      </div>
      <div v-if="dashboardError" class="dashboard-status error">{{ dashboardError }}</div>
      <div v-else-if="!lastUpdated && !isLoading" class="dashboard-status">暂无可展示的数据，请先启动后端服务。</div>
    </section>

    <!-- ══════════════════════════════════════════════════════════════════════
         指标卡片区（GSAP 数字动画）
         ══════════════════════════════════════════════════════════════════════ -->
    <section class="metrics-section">
      <TransitionGroup name="card-stagger" tag="div" class="metrics-grid">
        <MetricCard
          v-for="(m, index) in metricCards"
          :key="m.label"
          class="fade-in-up"
          :style="{ animationDelay: `${index * 0.1}s` }"
          :label="m.label"
          :value="m.displayValue"
          :value-class="m.valueClass"
          :icon-path="m.iconPath"
          :accent="toMetricAccent(m.iconClass)"
        />
      </TransitionGroup>
    </section>

    <!-- ══════════════════════════════════════════════════════════════════════
         AI 股票推荐区
         ══════════════════════════════════════════════════════════════════════ -->
    <section class="predictions-section glass-card module-shell module-shell--green">
      <div class="section-header">
        <div class="section-title">
          <span class="title-icon">&#63720;</span>
          <h2>AI 股票推荐</h2>
        </div>
        <div class="section-meta status-rail">
          <span class="meta-label">AlphaT-2026 模型</span>
          <span class="meta-divider">|</span>
          <span class="meta-time">更新于 {{ lastUpdated }}</span>
        </div>
      </div>

      <div class="predictions-table data-panel">
        <el-table :data="predictions" stripe highlight-current-row>
          <el-table-column label="排名" width="60" align="center">
            <template #default="{ $index }">
              <span class="rank-badge" :class="{ top3: $index < 3 }">{{ $index + 1 }}</span>
            </template>
          </el-table-column>

          <el-table-column prop="ticker" label="股票代码" width="100">
            <template #default="{ row }">
              <span class="ticker-badge">{{ row.ticker }}</span>
            </template>
          </el-table-column>

          <el-table-column prop="name" label="公司名称" min-width="150"/>

          <el-table-column prop="score" label="AI 评分" width="120" align="center">
            <template #default="{ row }">
              <span class="score-value" :class="{ positive: row.score > 0, negative: row.score < 0 }">
                {{ row.score >= 0 ? '+' : '' }}{{ row.score.toFixed(4) }}
              </span>
            </template>
          </el-table-column>

          <el-table-column prop="confidence" label="置信度" width="110" align="center">
            <template #default="{ row }">
              <div class="confidence-bar-wrap">
                <div class="confidence-bar">
                  <div class="confidence-fill" :style="{ width: Math.min(row.confidence, 100) + '%' }"></div>
                </div>
                <span class="confidence-text">{{ row.confidence.toFixed(0) }}%</span>
              </div>
            </template>
          </el-table-column>

          <el-table-column prop="direction" label="方向" width="90" align="center">
            <template #default="{ row }">
              <span class="direction-badge" :class="row.direction">
                {{ row.direction === 'bullish' ? '&#128200; 多' : row.direction === 'bearish' ? '&#128201; 空' : '&#8212; 中' }}
              </span>
            </template>
          </el-table-column>

          <el-table-column prop="change_pct" label="涨跌幅" width="100" align="center">
            <template #default="{ row }">
              <span class="change-value-cell" :class="{ positive: row.change_pct >= 0, negative: row.change_pct < 0 }">
                {{ row.change_pct >= 0 ? '+' : '' }}{{ row.change_pct.toFixed(2) }}%
              </span>
            </template>
          </el-table-column>

          <el-table-column prop="ai_advice" label="AI 建议" width="100" align="center">
            <template #default="{ row }">
              <span class="advice-badge">{{ row.ai_advice }}</span>
            </template>
          </el-table-column>

          <el-table-column label="操作" width="130" align="center">
            <template #default="{ row }">
              <div class="action-buttons">
                <button class="btn btn-sm btn-success" @click="handleBuy(row)">买入</button>
                <button class="btn btn-sm btn-ghost" @click="handleDetail(row)">详情</button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </section>

    <!-- ══════════════════════════════════════════════════════════════════════
         特征重要性
         ══════════════════════════════════════════════════════════════════════ -->
    <section class="features-section glass-card module-shell module-shell--gold">
      <div class="section-header">
        <div class="section-title">
          <span class="title-icon">&#128202;</span>
          <h2>特征重要性</h2>
        </div>
        <div class="section-meta status-rail">
          <span class="meta-label">AlphaTransformer Cross-Asset Attention</span>
        </div>
      </div>

      <div class="features-content">
        <div class="features-chart">
          <div ref="featuresChartRef" class="chart-container"></div>
        </div>
        <div class="features-list">
          <div class="feature-item" v-for="(feat, idx) in featureImportance" :key="feat.name">
            <div class="feature-rank" :class="{ top: idx < 3 }">{{ idx + 1 }}</div>
            <div class="feature-info">
              <span class="feature-name">{{ feat.name }}</span>
              <span class="feature-desc">{{ feat.description }}</span>
            </div>
            <div class="feature-bar-wrap">
              <div class="feature-bar">
                <div class="bar-fill" :style="{ width: (feat.importance * 100) + '%' }"></div>
              </div>
              <span class="feature-value">{{ (feat.importance * 100).toFixed(1) }}%</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import ElMessage from 'element-plus/es/components/message/index'
import type { ECharts, EChartsCoreOption } from 'echarts/core'
import { api } from '../api'
import gsap from 'gsap'
import type { EquityCurve } from '../types/api'
import { formatNumber as fmtNum } from '../utils/formatters'
import MetricCard from '../components/ui/MetricCard.vue'

type DashboardEchartsModule = typeof import('../lib/echarts/dashboard')

let dashboardEchartsPromise: Promise<DashboardEchartsModule> | null = null

function loadDashboardEcharts() {
  dashboardEchartsPromise ??= import('../lib/echarts/dashboard')
  return dashboardEchartsPromise
}

const router = useRouter()

type MetricAccent = 'cyan' | 'green' | 'gold' | 'red'

function toMetricAccent(value: string): MetricAccent {
  return ['cyan', 'green', 'gold', 'red'].includes(value) ? value as MetricAccent : 'cyan'
}

// ─── Refs ───────────────────────────────────────────────────────────────────
const equityChartRef = ref<HTMLElement | null>(null)
const featuresChartRef = ref<HTMLElement | null>(null)
let equityChart: ECharts | null = null
let featuresChart: ECharts | null = null
let gsapTween: gsap.core.Tween | null = null
let isActive = true

// ─── State ───────────────────────────────────────────────────────────────────
const isLoading = ref(false)
const lastUpdated = ref('')
const dashboardError = ref('')

const account = reactive({
  total_assets: 100000,
  cash: 100000,
  init_cash: 100000,
  portfolio_value: 0,
  total_pnl: 0,
  total_return_pct: 0,
  positions: [] as any[],
})

const predictions = ref<any[]>([])
const featureImportance = ref<any[]>([])

// Animated display value
const displayTotalAssets = ref('100,000.00')

// ─── Metric Cards ─────────────────────────────────────────────────────────────
const metricCards = computed(() => {
  const m = account
  return [
    {
      label: '可用资金',
      iconClass: 'cyan',
      iconPath: 'M12 1v22M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6',
      valueClass: '',
      displayValue: '$' + formatNumber(m.cash),
    },
    {
      label: '持仓市值',
      iconClass: 'gold',
      iconPath: 'M2 7l10-5 10 5-10 5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5',
      valueClass: '',
      displayValue: '$' + formatNumber(m.portfolio_value),
    },
    {
      label: '累计收益',
      iconClass: m.total_pnl >= 0 ? 'green' : 'red',
      iconPath: 'M23 6l-13.5 13.5L2 18M17 6h6v6',
      valueClass: m.total_pnl >= 0 ? 'text-glow-green' : 'text-glow-red',
      displayValue: (m.total_pnl >= 0 ? '+$' : '-$') + formatNumber(Math.abs(m.total_pnl)),
    },
    {
      label: '胜率',
      iconClass: 'green',
      iconPath: 'M22 11.08V12a10 10 0 1 1-5.93-9.14M22 4L12 14.01l-3-3',
      valueClass: 'text-glow-green',
      displayValue: (account as any).win_rate ? (account as any).win_rate.toFixed(1) + '%' : '—',
    },
  ]
})

// ─── Formatters ───────────────────────────────────────────────────────────────
const formatNumber = (num: number) => fmtNum(num, { minimumFractionDigits: 2, maximumFractionDigits: 2 })

// ─── GSAP 数字滚动 ────────────────────────────────────────────────────────────
function animateTo(target: number) {
  const obj = { val: parseFloat(displayTotalAssets.value.replace(/,/g, '')) || 100000 }
  if (gsapTween) gsapTween.kill()
  gsapTween = gsap.to(obj, {
    val: target,
    duration: 0.8,
    ease: 'power2.out',
    onUpdate: () => {
      displayTotalAssets.value = formatNumber(obj.val)
    },
  })
}

// ─── 权益曲线图 ───────────────────────────────────────────────────────────────
async function initEquityChart(curve: EquityCurve) {
  const el = equityChartRef.value
  const container = el?.querySelector('.chart-container') as HTMLElement | null
  if (!container) {
    console.warn('[initEquityChart] container not found')
    return
  }

  const { echarts } = await loadDashboardEcharts()
  if (!isActive) return
  if (equityChart) equityChart.dispose()
  equityChart = echarts.init(container)

  const dates = curve?.dates || []
  const strategy = curve?.strategy_equity || []
  const benchmark = curve?.benchmark_equity || []

  const option: EChartsCoreOption = {
    backgroundColor: 'transparent',
    grid: { top: 20, right: 20, bottom: 40, left: 70 },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(22,27,34,0.95)',
      borderColor: 'rgba(0,209,255,0.3)',
      textStyle: { color: '#F0F6FC' },
      formatter: (params: any) => {
        const s = params.find((p: any) => p.seriesName === '策略权益')
        const b = params.find((p: any) => p.seriesName === '基准')
        if (!s) return ''
        const excess = s.value - b.value
        return `<div style="font-size:12px">
          <div style="color:#8B949E;margin-bottom:4px">${s.axisValue}</div>
          <div style="color:#00D1FF">策略权益: $${formatNumber(s.value)}</div>
          <div style="color:#FFD700">基准: $${formatNumber(b?.value || 0)}</div>
          <div style="color:${excess >= 0 ? '#00FFBD' : '#FF3B30'}">超额: ${excess >= 0 ? '+' : ''}$${formatNumber(Math.abs(excess))}</div>
        </div>`
      },
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLine: { lineStyle: { color: 'rgba(255,255,255,0.08)' } },
      axisLabel: { color: '#6E7681', fontSize: 10 },
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } },
      axisLabel: {
        color: '#6E7681',
        fontSize: 10,
        formatter: (v: number) => '$' + (v / 1000).toFixed(0) + 'K',
      },
    },
    series: [
      {
        name: '策略权益',
        type: 'line',
        data: strategy,
        smooth: true,
        symbol: 'none',
        lineStyle: { width: 3, color: '#00D1FF' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(0,209,255,0.3)' },
            { offset: 1, color: 'rgba(0,209,255,0)' },
          ]),
        },
      },
      {
        name: '基准',
        type: 'line',
        data: benchmark,
        smooth: true,
        symbol: 'none',
        lineStyle: { width: 2, color: '#FFD700', type: 'dashed' },
      },
    ],
  }

  equityChart.setOption(option)
}

// ─── 特征重要性图 ─────────────────────────────────────────────────────────────
async function initFeaturesChart() {
  if (!featuresChartRef.value) return
  const { echarts } = await loadDashboardEcharts()
  if (!isActive) return
  if (featuresChart) featuresChart.dispose()
  featuresChart = echarts.init(featuresChartRef.value)

  const feats = [...featureImportance.value].sort((a, b) => b.importance - a.importance).slice(0, 6)

  const option: EChartsCoreOption = {
    backgroundColor: 'transparent',
    grid: { top: 10, right: 80, bottom: 20, left: 10 },
    xAxis: {
      type: 'value',
      axisLine: { show: false },
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } },
      axisLabel: { color: '#6E7681', fontSize: 10, formatter: '{c}%' },
    },
    yAxis: {
      type: 'category',
      data: feats.map(f => f.name).reverse(),
      axisLine: { show: false },
      axisLabel: { color: '#8B949E', fontSize: 12 },
    },
    series: [{
      type: 'bar',
      data: feats.map(f => (f.importance * 100).toFixed(1)).reverse(),
      barWidth: 16,
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
          { offset: 0, color: '#00D1FF' },
          { offset: 1, color: '#00FFBD' },
        ]),
        borderRadius: [0, 6, 6, 0],
      },
      label: {
        show: true,
        position: 'right',
        color: '#00D1FF',
        fontSize: 12,
        fontWeight: 600,
        formatter: '{c}%',
      },
    }],
  }

  featuresChart.setOption(option)
}

// ─── 数据获取 ──────────────────────────────────────────────────────────────────
async function fetchDashboard() {
  isLoading.value = true
  dashboardError.value = ''
  try {
    const res = await api.get('/dashboard/full')
    const data = res.data

    // 更新 account
    const acc = data.account || {}
    account.total_assets = acc.total_assets ?? 100000
    account.cash = acc.cash ?? 100000
    account.init_cash = acc.init_cash ?? 100000
    account.portfolio_value = acc.portfolio_value ?? 0
    account.total_pnl = acc.total_pnl ?? 0
    account.total_return_pct = acc.total_return_pct ?? 0
    account.positions = acc.positions || []

    // GSAP 动画更新总资产
    animateTo(account.total_assets)

    // 更新预测
    predictions.value = data.predictions || []

    // 更新特征重要性
    featureImportance.value = data.feature_importance || []

    // 权益曲线
    if (data.equity_curve) {
      await nextTick()
      await initEquityChart(data.equity_curve)
    }

    // 特征重要性图
    if (featureImportance.value.length > 0) {
      await nextTick()
      await initFeaturesChart()
    }

    lastUpdated.value = new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  } catch (e) {
    console.warn('Dashboard API 不可用，使用 mock 数据')
    loadMockData()
  } finally {
    isLoading.value = false
  }
}

function loadMockData() {
  account.total_assets = 128350.42
  account.cash = 83450.00
  account.portfolio_value = 44900.42
  account.total_pnl = 28350.42
  account.total_return_pct = 28.35
  account.positions = []
  animateTo(128350.42)

  predictions.value = [
    { ticker: 'NVDA', name: 'NVIDIA Corp.', score: 0.0734, confidence: 82, direction: 'bullish', change_pct: 3.21, ai_advice: '强烈买入' },
    { ticker: 'AAPL', name: 'Apple Inc.', score: 0.0612, confidence: 76, direction: 'bullish', change_pct: 1.85, ai_advice: '买入' },
    { ticker: 'MSFT', name: 'Microsoft Corp.', score: 0.0445, confidence: 71, direction: 'bullish', change_pct: 0.93, ai_advice: '持有' },
    { ticker: 'TSLA', name: 'Tesla Inc.', score: -0.0231, confidence: 65, direction: 'bearish', change_pct: -2.14, ai_advice: '建议观望' },
    { ticker: 'AMZN', name: 'Amazon.com Inc.', score: 0.0318, confidence: 68, direction: 'bullish', change_pct: 0.52, ai_advice: '持有' },
    { ticker: 'GOOGL', name: 'Alphabet Inc.', score: 0.0289, confidence: 64, direction: 'neutral', change_pct: 0.31, ai_advice: '持有' },
    { ticker: 'META', name: 'Meta Platforms', score: 0.0192, confidence: 59, direction: 'neutral', change_pct: -0.45, ai_advice: '持有' },
    { ticker: 'JPM', name: 'JPMorgan Chase', score: -0.0415, confidence: 72, direction: 'bearish', change_pct: -1.08, ai_advice: '建议观望' },
  ]

  featureImportance.value = [
    { name: '成交量异动', importance: 0.092, description: '当日成交量远超历史均值' },
    { name: 'MACD 背离', importance: 0.085, description: '价格与 MACD 指标背离' },
    { name: '均线多头排列', importance: 0.078, description: 'MA5 > MA20 > MA60' },
    { name: 'RSI 超卖反弹', importance: 0.071, description: 'RSI < 30 且开始回升' },
    { name: '布林带突破', importance: 0.065, description: '价格突破上轨' },
    { name: '资金净流入', importance: 0.058, description: '主力资金持续净流入' },
  ]

  const dates = Array.from({ length: 28 }, (_, i) => `2026-03-${String(i + 1).padStart(2, '0')}`)
  const strategy = dates.map((_, i) => {
    const base = 100000 * (1 + 0.001 * i + Math.sin(i * 0.3) * 0.05)
    return Math.round(base * 100) / 100
  })
  const benchmark = dates.map((_, i) => {
    const base = 100000 * (1 + 0.0006 * i + Math.sin(i * 0.2) * 0.03)
    return Math.round(base * 100) / 100
  })

  void nextTick(async () => {
    await initEquityChart({ dates, strategy_equity: strategy, benchmark_equity: benchmark })
    await initFeaturesChart()
  })

  lastUpdated.value = new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

async function refreshData() {
  await fetchDashboard()
  if (dashboardError.value) {
    ElMessage.warning('刷新失败，请检查后端服务')
    return
  }
  ElMessage.success('数据已刷新')
}

// ─── 操作处理 ─────────────────────────────────────────────────────────────────
function handleBuy(row: any) {
  router.push({ path: '/trade', query: { ticker: row.ticker } })
  ElMessage.success(`已打开模拟交易：${row.ticker}`)
}

function handleDetail(row: any) {
  ElMessage.info(`查看 ${row.ticker} — ${row.name} 详情`)
}

// ─── 窗口调整 ─────────────────────────────────────────────────────────────────
const handleResize = () => {
  equityChart?.resize()
  featuresChart?.resize()
}

// ─── 生命周期 ─────────────────────────────────────────────────────────────────
onMounted(async () => {
  try {
    await fetchDashboard()
  } catch (e) {
    console.warn('仪表盘加载异常', e)
  }
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  isActive = false
  window.removeEventListener('resize', handleResize)
  equityChart?.dispose()
  featuresChart?.dispose()
  if (gsapTween) gsapTween.kill()
})
</script>

<style lang="scss" scoped>
// ════════════════════════════════════════════════════════════════════════════
// 布局
// ════════════════════════════════════════════════════════════════════════════
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding-bottom: 72px;
}

// ─── 资产总览 ────────────────────────────────────────────────────────────────
.equity-section {
  padding: 24px;
}

.equity-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.equity-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: var(--text-secondary);
}

.label-icon {
  font-size: 18px;
  color: var(--accent-cyan);
}

.equity-value {
  display: flex;
  align-items: baseline;
  gap: 4px;
  margin-bottom: 8px;

  .currency {
    font-size: 24px;
    color: var(--text-secondary);
  }

  .amount {
    font-size: 56px;
    font-weight: 700;
    letter-spacing: -2px;
  }
}

.equity-change {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  margin-bottom: 24px;

  &.positive { color: var(--accent-green); }
  &.negative { color: var(--accent-red); }

  .change-icon { font-size: 18px; }
  .change-percent { color: var(--text-tertiary); }
}

.equity-chart {
  height: 240px;
  margin-top: 16px;
}

.chart-skeleton {
  width: 100%;
  height: 100%;
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  padding: 16px;
  overflow: hidden;
}

.skeleton-chart-bars {
  display: flex;
  align-items: flex-end;
  gap: 6px;
  height: 100%;
}

.skeleton-bar {
  flex: 1;
  background: var(--bg-tertiary);
  border-radius: var(--radius-sm) var(--radius-sm) 0 0;
  position: relative;
  overflow: hidden;
}

.skeleton-bar::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.04) 50%, transparent 100%);
  background-size: 200% 100%;
  animation: skeleton-shimmer 1.8s ease-in-out infinite;
}

.skeleton-bar:nth-child(odd) { opacity: 0.7; }
.skeleton-bar:nth-child(1) { animation-delay: 0s; }
.skeleton-bar:nth-child(2) { animation-delay: 0.1s; }
.skeleton-bar:nth-child(3) { animation-delay: 0.2s; }
.skeleton-bar:nth-child(4) { animation-delay: 0.3s; }
.skeleton-bar:nth-child(5) { animation-delay: 0.4s; }
.skeleton-bar:nth-child(6) { animation-delay: 0.5s; }
.skeleton-bar:nth-child(7) { animation-delay: 0.6s; }
.skeleton-bar:nth-child(8) { animation-delay: 0.7s; }
.skeleton-bar:nth-child(9) { animation-delay: 0.8s; }
.skeleton-bar:nth-child(10) { animation-delay: 0.9s; }
.skeleton-bar:nth-child(11) { animation-delay: 1.0s; }
.skeleton-bar:nth-child(12) { animation-delay: 1.1s; }

@keyframes skeleton-shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

.chart-container {
  width: 100%;
  height: 100%;
}

// ─── 指标卡片 ────────────────────────────────────────────────────────────────
.metrics-section {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.metrics-grid {
  display: contents;
}

.metric-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
}

.metric-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--accent-cyan-dim);

  svg { width: 24px; height: 24px; stroke: var(--accent-cyan); }

  &.green { background: var(--accent-green-dim); svg { stroke: var(--accent-green); } }
  &.red { background: var(--accent-red-dim); svg { stroke: var(--accent-red); } }
  &.gold { background: var(--accent-gold-dim); svg { stroke: var(--accent-gold); } }
}

.metric-label {
  font-size: 12px;
  color: var(--text-tertiary);
  margin-bottom: 4px;
}

.metric-value {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
}

/* 卡片交错入场动画 */
.card-stagger-enter-active {
  transition: opacity 0.4s ease, transform 0.4s ease;
}

.card-stagger-enter-from {
  opacity: 0;
  transform: translateY(16px);
}

.fade-in-up {
  animation: fadeInUp 0.5s ease forwards;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(16px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

// ─── 预测表格 ────────────────────────────────────────────────────────────────
.predictions-section {
  padding: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 12px;

  h2 { font-size: 18px; font-weight: 600; color: var(--text-primary); }
  .title-icon { font-size: 24px; }
}

.section-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--text-tertiary);

  .meta-divider { color: var(--border-default); }
}

.rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 6px;
  background: var(--bg-secondary);
  color: var(--text-secondary);
  font-size: 12px;
  font-weight: 600;

  &.top3 {
    background: linear-gradient(135deg, var(--accent-cyan), var(--accent-green));
    color: var(--bg-primary);
  }
}

.ticker-badge {
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
  font-weight: 600;
  color: var(--accent-cyan);
}

.score-value {
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
  font-weight: 600;

  &.positive { color: var(--accent-green); }
  &.negative { color: var(--accent-red); }
}

.confidence-bar-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
}

.confidence-bar {
  position: relative;
  width: 50px;
  height: 6px;
  background: var(--bg-secondary);
  border-radius: 3px;
  overflow: hidden;
}

.confidence-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--accent-cyan), var(--accent-green));
  border-radius: 3px;
  transition: width 0.5s ease;
}

.confidence-text {
  font-size: 11px;
  color: var(--text-tertiary);
  min-width: 32px;
}

.direction-badge {
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;

  &.bullish { background: var(--accent-green-dim); color: var(--accent-green); }
  &.bearish { background: var(--accent-red-dim); color: var(--accent-red); }
  &.neutral { background: var(--bg-secondary); color: var(--text-secondary); }
}

.change-value-cell {
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
  font-weight: 600;

  &.positive { color: var(--accent-green); }
  &.negative { color: var(--accent-red); }
}

.advice-badge {
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  background: var(--accent-cyan-dim);
  color: var(--accent-cyan);
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
}

// ─── 特征重要性 ──────────────────────────────────────────────────────────────
.features-section {
  padding: 24px;
}

.features-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 32px;
}

.features-chart {
  height: 260px;
}

.features-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.feature-rank {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  background: var(--bg-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  flex-shrink: 0;

  &.top {
    background: var(--accent-cyan-dim);
    color: var(--accent-cyan);
  }
}

.feature-info {
  width: 160px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.feature-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.feature-desc {
  font-size: 11px;
  color: var(--text-tertiary);
}

.feature-bar-wrap {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
}

.feature-bar {
  flex: 1;
  height: 8px;
  background: var(--bg-secondary);
  border-radius: 4px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--accent-cyan), var(--accent-green));
  border-radius: 4px;
  transition: width 0.5s ease;
}

.feature-value {
  font-size: 13px;
  font-weight: 600;
  color: var(--accent-cyan);
  min-width: 48px;
  text-align: right;
}

// ─── 响应式 ─────────────────────────────────────────────────────────────────
@media (max-width: 1200px) {
  .metrics-section {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 900px) {
  .features-content {
    grid-template-columns: 1fr;
  }
}
</style>
