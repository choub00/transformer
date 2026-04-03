<template>
  <div class="analysis-view">
    <!-- ══════════════════════════════════════════════════════════════════════════
         视图标题
         ══════════════════════════════════════════════════════════════════════════ -->
    <div class="view-header">
      <h1>&#128202; 股票分析</h1>
      <p class="view-subtitle">基于 AlphaTransformer AI 模型的多维度分析</p>
    </div>

    <div class="analysis-content">
      <!-- ══════════════════════════════════════════════════════════════════════════
           股票选择器
           ══════════════════════════════════════════════════════════════════════════ -->
      <section class="ticker-selector glass-card">
        <div class="selector-label">选择股票</div>
        <div v-if="!availableTickers.length" class="selector-empty">正在加载标的列表…</div>
        <div class="ticker-list" v-else>
          <button
            v-for="ticker in availableTickers"
            :key="ticker.ticker"
            class="ticker-btn"
            :class="{ active: selectedTicker === ticker.ticker }"
            @click="selectTicker(ticker.ticker)"
          >
            <span class="ticker-code">{{ ticker.ticker }}</span>
            <span class="ticker-sector">{{ ticker.sector }}</span>
          </button>
        </div>
      </section>

      <!-- ══════════════════════════════════════════════════════════════════════════
           分析图表区
           ══════════════════════════════════════════════════════════════════════════ -->
      <section class="analysis-charts">
        <!-- K线 + 预测图 -->
        <div class="chart-card glass-card">
          <div class="chart-header">
            <h3>K线走势与 AI 预测</h3>
            <div class="chart-legend">
              <span class="legend-item">
                <span class="legend-dot blue"></span>
                历史走势
              </span>
              <span class="legend-item">
                <span class="legend-dot cyan dashed"></span>
                AI 预测
              </span>
            </div>
          </div>
          <div class="chart-body">
            <div ref="klineChartRef" class="kline-chart"></div>
          </div>
        </div>

        <!-- 技术指标 + AI 评分 -->
        <div class="right-panels">
          <div class="chart-card glass-card">
            <div class="chart-header">
              <h3>技术指标</h3>
            </div>
            <div class="indicators-grid">
              <div class="indicator-item" v-for="ind in indicators" :key="ind.name">
                <span class="indicator-name">{{ ind.name }}</span>
                <span class="indicator-value" :class="ind.signal">
                  {{ ind.value }}
                  <span class="indicator-hint">{{ ind.hint }}</span>
                </span>
              </div>
            </div>
          </div>

          <!-- AI 预测评分卡 -->
          <div class="chart-card glass-card ai-card">
            <div class="chart-header">
              <h3>&#63720; AI 预测评分</h3>
              <span class="confidence-badge" :class="predictionData.confidence >= 70 ? 'high' : predictionData.confidence >= 40 ? 'medium' : 'low'">
                置信度 {{ predictionData.confidence }}%
              </span>
            </div>
            <div class="prediction-cards">
              <div class="prediction-card">
                <div class="card-label">AI 评分</div>
                <div class="card-value" :class="predictionData.score >= 0 ? 'positive' : 'negative'">
                  {{ predictionData.score >= 0 ? '+' : '' }}{{ predictionData.score.toFixed(4) }}
                </div>
                <div class="card-hint">基于多因子模型计算</div>
              </div>
              <div class="prediction-card">
                <div class="card-label">预测方向</div>
                <div class="card-value direction">
                  <span class="direction-icon">
                    {{ predictionData.direction === 'bullish' ? '&#128200;' : predictionData.direction === 'bearish' ? '&#128201;' : '&#10140;' }}
                  </span>
                  {{ predictionData.direction === 'bullish' ? '看多' : predictionData.direction === 'bearish' ? '看空' : '中性' }}
                </div>
                <div class="card-hint">未来 5 日走势预测</div>
              </div>
              <div class="prediction-card">
                <div class="card-label">目标涨幅</div>
                <div class="card-value" :class="predictionData.target_change >= 0 ? 'positive' : 'negative'">
                  {{ predictionData.target_change >= 0 ? '+' : '' }}{{ predictionData.target_change.toFixed(2) }}%
                </div>
                <div class="card-hint">5 日目标价预测</div>
              </div>
              <div class="prediction-card">
                <div class="card-label">风险等级</div>
                <div class="card-value risk" :class="predictionData.risk_level">
                  {{ predictionData.risk_level === 'low' ? '&#127807; 低' : predictionData.risk_level === 'medium' ? '&#128993; 中' : '&#128308; 高' }}
                </div>
                <div class="card-hint">综合风险评估</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ══════════════════════════════════════════════════════════════════════════
           AI 策略解读
           ══════════════════════════════════════════════════════════════════════════ -->
      <section class="ai-analysis glass-card">
        <div class="analysis-header">
          <div class="analysis-title">
            <span class="ai-icon">&#63720;</span>
            <h2>AI 策略解读</h2>
          </div>
          <button class="btn btn-primary btn-sm" @click="generateInsights" :disabled="insightsLoading">
            <span class="loading-spinner" v-if="insightsLoading"></span>
            <span v-else>&#128161; 深度解读</span>
          </button>
        </div>

        <div class="insights-panel">
          <div v-if="insightsLoading" class="insights-loading">
            <span class="loading-spinner"></span>
            <span>AI 正在分析 Cross-Asset Attention 权重...</span>
          </div>
          <div v-else-if="insightsText" class="insights-text">
            <div v-html="formattedInsights"></div>
          </div>
          <div v-else class="insights-placeholder">
            <span class="placeholder-icon">&#128172;</span>
            <p>点击「深度解读」按钮，基于 AlphaTransformer 的 Cross-Asset Attention 权重生成中文投资简报</p>
          </div>
        </div>
      </section>

      <!-- ══════════════════════════════════════════════════════════════════════════
           持仓分析：月度热力图 + 资产配置饼图
           ══════════════════════════════════════════════════════════════════════════ -->
      <section class="portfolio-analysis">
        <div class="analysis-card glass-card">
          <div class="chart-header">
            <h3>&#128199; 月度收益热力图</h3>
          </div>
          <div ref="heatmapRef" class="heatmap-chart"></div>
        </div>

        <div class="analysis-card glass-card">
          <div class="chart-header">
            <h3>&#11088; 资产配置</h3>
          </div>
          <div ref="pieChartRef" class="pie-chart"></div>
          <div class="allocation-legend" v-if="allocationData.length > 0">
            <div class="legend-item" v-for="item in allocationData" :key="item.name">
              <span class="legend-dot" :style="{ background: item.color }"></span>
              <span class="legend-name">{{ item.name }}</span>
              <span class="legend-pct">{{ item.pct }}%</span>
            </div>
          </div>
        </div>
      </section>

      <!-- ══════════════════════════════════════════════════════════════════════════
           特征贡献
           ══════════════════════════════════════════════════════════════════════════ -->
      <section class="feature-contribution glass-card">
        <div class="analysis-header">
          <div class="analysis-title">
            <span class="ai-icon">&#128202;</span>
            <h2>特征贡献度</h2>
          </div>
        </div>

        <div class="contribution-content">
          <div class="contribution-chart">
            <div ref="contributionChartRef" class="chart-container"></div>
          </div>
          <div class="feature-list">
            <div class="feature-item" v-for="(feat, index) in features" :key="feat.name">
              <div class="feature-rank" :class="{ top: index < 3 }">{{ index + 1 }}</div>
              <div class="feature-info">
                <span class="feature-name">{{ feat.name }}</span>
                <span class="feature-desc">{{ feat.description }}</span>
              </div>
              <div class="feature-bar-wrap">
                <div class="feature-bar">
                  <div class="bar-fill" :style="{ width: feat.value + '%' }"></div>
                </div>
                <span class="feature-value">{{ feat.value }}%</span>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { api, apiMarket, apiDashboard } from '../api'
