/**
 * AlphaTransformer API 客户端
 * - 统一 baseURL: http://localhost:8080
 * - AbortController: 股票切换时自动取消旧请求
 * - 全局错误拦截: 500 → 中文 Toast（永不裸崩）
 * - JWT 认证: 自动附加 token, 401 自动 refresh
 */

import axios, { type AxiosInstance, type AxiosError, type CancelTokenSource } from 'axios'
import ElNotification from 'element-plus/es/components/notification/index'
import { captureApiError, syncSentryUserContext } from '../lib/sentry'
import { useAuthStore } from '../stores/auth'
import type {
  AccountBalance, AccountConfig, KLineResponse, TickerListResponse,
  PredictionsResponse, OrderRequest, OrderResponse, DelayedOrderRequest,
  TradeHistoryResponse, AutoTradeStatus, AutoTradeStart, AISignalsResponse,
  DashboardFull, DashboardMetrics, EquityCurve, FeatureImportanceResponse,
  ForecastResponse, ApiError,
} from '../types/api'

// ─────────────────────────────────────────────────────────────────────────────
// Axios 实例
// ─────────────────────────────────────────────────────────────────────────────

export const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 30_000,
  headers: { 'Content-Type': 'application/json' },
})

// 避免循环依赖：在模块级别获取 store
function getAuthStore() {
  try {
    return useAuthStore()
  } catch {
    return null
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// 请求拦截器：自动附加 JWT
// ─────────────────────────────────────────────────────────────────────────────

api.interceptors.request.use(
  (config) => {
    const authStore = getAuthStore()
    if (authStore?.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    return config
  },
  (error) => Promise.reject(error),
)

// ─────────────────────────────────────────────────────────────────────────────
// 401 自动 refresh 机制
// ─────────────────────────────────────────────────────────────────────────────

const NOTIFICATION_DEDUPE_MS = 3500
const lastErrorNotificationAt = new Map<string, number>()
let isRefreshing = false
let refreshSubscribers: Array<(token: string) => void> = []

function subscribeTokenRefresh(callback: (token: string) => void) {
  refreshSubscribers.push(callback)
}

function onTokenRefreshed(newToken: string) {
  refreshSubscribers.forEach((cb) => cb(newToken))
  refreshSubscribers = []
}

async function handleUnauthorized(): Promise<string | null> {
  const authStore = getAuthStore()
  if (!authStore?.refreshToken) return null

  if (isRefreshing) {
    return new Promise((resolve) => {
      subscribeTokenRefresh((token) => resolve(token))
    })
  }

  isRefreshing = true
  try {
    const res = await api.post('/auth/refresh', { refresh_token: authStore.refreshToken })
    const { access_token, refresh_token } = res.data
    authStore.token = access_token
    authStore.refreshToken = refresh_token
    localStorage.setItem('at_access_token', access_token)
    localStorage.setItem('at_refresh_token', refresh_token)
    onTokenRefreshed(access_token)
    return access_token
  } catch {
    authStore.logout()
    window.location.href = '/login'
    return null
  } finally {
    isRefreshing = false
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// 响应拦截器：消灭 500 + 401 自动 refresh
// ─────────────────────────────────────────────────────────────────────────────

api.interceptors.response.use(
  async (response) => {
    syncSentryUserContext(response.data)
    return response
  },
  async (error: AxiosError<ApiError>) => {
    if (axios.isCancel(error)) {
      return Promise.reject(error)
    }

    const originalRequest = error.config

    // 401: 尝试 refresh token（避免循环）
    if (error.response?.status === 401 && originalRequest && !(originalRequest.headers as any)['X-Retry']) {
      const newToken = await handleUnauthorized()
      if (newToken) {
        ;(originalRequest.headers as any)['Authorization'] = `Bearer ${newToken}`
        ;(originalRequest.headers as any)['X-Retry'] = 'true'
        return api(originalRequest)
      }
      return Promise.reject(error)
    }

    captureApiError(error)

    const code = (error.response?.data as any)?.code || 'UNKNOWN'
    const detail = (error.response?.data as any)?.detail || error.message || '未知错误'
    const errorMsg = `[${code}] ${detail}`

    const now = Date.now()
    const notificationKey = `${code}:${detail}`
    const lastShownAt = lastErrorNotificationAt.get(notificationKey) || 0

    if (now - lastShownAt > NOTIFICATION_DEDUPE_MS) {
      lastErrorNotificationAt.set(notificationKey, now)
      ElNotification({
        title: '请求失败',
        message: errorMsg,
        type: 'error',
        duration: 3500,
        position: 'top-right',
      })
    }

    return Promise.reject(error)
  },
)

// ─────────────────────────────────────────────────────────────────────────────
// 请求管理器（AbortController 包装）
// ─────────────────────────────────────────────────────────────────────────────

const _sources = new Map<string, CancelTokenSource>()

export function cancelRequest(key: string) {
  const src = _sources.get(key)
  if (src) {
    src.cancel(`[Cancel] 请求 ${key} 被新的相同请求取消`)
    _sources.delete(key)
  }
}

export function getCancelToken(key: string): CancelTokenSource {
  cancelRequest(key)
  const src = axios.CancelToken.source()
  _sources.set(key, src)
  return src
}

// ─────────────────────────────────────────────────────────────────────────────
// 账户接口
// ─────────────────────────────────────────────────────────────────────────────

export const apiAccount = {
  /** 获取账户状态 */
  get: () => api.get<AccountBalance>('/account'),

  /** 修改账户配置 */
  config: (data: AccountConfig) =>
    api.post('/account/config', data),

  /** 重置账户 */
  reset: () => api.post('/account/reset'),
}

// ─────────────────────────────────────────────────────────────────────────────
// 市场接口
// ─────────────────────────────────────────────────────────────────────────────

export const apiMarket = {
  /** Alpha Vantage 实时 K 线（优先，失败时后端自动降级模拟数据） */
  kline: (ticker: string, period = '1y') =>
    api.get<KLineResponse>(`/dashboard/kline/realtime/${ticker}`, {
      params: { period },
      cancelToken: getCancelToken(`kline-${ticker}`).token,
    }),

  /** Alpha-Transformer-2026 历史 OHLC + 5日预测（主接口） */
  forecast: (ticker: string) =>
    api.get<ForecastResponse>(`/dashboard/forecast/${ticker}`, {
      cancelToken: getCancelToken(`forecast-${ticker}`).token,
    }),

  /** 股票列表 */
  tickers: () => api.get<TickerListResponse>('/dashboard/tickers'),

  /** AI 预测排名 */
  predictions: (top_n = 10) =>
    api.get<PredictionsResponse>('/dashboard/predictions', {
      params: { top_n },
    }),
}

// ─────────────────────────────────────────────────────────────────────────────
// 交易接口
// ─────────────────────────────────────────────────────────────────────────────

export const apiTrade = {
  /** 下单 */
  order: (data: OrderRequest) =>
    api.post<OrderResponse>('/trade/order', data),

  /** 平仓 */
  close: (ticker: string) =>
    api.post(`/trade/close`, null, { params: { ticker } }),

  /** T+1 延迟单 */
  delayed: (data: DelayedOrderRequest) =>
    api.post('/trade/delayed', data),

  /** 历史成交 */
  history: (limit = 50) =>
    api.get<TradeHistoryResponse>('/trade/history', { params: { limit } }),

  /** 交易日志 */
  logs: (limit = 50) =>
    api.get<TradeHistoryResponse>('/trade/logs', { params: { limit } }),
}

// ─────────────────────────────────────────────────────────────────────────────
// 自动交易接口
// ─────────────────────────────────────────────────────────────────────────────

export const apiAuto = {
  /** 获取自动交易状态 */
  status: () => api.get<AutoTradeStatus>('/auto/status'),

  /** 启动自动交易 */
  start: (data?: AutoTradeStart) =>
    api.post('/auto/start', data || {}),

  /** 停止自动交易 */
  stop: () => api.post('/auto/stop'),

  /** 获取 AI 信号 */
  signals: () => api.get<AISignalsResponse>('/auto/signals'),
}

// ─────────────────────────────────────────────────────────────────────────────
// Dashboard 接口
// ─────────────────────────────────────────────────────────────────────────────

export const apiDashboard = {
  /** 完整 Dashboard */
  full: () => api.get<DashboardFull>('/dashboard/full'),

  /** 回测指标 */
  metrics: () => api.get<DashboardMetrics>('/dashboard/metrics'),

  /** AI 预测排名 */
  predictions: () => api.get<PredictionsResponse>('/dashboard/predictions'),

  /** 权益曲线 */
  equityCurve: () => api.get<EquityCurve>('/dashboard/equity-curve'),

  /** 特征重要性 */
  featureImportance: () =>
    api.get<FeatureImportanceResponse>('/dashboard/feature-importance'),
}

// ─────────────────────────────────────────────────────────────────────────────
// 快捷导出（向后兼容）
// ─────────────────────────────────────────────────────────────────────────────

export const apiTrading = apiAccount
