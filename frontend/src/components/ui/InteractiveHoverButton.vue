<template>
  <button
    ref="buttonRef"
    class="interactive-hover-btn"
    :class="[colorClass, { 'is-loading': loading }]"
    :disabled="disabled || loading"
    v-bind="$attrs"
    @mouseenter="handleMouseEnter"
    @mouseleave="handleMouseLeave"
  >
    <span class="btn-text">{{ text }}</span>
    <span class="btn-content" aria-hidden="true">
      <span class="btn-content-text">{{ text }}</span>
      <span class="btn-icon">
        <slot name="icon">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M5 12h14M12 5l7 7-7 7"/>
          </svg>
        </slot>
      </span>
    </span>
  </button>
</template>

<script setup lang="ts">
/**
 * InteractiveHoverButton
 *
 * 鼠标悬停时文字向右滑动显示图标的按钮组件。
 * 改编自 careercompass Next.js 版本。
 */

import { ref, computed } from 'vue'

interface Props {
  text?: string
  color?: 'cyan' | 'green' | 'gold' | 'purple'
  disabled?: boolean
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  text: 'Button',
  color: 'cyan',
  disabled: false,
  loading: false
})

const buttonRef = ref<HTMLButtonElement | null>(null)

const colorClass = computed(() => `btn-${props.color}`)

const handleMouseEnter = (e: MouseEvent) => {
  if (!buttonRef.value) return
  const rect = buttonRef.value.getBoundingClientRect()
  const x = ((e.clientX - rect.left) / rect.width) * 100
  const y = ((e.clientY - rect.top) / rect.height) * 100
  buttonRef.value.style.setProperty('--mouse-x', `${x}%`)
  buttonRef.value.style.setProperty('--mouse-y', `${y}%`)
}

const handleMouseLeave = () => {
  // Reset is optional
}
</script>

<style scoped>
.interactive-hover-btn {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  padding: 14px 28px;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 0.01em;
  cursor: pointer;
  border: none;
  outline: none;
  overflow: hidden;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  background: transparent;
  /* Default cyan */
  background: linear-gradient(135deg, #00D1FF, #00A8CC);
  color: #0D1117;
  box-shadow: 0 4px 15px rgba(0, 209, 255, 0.3);
  font-family: inherit;
  --mouse-x: 50%;
  --mouse-y: 50%;
}

.interactive-hover-btn::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(
    circle at var(--mouse-x) var(--mouse-y),
    rgba(255, 255, 255, 0.25) 0%,
    transparent 60%
  );
  opacity: 0;
  transition: opacity 0.2s ease;
}

.interactive-hover-btn:hover::before {
  opacity: 1;
}

.interactive-hover-btn:hover {
  transform: translateY(-2px);
}

.interactive-hover-btn:active {
  transform: translateY(0) scale(0.97);
}

/* Color variants */
.btn-cyan {
  background: linear-gradient(135deg, #00D1FF, #00A8CC);
  color: #0D1117;
  box-shadow: 0 4px 15px rgba(0, 209, 255, 0.3);
}

.btn-cyan:hover {
  box-shadow: 0 6px 24px rgba(0, 209, 255, 0.5);
}

.btn-green {
  background: linear-gradient(135deg, #00FFBD, #00CC9A);
  color: #0D1117;
  box-shadow: 0 4px 15px rgba(0, 255, 189, 0.3);
}

.btn-green:hover {
  box-shadow: 0 6px 24px rgba(0, 255, 189, 0.5);
}

.btn-gold {
  background: linear-gradient(135deg, #FFD700, #E6B800);
  color: #0D1117;
  box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);
}

.btn-gold:hover {
  box-shadow: 0 6px 24px rgba(255, 215, 0, 0.5);
}

.btn-purple {
  background: linear-gradient(135deg, #a855f7, #7c3aed);
  color: white;
  box-shadow: 0 4px 15px rgba(168, 85, 247, 0.3);
}

.btn-purple:hover {
  box-shadow: 0 6px 24px rgba(168, 85, 247, 0.5);
}

/* Disabled state */
.interactive-hover-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
  box-shadow: none !important;
}

/* Loading state */
.interactive-hover-btn.is-loading {
  cursor: wait;
}

/* ─── Text animation ─────────────────────────────────────────────────────── */
.btn-text {
  position: absolute;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.btn-content {
  display: flex;
  align-items: center;
  gap: 8px;
  transform: translateX(20px);
  opacity: 0;
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.interactive-hover-btn:hover .btn-text {
  transform: translateX(-28px);
  opacity: 0;
}

.interactive-hover-btn:hover .btn-content {
  transform: translateX(0);
  opacity: 1;
}

.btn-icon {
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