import type { ForecastResponse, KLinePoint } from '../types/api'
import { buildTechnicalIndicators } from '../utils/technicals'
import { forecastToChartSeries } from '../utils/forecastChart'
import { useTickerStore } from '../stores/ticker'

// ─── Refs ─────────────────────────────────────────────────────────────────
const klineChartRef = ref<HTMLElement | null>(null)
const contributionChartRef = ref<HTMLElement | null>(null)
const heatmapRef = ref<HTMLElement | null>(null)
const pieChartRef = ref<HTMLElement | null>(null)

let klineChart: echarts.ECharts | null = null
let contributionChart: echarts.ECharts | null = null
let heatmapChart: echarts.ECharts | null = null
let pieChart: echarts.ECharts | null = null

// ─── State ──────────────────────────────────────────────────────────────
type TickerRow = { ticker: string; name: string; sector: string }

const tickerStore = useTickerStore()
const selectedTicker = ref(tickerStore.selectedTicker || '')
const availableTickers = ref<TickerRow[]>([])
const analysisLoading = ref(false)
const lastForecast = ref<ForecastResponse | null>(null)

const indicators = ref(buildTechnicalIndicators([]))

const predictionData = ref({
  score: 0,
  confidence: 0,
  direction: 'neutral' as 'bullish' | 'bearish' | 'neutral',
  target_change: 0,
  risk_level: 'low' as 'low' | 'medium' | 'high',
})

