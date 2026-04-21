<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { gsap } from 'gsap'

interface Props {
  value: number
  prefix?: string
  suffix?: string
  decimals?: number
  duration?: number
  enableFlash?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  prefix: '',
  suffix: '',
  decimals: 2,
  duration: 0.6,
  enableFlash: true,
})

const displayValue = ref(formatValue(props.value))
const containerRef = ref<HTMLElement | null>(null)
let currentVal = ref(props.value)
let tween: gsap.core.Tween | null = null

function formatValue(val: number): string {
  const formatted = val.toLocaleString('en-US', {
    minimumFractionDigits: props.decimals,
    maximumFractionDigits: props.decimals,
  })
  return `${props.prefix}${formatted}${props.suffix}`
}

const flashClass = computed(() => {
  if (!props.enableFlash) return ''
  const diff = props.value - currentVal.value
  if (Math.abs(diff) < 0.01) return ''
  return diff > 0 ? 'flash-up' : 'flash-down'
})

watch(() => props.value, (newVal) => {
  const oldVal = currentVal.value

  if (tween) tween.kill()

  const obj = { val: oldVal }
  tween = gsap.to(obj, {
    val: newVal,
    duration: props.duration,
    ease: 'power2.out',
    onUpdate: () => {
      displayValue.value = formatValue(obj.val)
    },
    onComplete: () => {
      currentVal.value = newVal
      displayValue.value = formatValue(newVal)
    },
  })
}, { immediate: false })

watch(() => props.value, (newVal) => {
  currentVal.value = newVal
})
</script>

<template>
  <span ref="containerRef" class="animated-number" :class="flashClass">
    {{ displayValue }}
  </span>
</template>

<style scoped>
.animated-number {
  font-variant-numeric: tabular-nums;
  font-feature-settings: "tnum";
  font-family: 'JetBrains Mono', monospace;
  transition: color 0.15s ease;
}

.animated-number.flash-up {
  animation: number-flash-up 0.4s ease;
}

.animated-number.flash-down {
  animation: number-flash-down 0.4s ease;
}

@keyframes number-flash-up {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); color: var(--up-color); text-shadow: var(--shadow-glow-green); }
}

@keyframes number-flash-down {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); color: var(--down-color); text-shadow: var(--shadow-glow-red); }
}
</style>
