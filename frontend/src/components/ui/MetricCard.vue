<template>
  <ModuleShell as="article" class="metric-card" :accent="accent" interactive>
    <div class="metric-icon" :class="accent">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path :d="iconPath" />
      </svg>
    </div>
    <div class="metric-content">
      <div class="metric-label">{{ label }}</div>
      <div class="metric-value number-roll" :class="valueClass">{{ value }}</div>
    </div>
  </ModuleShell>
</template>

<script setup lang="ts">
import ModuleShell from './ModuleShell.vue'

withDefaults(defineProps<{
  label: string
  value: string
  iconPath: string
  accent?: 'cyan' | 'green' | 'gold' | 'red'
  valueClass?: string
}>(), {
  accent: 'cyan',
  valueClass: '',
})
</script>

<style lang="scss" scoped>
.metric-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
}

.metric-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--accent-cyan-dim);
  flex-shrink: 0;

  svg {
    width: 24px;
    height: 24px;
    stroke: var(--accent-cyan);
  }

  &.green {
    background: var(--accent-green-dim);
    svg { stroke: var(--accent-green); }
  }

  &.red {
    background: var(--accent-red-dim);
    svg { stroke: var(--accent-red); }
  }

  &.gold {
    background: var(--accent-gold-dim);
    svg { stroke: var(--accent-gold); }
  }
}

.metric-label {
  font-size: 12px;
  color: var(--text-tertiary);
  margin-bottom: 4px;
}

.metric-value {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
}
</style>