const features = ref<{ name: string; description: string; value: number }[]>([])

function riskFromScore(score: number): 'low' | 'medium' | 'high' {
  const a = Math.abs(score)
  if (a < 0.035) return 'low'
  if (a < 0.07) return 'medium'
  return 'high'
}

async function loadTickerUniverse() {
  try {
    const res = await apiMarket.tickers()
    const rows = res.data?.tickers ?? []
    availableTickers.value = rows.map((t: { ticker: string; name?: string; sector?: string }) => ({
      ticker: t.ticker,
      name: t.name || t.ticker,
      sector: t.sector || '—',
    }))
    if (!selectedTicker.value && availableTickers.value.length) {
      selectedTicker.value = availableTickers.value[0].ticker
      tickerStore.selectTicker(availableTickers.value[0].ticker, availableTickers.value[0].name)
    } else if (selectedTicker.value) {
      const current = availableTickers.value.find((t) => t.ticker === selectedTicker.value)
      if (current) {
        tickerStore.selectTicker(current.ticker, current.name)
      }
    }
  } catch {
    availableTickers.value = []
  }
}

async function loadAnalysisData(ticker: string) {
  if (!ticker) return
  analysisLoading.value = true
  try {
    const [fcRes, predRes] = await Promise.all([
      apiMarket.forecast(ticker),
      api.get<{ predictions: Array<Record<string, unknown>> }>('/dashboard/predictions', { params: { top_n: 64 } }),
    ])

    const forecast = fcRes.data as ForecastResponse
    lastForecast.value = forecast
    indicators.value = buildTechnicalIndicators(forecast.history as KLinePoint[])

    const preds = predRes.data?.predictions ?? []
    const row = preds.find((p) => String(p.ticker || '').toUpperCase() === ticker.toUpperCase())

    const lastPred = forecast.forecast?.length
      ? forecast.forecast[forecast.forecast.length - 1].predicted_price
      : forecast.current_price
    const targetPct =
      forecast.current_price > 0 ? ((lastPred / forecast.current_price) - 1) * 100 : 0

    const dirRaw = String(row?.direction || 'neutral').toLowerCase()
    const direction =
      dirRaw === 'bullish' || dirRaw === 'bearish' || dirRaw === 'neutral'
        ? dirRaw
        : targetPct > 0.1
          ? 'bullish'
          : targetPct < -0.1
            ? 'bearish'
            : 'neutral'

    const score = typeof row?.score === 'number' ? row.score : targetPct / 800
    const conf =
      typeof row?.confidence === 'number'
        ? row.confidence
        : typeof forecast.confidence_avg === 'number'
          ? forecast.confidence_avg
          : 50

    predictionData.value = {
      score,
      confidence: Math.min(100, Math.max(0, conf)),
      direction,
      target_change: targetPct,
      risk_level: riskFromScore(score),
    }

    await nextTick()
    initKlineChart()
  } catch (e) {
    console.warn('分析数据加载失败', e)
    lastForecast.value = null
    indicators.value = buildTechnicalIndicators([])
  } finally {
    analysisLoading.value = false
  }
}

