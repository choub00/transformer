export interface ApiError {
  error: string
  detail: string
  code: string
}

export interface AccountConfig {
  init_cash: number
  fee_rate: number
  stop_loss_pct: number
  top_n: number
}

export interface Position {
  ticker: string
  quantity: number
  entry_price: number
  current_price: number
  market_value: number
  unrealized_pnl: number
  unrealized_pnl_pct: number
  ai_advice: string
  direction: string
}

export interface AccountBalance {
  total_assets: number
  cash: number
  init_cash: number
  portfolio_value: number
  total_pnl: number
  total_return_pct: number
  available_cash: number
  positions_count: number
  total_fees: number
  total_trades: number
  winning_trades: number
  losing_trades: number
  win_rate: number
  daily_pnl: number
  daily_trades: number
  positions: Position[]
  equity_curve: Array<Record<string, unknown>>
  updated_at: string
}

export interface DashboardMetrics {
  sharpe_ratio: number
  annual_return: number
  max_drawdown: number
  win_rate: number
  total_trades: number
  avg_trade_pnl: number
  profit_factor: number
}

export interface EquityCurve {
  dates: string[]
  strategy_equity: number[]
  benchmark_equity: number[]
}

export interface FeatureImportanceItem {
  name: string
  importance: number
  description: string
}

export interface FeatureImportanceResponse {
  features: FeatureImportanceItem[]
}

export interface StockPrediction {
  ticker: string
  name: string
  score: number
  confidence: number
  direction: 'bullish' | 'bearish' | 'neutral'
  change_pct: number
  ai_advice: string
  rank: number
  symbol?: string
  signal?: 'bullish' | 'bearish' | 'neutral'
}

export interface PredictionsResponse {
  predictions: StockPrediction[]
  updated_at: string
  ic: number
  sharpe: number
  max_drawdown: number
  win_rate: number
}

export interface KLinePoint {
  date: string
  open: number
  high: number
  low: number
  close: number
  volume: number
}

export interface PredictionPoint {
  date: string
  predicted_price: number
  lower_bound: number
  upper_bound: number
  confidence: number
}

export interface KLineResponse {
  ticker: string
  period: string
  klines: KLinePoint[]
  predictions: PredictionPoint[]
}

export interface ForecastPoint {
  date: string
  predicted_price: number
  lower_bound: number
  upper_bound: number
  confidence: number
}

export interface ForecastResponse {
  ticker: string
  current_price: number
  history: KLinePoint[]
  forecast: ForecastPoint[]
  model_version: string
  confidence_avg: number
}

export interface TickerListResponse {
  tickers: Array<{
    ticker: string
    name: string
    sector: string
    price: number
    change_pct: number
  }>
}

export interface OrderRequest {
  ticker: string
  side: 'buy' | 'sell'
  quantity: number
  price?: number
}

export interface OrderResponse {
  success: boolean
  order_id: string
  ticker: string
  side: 'buy' | 'sell'
  quantity: number
  price: number
  fee: number
  total_cost: number
  timestamp: string
  status: 'filled' | 'pending' | 'rejected'
}

export interface DelayedOrderRequest {
  ticker: string
  side: 'buy' | 'sell'
  quantity: number
  ai_score?: number
}

export interface TradeLog {
  date: string
  ticker: string
  side: 'buy' | 'sell'
  quantity: number
  price: number
  fee: number
  pnl?: number | null
}

export interface TradeHistoryResponse {
  trades: TradeLog[]
  total: number
}

export interface AutoTradeStatus {
  enabled: boolean
  interval: number
  top_n: number
  last_run: string | null
  signals: Array<{
    ticker: string
    ai_score: number
    direction: string
    confidence: number
    reason: string
  }>
}

export interface AutoTradeStart {
  interval?: number
  top_n?: number
  stop_loss_pct?: number
}

export interface AISignalsResponse {
  signals: Array<{
    ticker: string
    ai_score: number
    direction: string
    confidence: number
    reason: string
  }>
  generated_at: string
  count?: number
}

export interface DashboardFull {
  metrics: DashboardMetrics
  equity_curve: EquityCurve
  feature_importance: FeatureImportanceItem[]
  predictions: StockPrediction[]
  account: AccountBalance
}

export interface AIInsightRequest {
  positions: Position[]
  predictions: StockPrediction[]
  top_attention_weights?: Array<{ from: string; to: string; weight: number }>
}

export interface AIInsightResponse {
  insights: string
  confidence: number
  generated_at: string
}
