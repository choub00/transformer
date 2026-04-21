<script setup lang="ts">
import { computed } from 'vue'
import AnimatedNumber from '../base/AnimatedNumber.vue'

type MetricTrend = 'up' | 'down' | 'flat' | 'positive' | 'negative'

interface Props {
  title: string
  value: number | string
  prefix?: string
  suffix?: string
  trend?: MetricTrend
  decimals?: number
  iconPath?: string
  iconClass?: string
  valueClass?: string
  description?: string
  loading?: boolean
  animated?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  prefix: '$',
  suffix: '',
  trend: 'flat',
  decimals: 2,
  iconClass: 'text-glow-cyan',
  valueClass: '',
  loading: false,
  animated: true,
})

const computedValue = computed(() => {
  if (typeof props.value === 'string') return props.value
  return props.value
})

const trendClass = computed(() => {
  switch (props.trend) {
    case 'up':
    case 'positive':
      return 'trend-up'
    case 'down':
    case 'negative':
      return 'trend-down'
    default:
      return ''
  }
})

const numericValue = computed(() => {
  if (typeof props.value === 'number') return props.value
  return parseFloat(props.value.replace(/,/g, '')) || 0
})
</script>

<template>
  <div class="metric-card glass-card-interactive">
    <div class="metric-header">
      <div class="metric-icon" :class="iconClass">
        <svg v-if="iconPath" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path :d="iconPath" />
        </svg>
      </div>
      <span class="metric-title">{{ title }}</span>
    </div>

    <div class="metric-body">
      <template v-if="loading">
        <div class="skeleton-value">
          <div class="skeleton-block" style="width: 80%; height: 28px;" />
        </div>
      </template>
      <template v-else>
        <AnimatedNumber
          v-if="typeof value === 'number'"
          :value="numericValue"
          :prefix="prefix"
          :suffix="suffix"
          :decimals="decimals"
          :enable-flash="false"
          class="metric-value"
          :class="[valueClass, trendClass]"
        />
        <span v-else class="metric-value" :class="[valueClass, trendClass]">
          {{ prefix }}{{ value }}{{ suffix }}
        </span>
      </template>
    </div>

    <div v-if="description" class="metric-description">
      {{ description }}
    </div>
  </div>
</template>

<style scoped>
.metric-card {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.metric-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.metric-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--accent-cyan-dim);
  border-radius: var(--radius-md);
}

.metric-title {
  font-size: 13px;
  color: var(--text-tertiary);
  font-weight: 500;
}

.metric-body {
  margin-top: 4px;
}

.metric-value {
  font-size: 24px;
  font-weight: 700;
  font-family: 'JetBrains Mono', monospace;
  color: var(--text-primary);
  line-height: 1.2;
}

.trend-up {
  color: var(--up-color);
}

.trend-down {
  color: var(--down-color);
}

.metric-description {
  font-size: 12px;
  color: var(--text-tertiary);
  margin-top: 4px;
}

.skeleton-value {
  display: flex;
  align-items: center;
}
</style>