// AI 解读
const insightsLoading = ref(false)
const insightsText = ref('')
const allocationData = ref<any[]>([])

// 格式化 AI 解读（简单 Markdown-like 渲染）
const formattedInsights = computed(() => {
  return insightsText.value
    .split('\n')
    .map(line => {
      if (line.startsWith('【') && line.endsWith('】')) {
        return `<div class="insight-section-title">${line}</div>`
      }
      if (line.startsWith('· ')) {
        return `<div class="insight-bullet">${line.slice(2)}</div>`
      }
      return `<p>${line}</p>`
    })
    .join('')
})

// ─── K 线图初始化（数据来自 GET /dashboard/forecast/{ticker}）────────────────
const initKlineChart = () => {
  if (!klineChartRef.value) return
  if (klineChart) klineChart.dispose()
  klineChart = echarts.init(klineChartRef.value)

  const fc = lastForecast.value
  if (!fc?.history?.length) {
    klineChart.setOption({
      backgroundColor: 'transparent',
      title: {
        text: analysisLoading.value ? '加载行情…' : '暂无 K 线数据',
        left: 'center',
        top: 'center',
        textStyle: { color: '#6E7681', fontSize: 14 },
      },
    })
    return
  }

  const { dates, kData, predDates, predValues, lastClose } = forecastToChartSeries(fc)
  const histTail = Math.min(20, dates.length)
  const histDates = dates.slice(-histTail)
  const histCloses = kData.slice(-histTail).map((row) => row[1])
  const xAxisLower = [...histDates, ...predDates]
  const lineDataLower: (number | null)[] = [...histCloses, ...predValues]

  const option: echarts.EChartsOption = {
    backgroundColor: 'transparent',
    grid: [
      { top: 20, left: 60, right: 20, height: '55%' },
      { left: 60, right: 20, top: '78%', height: '15%' },
    ],
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
      backgroundColor: 'rgba(22,27,34,0.95)',
      borderColor: 'rgba(0,209,255,0.3)',
      textStyle: { color: '#F0F6FC' },
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
        data: xAxisLower,
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
        data: kData,
        xAxisIndex: 0,
        yAxisIndex: 0,
        itemStyle: {
          color: '#00FFBD',
          color0: '#FF3B30',
          borderColor: '#00FFBD',
          borderColor0: '#FF3B30',
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
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(0,209,255,0.3)' },
            { offset: 1, color: 'rgba(0,209,255,0)' },
          ]),
        },
        markArea:
          predDates.length && histDates.length
            ? {
                silent: true,
                data: [[{ xAxis: histDates[histDates.length - 1] }, { xAxis: predDates[predDates.length - 1] }]],
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

// ─── 特征贡献图 ────────────────────────────────────────────────────────
const initContributionChart = () => {
  if (!contributionChartRef.value) return
  if (contributionChart) contributionChart.dispose()
  contributionChart = echarts.init(contributionChartRef.value)

  const option: echarts.EChartsOption = {
    backgroundColor: 'transparent',
    grid: { left: 120, right: 80, top: 10, bottom: 20 },
    tooltip: { trigger: 'axis', axisPointer: 'shadow' },
    xAxis: {
      type: 'value',
      axisLine: { show: false },
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } },
      axisLabel: { color: '#6E7681', formatter: '{value}%' },
    },
    yAxis: {
      type: 'category',
      data: features.value.map(f => f.name).reverse(),
      axisLine: { show: false },
      axisLabel: { color: '#8B949E', fontSize: 12 },
    },
    series: [{
      type: 'bar',
      data: features.value.map(f => f.value).reverse(),
      barWidth: 18,
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

  contributionChart.setOption(option)
}

// ─── 月度热力图 ────────────────────────────────────────────────────────
const initHeatmapChart = () => {
  if (!heatmapRef.value) return
  if (heatmapChart) heatmapChart.dispose()
  heatmapChart = echarts.init(heatmapRef.value)

  // 生成 12 周 * 5 天的数据
  const data: number[][] = []
  for (let i = 0; i < 12; i++) {
    for (let j = 0; j < 5; j++) {
      data.push([j, i, (Math.random() - 0.45) * 5])
    }
  }

  const option: echarts.EChartsOption = {
    backgroundColor: 'transparent',
    tooltip: {
      formatter: (p: any) => `第 ${p.data[0] + 1} 天，第 ${p.data[1] + 1} 周<br/>收益率: ${p.data[2].toFixed(2)}%`,
    },
    grid: { top: 10, bottom: 10, left: 50, right: 10 },
    xAxis: {
      type: 'category',
      data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
      axisLine: { show: false },
      splitArea: { show: false },
      axisLabel: { color: '#8B949E', fontSize: 10 },
    },
    yAxis: {
      type: 'category',
      data: Array.from({ length: 12 }, (_, i) => `W${i + 1}`).reverse(),
      axisLine: { show: false },
      axisLabel: { color: '#8B949E', fontSize: 10 },
    },
    visualMap: {
      min: -3,
      max: 3,
      calculable: false,
      orient: 'horizontal',
      left: 'center',
      bottom: '-5px',
      inRange: {
        color: ['#FF3B30', '#FF6B6B', '#30363D', '#00FFBD', '#00D1FF'],
      },
      textStyle: { color: '#8B949E', fontSize: 10 },
    },
    series: [{
      type: 'heatmap',
      data,
      itemStyle: {
        borderColor: '#0D1117',
        borderWidth: 2,
        borderRadius: 2,
      },
      label: { show: false },
    }],
  }

  heatmapChart.setOption(option)
}

// ─── 资产配置饼图 ─────────────────────────────────────────────────────
const initPieChart = () => {
  if (!pieChartRef.value) return
  if (pieChart) pieChart.dispose()
  pieChart = echarts.init(pieChartRef.value)

  allocationData.value = [
    { name: 'AAPL', value: 32000, pct: 32, color: '#00D1FF' },
    { name: 'NVDA', value: 25000, pct: 25, color: '#00FFBD' },
    { name: 'MSFT', value: 18000, pct: 18, color: '#FFD700' },
    { name: 'AMZN', value: 15000, pct: 15, color: '#FF6B6B' },
    { name: 'TSLA', value: 10000, pct: 10, color: '#A855F7' },
  ]

  const option: echarts.EChartsOption = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(22,27,34,0.95)',
      borderColor: 'rgba(0,209,255,0.3)',
      textStyle: { color: '#F0F6FC' },
      formatter: '{b}: ${c} ({d}%)',
    },
    legend: { show: false },
    series: [{
      type: 'pie',
      radius: ['45%', '75%'],
      center: ['50%', '50%'],
      avoidLabelOverlap: true,
      itemStyle: {
        borderColor: '#0D1117',
        borderWidth: 2,
        borderRadius: 8,
      },
      label: {
        show: true,
        position: 'outside',
        color: '#8B949E',
        fontSize: 12,
        formatter: '{b} {d}%',
      },
      labelLine: { show: true, lineStyle: { color: '#30363D' } },
      data: allocationData.value.map(d => ({ name: d.name, value: d.value, itemStyle: { color: d.color } })),
    }],
  }

  pieChart.setOption(option)
}

