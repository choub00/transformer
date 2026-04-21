type FormatNumberOptions = {
  decimals?: number
  minimumFractionDigits?: number
  maximumFractionDigits?: number
  fallback?: string
  signed?: boolean
}

function toFiniteNumber(value: unknown): number | null {
  const numeric = typeof value === 'number' ? value : Number(value)
  return Number.isFinite(numeric) ? numeric : null
}

export function formatNumber(value: unknown, options: FormatNumberOptions = {}) {
  const numeric = toFiniteNumber(value)
  if (numeric === null) {
    return options.fallback ?? '--'
  }

  const decimals = options.decimals
  const minimumFractionDigits = options.minimumFractionDigits ?? decimals ?? 0
  const maximumFractionDigits = options.maximumFractionDigits ?? decimals ?? 0
  const formatter = new Intl.NumberFormat('en-US', {
    minimumFractionDigits,
    maximumFractionDigits,
  })

  const formatted = formatter.format(Math.abs(numeric))
  if (!options.signed) {
    return numeric < 0 ? `-${formatted}` : formatted
  }

  if (numeric > 0) return `+${formatted}`
  if (numeric < 0) return `-${formatted}`
  return formatted
}

export function formatCurrency(value: unknown, options: FormatNumberOptions = {}) {
  const numeric = toFiniteNumber(value)
  if (numeric === null) {
    return options.fallback ?? '--'
  }

  const body = formatNumber(numeric, {
    ...options,
    signed: false,
  })

  if (options.signed) {
    if (numeric > 0) return `+$${body}`
    if (numeric < 0) return `-$${formatNumber(Math.abs(numeric), { ...options, signed: false })}`
  }

  return `${numeric < 0 ? '-' : ''}$${formatNumber(Math.abs(numeric), {
    ...options,
    signed: false,
  })}`
}

export function formatPercent(value: unknown, options: FormatNumberOptions = {}) {
  const numeric = toFiniteNumber(value)
  if (numeric === null) {
    return options.fallback ?? '--'
  }

  return `${formatNumber(numeric, {
    ...options,
    signed: options.signed ?? false,
    minimumFractionDigits: options.minimumFractionDigits ?? options.decimals ?? 1,
    maximumFractionDigits: options.maximumFractionDigits ?? options.decimals ?? 1,
  })}%`
}

// ─── 涨跌/盈亏相关 ───────────────────────────────────────────────────────────

export type Trend = 'up' | 'down' | 'flat'

export function getTrend(value: number | undefined | null): Trend {
  if (value === undefined || value === null) return 'flat'
  if (value > 0) return 'up'
  if (value < 0) return 'down'
  return 'flat'
}

export function isPositive(value: number | undefined | null): boolean {
  return value !== undefined && value !== null && value >= 0
}

export function getPnLSign(value: number | undefined | null): '' | '+' | '-' {
  if (value === undefined || value === null) return ''
  if (value > 0) return '+'
  if (value < 0) return '-'
  return ''
}

// ─── 格式化快捷函数 ─────────────────────────────────────────────────────────

export function formatPrice(value: unknown, decimals = 2): string {
  return formatNumber(value, { decimals, minimumFractionDigits: decimals, maximumFractionDigits: decimals })
}

export function formatMoney(value: unknown, decimals = 2): string {
  return formatCurrency(value, { decimals, minimumFractionDigits: decimals, maximumFractionDigits: decimals })
}

export function formatChange(value: unknown, decimals = 2): string {
  return formatCurrency(value, { signed: true, decimals })
}

export function formatRatio(value: unknown, decimals = 2): string {
  return formatPercent(value, { signed: true, decimals })
}

export function formatShares(value: unknown): string {
  return formatNumber(value, { decimals: 0 })
}

// ─── 颜色相关 ────────────────────────────────────────────────────────────────

export type ColorTheme = 'dark' | 'light'

export interface PnLColorOptions {
  positiveClass?: string
  negativeClass?: string
  neutralClass?: string
  theme?: ColorTheme
}

export function getPnLClasses(
  value: number | undefined | null,
  options: PnLColorOptions = {}
): string {
  const { positiveClass = 'text-positive', negativeClass = 'text-negative', neutralClass = 'text-neutral' } = options

  if (value === undefined || value === null) return neutralClass
  if (value > 0) return positiveClass
  if (value < 0) return negativeClass
  return neutralClass
}

// ─── 默认配置 ────────────────────────────────────────────────────────────────

export const DEFAULT_FORMAT_OPTIONS: FormatNumberOptions = {
  decimals: 2,
  fallback: '--',
}

