<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  value: number
  label?: string
  showLabel?: boolean
  animated?: boolean
  size?: 'sm' | 'md' | 'lg'
  colorVariant?: 'cyan' | 'green' | 'gold' | 'red'
}

const props = withDefaults(defineProps<Props>(), {
  label: '',
  showLabel: true,
  animated: true,
  size: 'md',
  colorVariant: 'cyan',
})

const percentage = computed(() => Math.min(Math.max(props.value, 0), 100))

const heightClass = computed(() => {
  switch (props.size) {
    case 'sm': return 'h-2'
    case 'lg': return 'h-3'
    default: return 'h-2.5'
  }
})

const gradientClass = computed(() => {
  switch (props.colorVariant) {
    case 'green': return 'gradient-green'
    case 'gold': return 'gradient-gold'
    case 'red': return 'gradient-red'
    default: return 'gradient-cyan'
  }
})
</script>

<template>
  <div class="confidence-bar-container">
    <div v-if="showLabel && label" class="confidence-label">
      <span class="label-text">{{ label }}</span>
      <span class="label-value">{{ percentage.toFixed(0) }}%</span>
    </div>
    <div class="confidence-track" :class="heightClass">
      <div
        class="confidence-fill"
        :class="[gradientClass, { animated }]"
        :style="{ width: animated ? '0%' : `${percentage}%` }"
        :data-width="`${percentage}%`"
      />
    </div>
  </div>
</template>

<style scoped>
.confidence-bar-container {
  width: 100%;
}

.confidence-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.label-text {
  font-size: 12px;
  color: var(--text-tertiary);
}

.label-value {
  font-size: 12px;
  font-weight: 600;
  font-family: 'JetBrains Mono', monospace;
  color: var(--text-secondary);
}

.confidence-track {
  width: 100%;
  background: var(--bg-primary);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.h-2 { height: 8px; }
.h-2\.5 { height: 10px; }
.h-3 { height: 12px; }

.confidence-fill {
  height: 100%;
  border-radius: var(--radius-full);
  transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.confidence-fill.animated {
  animation: fillExpand 0.8s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}

@keyframes fillExpand {
  from { width: 0; }
  to { width: var(--target-width, 100%); }
}

.confidence-fill.animated[data-width] {
  --target-width: attr(data-width);
}

.gradient-cyan {
  background: linear-gradient(90deg, var(--accent-cyan), var(--accent-green));
}

.gradient-green {
  background: linear-gradient(90deg, var(--accent-green), #00CC9A);
}

.gradient-gold {
  background: linear-gradient(90deg, var(--accent-gold), #FFA500);
}

.gradient-red {
  background: linear-gradient(90deg, var(--accent-red), #CC2F26);
}
</style>