// ─── AI 策略解读 ────────────────────────────────────────────────────
async function generateInsights() {
  insightsLoading.value = true
  insightsText.value = ''

  // 模拟 Claude API 流式响应（实际使用时替换为真实 API 调用）
  await new Promise(resolve => setTimeout(resolve, 500))

  const ticker = selectedTicker.value
  const score = predictionData.value.score
  const direction = predictionData.value.direction

  insightsText.value = `【强势关联分析】
· ${ticker} 与 NVDA 的 Cross-Asset Attention 权重为 0.32，高于均值（0.18），表明资金在科技板块内部轮动。
· ${ticker} 与 JPM 的跨板块 Attention 权重为 0.08，低于预期，建议关注金融板块联动风险。

【风险提示】
· 当前组合波动率为 18.5%，接近策略上限（20%）。
· RSI 指标触及 42.5，处于中性区间，短期可能震荡。
· MACD 出现金叉买入信号，建议关注。

【调仓建议】
· 基于时序注意力分析，预测短期内科技板块动量减弱，建议将 ${ticker} 的 10% 仓位转移至防御性板块（JNJ）。
· 当前持仓方向：${direction === 'bullish' ? '看多' : direction === 'bearish' ? '看空' : '中性'}，AI 评分 ${score >= 0 ? '+' : ''}${score.toFixed(4)}，置信度 ${predictionData.value.confidence}%。`

  insightsLoading.value = false
}

