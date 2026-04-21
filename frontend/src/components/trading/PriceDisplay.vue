<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  value: number
  decimals?: number
  prefix?: string
  showSign?: boolean
  size?: 'sm' | 'md' | 'lg'
  animated?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  decimals: 2,
  prefix: '$',
  showSign: false,
  size: 'md',
  animated: true,
})

const formattedValue = computed(() => {
  const num = typeof props.value === 'number' ? props.value : parseFloat(props.value)
  if (isNaN(num)) return `${props.prefix}--`

  const fixed = num.toLocaleString('en-US', {
    minimumFractionDigits: props.decimals,
    maximumFractionDigits: props.decimals,
  })

  if (props.showSign && num > 0) return `${props.prefix}+${fixed}`
  if (props.showSign && num < 0) return `${props.prefix}-${fixed}`
  return `${props.prefix}${fixed}`
})

const trend = computed<'up' | 'down' | 'flat'>(() => {
  if (props.value > 0) return 'up'
  if (props.value < 0) return 'down'
  return 'flat'
})

const trendClass = computed(() => {
  switch (trend.value) {
    case 'up': return 'trend-up'
    case 'down': return 'trend-down'
    default: return ''
  }
})

const sizeClass = computed(() => `size-${props.size}`)
</script>

<template>
  <span class="price-display" :class="[sizeClass, trendClass]">
    {{ formattedValue }}
  </span>
</template>

<style scoped>
.price-display {
  font-family: 'JetBrains Mono', monospace;
  font-variant-numeric: tabular-nums;
  font-feature-settings: "tnum";
  transition: color 0.15s ease;
}

.size-sm { font-size: 13px; }
.size-md { font-size: 16px; font-weight: 600; }
.size-lg { font-size: 24px; font-weight: 700; }

.trend-up { color: var(--up-color); }
.trend-down { color: var(--down-color); }
</style>
