<script setup lang="ts">
interface Props {
  title: string
  subtitle?: string
  icon?: string
  size?: 'sm' | 'md' | 'lg'
  animated?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  subtitle: '',
  icon: '',
  size: 'md',
  animated: true,
})
</script>

<template>
  <div class="section-header" :class="[`size-${size}`, { animated }]">
    <div class="header-left">
      <span v-if="icon" class="header-icon">{{ icon }}</span>
      <div class="header-text">
        <h3 class="header-title">{{ title }}</h3>
        <p v-if="subtitle" class="header-subtitle">{{ subtitle }}</p>
      </div>
    </div>
    <div class="header-right">
      <slot name="actions" />
    </div>
  </div>
</template>

<style scoped>
.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.section-header.animated {
  animation: fadeInUp var(--transition-normal) ease forwards;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-icon {
  font-size: 18px;
  opacity: 0.8;
}

.header-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.header-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
  line-height: 1.3;
}

.header-subtitle {
  font-size: 12px;
  color: var(--text-tertiary);
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 尺寸变体 */
.size-sm .header-title { font-size: 14px; }
.size-sm .header-icon { font-size: 14px; }

.size-lg .header-title { font-size: 20px; }
.size-lg .header-icon { font-size: 24px; }

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