// ─── 选择股票 ────────────────────────────────────────────────────────
function selectTicker(ticker: string) {
  const next = ticker.trim().toUpperCase()
  selectedTicker.value = next
  const current = availableTickers.value.find((t) => t.ticker === next)
  tickerStore.selectTicker(next, current?.name || next)
  void loadAnalysisData(next)
}

// ─── 窗口调整 ───────────────────────────────────────────────────────
const handleResize = () => {
  klineChart?.resize()
  contributionChart?.resize()
  heatmapChart?.resize()
  pieChart?.resize()
}

async function loadFeatureImportance() {
  try {
    const res = await apiDashboard.featureImportance()
    const feats = res.data?.features ?? []
    features.value = feats.slice(0, 8).map((f) => ({
      name: f.name,
      description: f.description || '',
      value: Math.min(100, Math.round((f.importance ?? 0) * 1000)),
    }))
    await nextTick()
    initContributionChart()
  } catch {
    features.value = []
  }
}

// ─── 生命周期 ─────────────────────────────────────────────────────
onMounted(async () => {
  try {
    await loadTickerUniverse()
    await loadFeatureImportance()
    if (selectedTicker.value) {
      await loadAnalysisData(selectedTicker.value)
    } else {
      await nextTick()
      initKlineChart()
    }
    initHeatmapChart()
    initPieChart()
  } catch (e) {
    console.warn('分析页图表初始化失败', e)
  }
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  klineChart?.dispose()
  contributionChart?.dispose()
  heatmapChart?.dispose()
  pieChart?.dispose()
})
</script>

<style lang="scss" scoped>
// ════════════════════════════════════════════════════════════════════════════
// 布局
// ════════════════════════════════════════════════════════════════════════════
.analysis-view {
  padding-bottom: 72px;
}

.view-header {
  margin-bottom: 24px;

  h1 {
    font-size: 24px;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 8px;
  }

  .view-subtitle {
    font-size: 14px;
    color: var(--text-secondary);
  }
}

.analysis-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

// ─── 股票选择器 ──────────────────────────────────────────────────────
.ticker-selector {
  padding: 20px;
}

.selector-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
}

.selector-empty {
  font-size: 13px;
  color: var(--text-tertiary);
  padding: 8px 0;
}

.ticker-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.ticker-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 12px 20px;
  border: 1px solid var(--border-default);
  border-radius: 12px;
  background: transparent;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    border-color: var(--accent-cyan);
    background: var(--accent-cyan-dim);
  }

  &.active {
    border-color: var(--accent-cyan);
    background: var(--accent-cyan-dim);

    .ticker-code {
      color: var(--accent-cyan);
    }
  }

  .ticker-code {
    font-size: 14px;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
    color: var(--text-primary);
  }

  .ticker-sector {
    font-size: 11px;
    color: var(--text-tertiary);
  }
}

// ─── 分析图表 ──────────────────────────────────────────────────────
.analysis-charts {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
}

.right-panels {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.chart-card {
  padding: 20px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;

  h3 {
    font-size: 16px;
    font-weight: 600;
    color: var(--text-primary);
  }
}

.chart-legend {
  display: flex;
  gap: 16px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--text-secondary);
}

.legend-dot {
  width: 12px;
  height: 3px;
  border-radius: 2px;

  &.blue { background: var(--accent-green); }
  &.cyan {
    background: repeating-linear-gradient(
      90deg, var(--accent-cyan), var(--accent-cyan) 4px, transparent 4px, transparent 8px
    );
  }
}

.chart-body {
  height: 280px;
}

.kline-chart {
  width: 100%;
  height: 100%;
}

