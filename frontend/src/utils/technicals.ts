import type { KLinePoint } from '../types/api'

export type IndicatorSignal = 'bullish' | 'bearish' | 'neutral'

export interface TechnicalIndicatorRow {
  name: string
  value: string
  signal: IndicatorSignal
  hint: string
}

function sma(values: number[], len: number): number {
  const slice = values.slice(-len)
  if (!slice.length) return 0
  return slice.reduce((a, b) => a + b, 0) / slice.length
}

/** 递推 EMA，与常见行情库足够接近（演示/联动用） */
function emaSeries(values: number[], period: number): number[] {
  if (!values.length) return []
  const k = 2 / (period + 1)
  const out: number[] = []
  let e = values[0]
  for (const v of values) {
    e = v * k + e * (1 - k)
    out.push(e)
  }
  return out
}

function rsiWilder(closes: number[], period = 14): number {
  if (closes.length < period + 1) return 50
  let gains = 0
  let losses = 0
  for (let i = closes.length - period; i < closes.length; i++) {
    const d = closes[i] - closes[i - 1]
    if (d >= 0) gains += d
    else losses -= d
  }
  const ag = gains / period
  const al = losses / period
  if (al === 0) return 100
  const rs = ag / al
  return 100 - 100 / (1 + rs)
}

/**
 * 由后端返回的 OHLC 序列推导技术指标展示行（与 UI 六宫格对齐）
 */
export function buildTechnicalIndicators(history: KLinePoint[]): TechnicalIndicatorRow[] {
  if (!history?.length) {
    return [
      { name: 'MACD', value: '—', signal: 'neutral', hint: '等待 K 线数据' },
      { name: 'RSI', value: '—', signal: 'neutral', hint: '等待 K 线数据' },
      { name: '布林带', value: '—', signal: 'neutral', hint: '等待 K 线数据' },
      { name: 'MA5', value: '—', signal: 'neutral', hint: '等待 K 线数据' },
      { name: 'MA20', value: '—', signal: 'neutral', hint: '等待 K 线数据' },
      { name: '成交量', value: '—', signal: 'neutral', hint: '等待 K 线数据' },
    ]
  }

  const closes = history.map((h) => h.close)
  const vols = history.map((h) => h.volume)
  const last = closes[closes.length - 1]

  const ma5 = closes.length >= 5 ? sma(closes, 5) : last
  const ma20 = closes.length >= 20 ? sma(closes, 20) : sma(closes, Math.min(20, closes.length))
  const sd20 =
    closes.length >= 20
      ? Math.sqrt(
          closes
            .slice(-20)
            .reduce((s, c) => s + (c - ma20) ** 2, 0) / 20,
        )
      : 0
  const upper = ma20 + 2 * sd20
  const lower = ma20 - 2 * sd20

  let bbPos: TechnicalIndicatorRow['signal'] = 'neutral'
  let bbHint = '中轨附近'
  if (last > upper) {
    bbPos = 'bearish'
    bbHint = '触及上轨'
  } else if (last < lower) {
    bbPos = 'bullish'
    bbHint = '触及下轨'
  } else if (last > ma20) {
    bbPos = 'bullish'
    bbHint = '中轨上方'
  } else {
    bbPos = 'bearish'
    bbHint = '中轨下方'
  }

  const r = rsiWilder(closes, 14)
  let rsiSig: IndicatorSignal = 'neutral'
  let rsiHint = '中性区间'
  if (r >= 70) {
    rsiSig = 'bearish'
    rsiHint = '超买区域'
  } else if (r <= 30) {
    rsiSig = 'bullish'
    rsiHint = '超卖区域'
  }

  const e12 = emaSeries(closes, 12)
  const e26 = emaSeries(closes, 26)
  const macdLine = e12.map((v, i) => v - e26[i])
  const signalLine = emaSeries(macdLine, 9)
  const i = macdLine.length - 1
  const macdNow = macdLine[i]
  const sigNow = signalLine[i]
  const macdPrev = macdLine[Math.max(0, i - 1)]
  const sigPrev = signalLine[Math.max(0, i - 1)]

  let macdText = macdNow >= sigNow ? '多头' : '空头'
  let macdSig: IndicatorSignal = macdNow >= sigNow ? 'bullish' : 'bearish'
  let macdHint = macdNow >= sigNow ? '动能偏强' : '动能偏弱'
  if (macdPrev <= sigPrev && macdNow > sigNow) {
    macdText = '金叉'
    macdSig = 'bullish'
    macdHint = '买入信号'
  } else if (macdPrev >= sigPrev && macdNow < sigNow) {
    macdText = '死叉'
    macdSig = 'bearish'
    macdHint = '卖出信号'
  }

  const volMa = vols.length >= 20 ? sma(vols, 20) : sma(vols, vols.length)
  const lastVol = vols[vols.length - 1] || 0
  const volRatio = volMa > 0 ? lastVol / volMa : 1
  let volSig: IndicatorSignal = 'neutral'
  if (volRatio >= 1.2) volSig = 'bullish'
  else if (volRatio <= 0.8) volSig = 'bearish'

  const maTrend: IndicatorSignal = ma5 >= ma20 ? 'bullish' : 'bearish'

  return [
    { name: 'MACD', value: macdText, signal: macdSig, hint: macdHint },
    { name: 'RSI', value: r.toFixed(1), signal: rsiSig, hint: rsiHint },
    { name: '布林带', value: last > upper ? '上轨' : last < lower ? '下轨' : '中轨', signal: bbPos, hint: bbHint },
    { name: 'MA5', value: ma5.toFixed(2), signal: maTrend, hint: ma5 >= ma20 ? '均线多头' : '均线空头' },
    { name: 'MA20', value: ma20.toFixed(2), signal: last >= ma20 ? 'bullish' : 'bearish', hint: last >= ma20 ? '趋势向上' : '趋势承压' },
    {
      name: '成交量',
      value: `${volRatio.toFixed(2)}x`,
      signal: volSig,
      hint: volRatio >= 1.2 ? '量能放大' : volRatio <= 0.8 ? '量能萎缩' : '量能平稳',
    },
  ]
}
