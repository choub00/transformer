<script setup lang="ts">
import { computed } from 'vue'

type SignalType = 'bullish' | 'bearish' | 'neutral' | 'buy' | 'sell' | 'hold'
type RiskLevel = 'low' | 'medium' | 'high'

interface Props {
  type: SignalType
  label?: string
  showIcon?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  label: '',
  showIcon: true,
})

const normalizedType = computed<SignalType>(() => {
  if (props.type === 'buy') return 'bullish'
  if (props.type === 'sell') return 'bearish'
  if (props.type === 'hold') return 'neutral'
  return props.type
})

const config = computed(() => {
  switch (normalizedType.value) {
    case 'bullish':
      return { class: 'bullish', text: '多头', icon: '↑' }
    case 'bearish':
      return { class: 'bearish', text: '空头', icon: '↓' }
    case 'buy':
      return { class: 'bullish', text: '买入', icon: '↗' }
    case 'sell':
      return { class: 'bearish', text: '卖出', icon: '↘' }
    default:
      return { class: 'neutral', text: '中性', icon: '→' }
  }
})
</script>

<template>
  <span class="signal-badge" :class="config.class">
    <span v-if="showIcon" class="signal-icon">{{ config.icon }}</span>
    <span v-if="label" class="signal-text">{{ label }}</span>
    <span v-else class="signal-text">{{ config.text }}</span>
  </span>
</template>

<style scoped>
.signal-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  border-radius: var(--radius-full);
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
  transition: all var(--transition-fast);
}

.signal-badge:hover {
  transform: scale(1.03);
}

.signal-icon {
  font-size: 10px;
  font-weight: 700;
}

.signal-text {
  line-height: 1;
}

.bullish {
  background: var(--accent-green-dim);
  color: var(--accent-green);
  border: 1px solid rgba(0, 255, 189, 0.2);
}

.bullish:hover {
  background: rgba(0, 255, 189, 0.25);
  box-shadow: 0 0 12px var(--accent-green-glow);
}

.bearish {
  background: var(--accent-red-dim);
  color: var(--accent-red);
  border: 1px solid rgba(255, 59, 48, 0.2);
}

.bearish:hover {
  background: rgba(255, 59, 48, 0.25);
  box-shadow: 0 0 12px var(--accent-red-glow);
}

.neutral {
  background: var(--bg-secondary);
  color: var(--text-secondary);
  border: 1px solid var(--border-default);
}

.neutral:hover {
  border-color: var(--border-hover);
  background: var(--bg-hover);
}
</style>