// ─── 技术指标 ──────────────────────────────────────────────────────
.indicators-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.indicator-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 14px;
  background: var(--bg-secondary);
  border-radius: 12px;
}

.indicator-name {
  font-size: 12px;
  color: var(--text-tertiary);
}

.indicator-value {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);

  &.bullish { color: var(--accent-green); }
  &.bearish { color: var(--accent-red); }
  &.neutral { color: var(--text-secondary); }
}

.indicator-hint {
  font-size: 11px;
  color: var(--text-tertiary);
  font-weight: 400;
  margin-left: 4px;
}

// ─── AI 预测评分卡 ─────────────────────────────────────────────────
.ai-card {
  flex: 1;
}

.confidence-badge {
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;

  &.high { background: var(--accent-green-dim); color: var(--accent-green); }
  &.medium { background: var(--accent-gold-dim); color: var(--accent-gold); }
  &.low { background: var(--accent-red-dim); color: var(--accent-red); }
}

.prediction-cards {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-top: 12px;
}

.prediction-card {
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: 12px;
  text-align: center;
}

.card-label {
  font-size: 11px;
  color: var(--text-tertiary);
  margin-bottom: 8px;
}

.card-value {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 6px;

  &.positive { color: var(--accent-green); }
  &.negative { color: var(--accent-red); }

  &.direction {
    font-size: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
  }

  .direction-icon { font-size: 20px; }
}

.card-hint {
  font-size: 11px;
  color: var(--text-tertiary);
}

// ─── AI 策略解读 ────────────────────────────────────────────────────
.ai-analysis {
  padding: 24px;
}

.analysis-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.analysis-title {
  display: flex;
  align-items: center;
  gap: 12px;

  h2 {
    font-size: 18px;
    font-weight: 600;
    color: var(--text-primary);
  }

  .ai-icon { font-size: 24px; }
}

.btn-sm {
  padding: 8px 16px;
  font-size: 13px;
}

.insights-panel {
  min-height: 160px;
  background: var(--bg-secondary);
  border-radius: 12px;
  padding: 20px;
}

.insights-loading {
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--text-secondary);
  font-size: 14px;
  height: 160px;
  justify-content: center;
}

.insights-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  height: 160px;
  color: var(--text-tertiary);
  text-align: center;

  .placeholder-icon { font-size: 36px; opacity: 0.4; }
  p { font-size: 14px; max-width: 400px; }
}

.insights-text {
  font-size: 14px;
  line-height: 1.8;
  color: var(--text-secondary);

  :deep(.insight-section-title) {
    font-size: 15px;
    font-weight: 700;
    color: var(--accent-cyan);
    margin: 12px 0 8px;
  }

  :deep(.insight-bullet) {
    color: var(--text-secondary);
    padding-left: 16px;
    margin: 4px 0;
  }

  p {
    margin: 4px 0;
    color: var(--text-secondary);
  }
}

// ─── 持仓分析 ──────────────────────────────────────────────────────
.portfolio-analysis {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.analysis-card {
  padding: 20px;
}

.heatmap-chart {
  height: 200px;
  margin-top: 12px;
}

.pie-chart {
  height: 220px;
  margin-top: 12px;
}

.allocation-legend {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 12px;

  .legend-item {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
  }

  .legend-dot {
    width: 10px;
    height: 10px;
    border-radius: 2px;
    flex-shrink: 0;
  }

  .legend-name {
    color: var(--text-primary);
    font-weight: 500;
    flex: 1;
  }

  .legend-pct {
    color: var(--text-secondary);
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
  }
}

// ─── 特征贡献 ──────────────────────────────────────────────────────
.feature-contribution {
  padding: 24px;
}

.contribution-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 32px;
}

.contribution-chart {
  height: 260px;
}

.chart-container {
  width: 100%;
  height: 100%;
}

.feature-list {
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

// ─── 响应式 ────────────────────────────────────────────────────────
@media (max-width: 1200px) {
  .analysis-charts {
    grid-template-columns: 1fr;
  }

  .portfolio-analysis {
    grid-template-columns: 1fr;
  }

  .contribution-content {
    grid-template-columns: 1fr;
  }
}
</style>
