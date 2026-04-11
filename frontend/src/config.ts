/**
 * K 线 / 预测数据轮询间隔（毫秒）。
 * - 默认 5 分钟：换日后会自动拉到新日期区间（依赖后端 date.today()）。
 * - 设为 0 关闭轮询。
 * - 可在 .env 中设置：VITE_FORECAST_REFRESH_MS=60000
 */
export const FORECAST_REFRESH_MS = (() => {
  const raw = import.meta.env.VITE_FORECAST_REFRESH_MS
  if (raw === '0' || raw === '') return 0
  const n = Number(raw)
  if (Number.isFinite(n) && n >= 0) return n
  return 5 * 60 * 1000
})()
