/**
 * 数字格式化工具
 */

export function formatNumber(
  num: number,
  options?: Intl.NumberFormatOptions
): string {
  if (num === null || num === undefined || isNaN(num)) {
    return '0.00'
  }

  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
    ...options,
  }).format(num)
}

export function formatPercent(
  num: number,
  options?: Intl.NumberFormatOptions
): string {
  return formatNumber(num * 100, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
    ...options,
  }) + '%'
}

export function formatCompact(num: number): string {
  if (num === null || num === undefined || isNaN(num)) {
    return '0'
  }

  if (Math.abs(num) >= 1e9) {
    return (num / 1e9).toFixed(2) + 'B'
  }
  if (Math.abs(num) >= 1e6) {
    return (num / 1e6).toFixed(2) + 'M'
  }
  if (Math.abs(num) >= 1e3) {
    return (num / 1e3).toFixed(2) + 'K'
  }
  return num.toFixed(2)
}
