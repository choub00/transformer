/**
 * Dashboard Pinia Store — 严格类型版
 * 管理仪表盘核心数据：指标、权益曲线、预测、特征重要性
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
import { apiDashboard } from '../api'
import type {
  DashboardMetrics,
  EquityCurve,
  StockPrediction,
  FeatureImportanceItem,
} from '../types/api'

export const useDashboardStore = defineStore('dashboard', () => {
  // ─── State ────────────────────────────────────────────────────────────────
  const metrics = ref<DashboardMetrics | null>(null)
  const equityCurve = ref<EquityCurve | null>(null)
  const predictions = ref<StockPrediction[]>([])
  const featureImportance = ref<FeatureImportanceItem[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const lastUpdated = ref<string | null>(null)

  // ─── Computed ─────────────────────────────────────────────────────────────
  const topPrediction = computed<StockPrediction | null>(() =>
    predictions.value.length > 0 ? predictions.value[0] : null
  )

  const bullishCount = computed<number>(() =>
    predictions.value.filter((p) => p.direction === 'bullish').length
  )

  const bearishCount = computed<number>(() =>
    predictions.value.filter((p) => p.direction === 'bearish').length
  )

  const neutralCount = computed<number>(() =>
    predictions.value.filter((p) => p.direction === 'neutral').length
  )

  // ─── Actions ──────────────────────────────────────────────────────────────

  /** 加载完整 Dashboard 数据（一个请求搞定） */
  async function loadFull() {
    loading.value = true
    error.value = null
    try {
      const { data } = await apiDashboard.full()
      metrics.value = data.metrics
      equityCurve.value = data.equity_curve
      predictions.value = data.predictions ?? []
      featureImportance.value = data.feature_importance ?? []
      lastUpdated.value = new Date().toLocaleTimeString('zh-CN')
    } catch (e: unknown) {
      if (!axios.isCancel(e)) {
        const msg = e instanceof Error ? e.message : '加载 Dashboard 数据失败'
        error.value = msg
      }
    } finally {
      loading.value = false
    }
  }

  /** 单独刷新指标 */
  async function refreshMetrics() {
    try {
      const { data } = await apiDashboard.metrics()
      metrics.value = data
    } catch {
      // 静默失败，不影响主流程
    }
  }

  /** 单独刷新权益曲线 */
  async function refreshEquityCurve() {
    try {
      const { data } = await apiDashboard.equityCurve()
      equityCurve.value = data
    } catch {
      // 静默失败
    }
  }

  /** 单独刷新预测排名 */
  async function refreshPredictions() {
    try {
      const { data } = await apiDashboard.predictions()
      predictions.value = data.predictions ?? []
    } catch {
      // 静默失败
    }
  }

  /** 单独刷新特征重要性 */
  async function refreshFeatureImportance() {
    try {
      const { data } = await apiDashboard.featureImportance()
      featureImportance.value = data.features ?? []
    } catch {
      // 静默失败
    }
  }

  /** 重置状态 */
  function $reset() {
    metrics.value = null
    equityCurve.value = null
    predictions.value = []
    featureImportance.value = []
    loading.value = false
    error.value = null
    lastUpdated.value = null
  }

  return {
    // State
    metrics,
    equityCurve,
    predictions,
    featureImportance,
    loading,
    error,
    lastUpdated,
    // Computed
    topPrediction,
    bullishCount,
    bearishCount,
    neutralCount,
    // Actions
    loadFull,
    refreshMetrics,
    refreshEquityCurve,
    refreshPredictions,
    refreshFeatureImportance,
    $reset,
  }
})
