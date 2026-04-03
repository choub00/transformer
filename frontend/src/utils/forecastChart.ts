import type { ForecastResponse } from '../types/api'

/** 将 /dashboard/forecast 响应拆成 ECharts K 线 + 预测序列所需结构 */
export function forecastToChartSeries(forecast: ForecastResponse) {
  const h = forecast.history || []
  const dates = h.map((x) => x.date)
  const kData = h.map((x) => [x.open, x.close, x.low, x.high] as number[])
  const f = forecast.forecast || []
  const predDates = f.map((x) => x.date)
  const predValues = f.map((x) => x.predicted_price)
  const lastClose = h.length ? h[h.length - 1].close : forecast.current_price
  return { dates, kData, predDates, predValues, lastClose, currentPrice: forecast.current_price }
}
