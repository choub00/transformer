<script setup lang="ts">
interface Props {
  type?: 'chart' | 'text' | 'card' | 'table'
  height?: string
  lines?: number
  animate?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  height: '160px',
  lines: 3,
  animate: true,
})
</script>

<template>
  <!-- 图表骨架屏 -->
  <div v-if="type === 'chart'" class="skeleton-chart" :style="{ height }">
    <div
      v-for="i in 8"
      :key="i"
      class="skeleton-bar"
      :style="{ height: `${30 + Math.random() * 60}%`, animationDelay: `${i * 0.1}s` }"
    />
  </div>

  <!-- 文本骨架屏 -->
  <div v-else-if="type === 'text'" class="skeleton-text">
    <div
      v-for="i in lines"
      :key="i"
      class="skeleton-line"
      :class="i === lines ? 'w-3/4' : 'w-full'"
      :style="{ animationDelay: `${i * 0.05}s` }"
    />
  </div>

  <!-- 卡片骨架屏 -->
  <div v-else-if="type === 'card'" class="skeleton-card">
    <div class="skeleton-card-header">
      <div class="skeleton-block" style="width: 40px; height: 40px; border-radius: 50%;" />
      <div class="skeleton-text" style="flex: 1;">
        <div class="skeleton-line" style="width: 60%;" />
        <div class="skeleton-line" style="width: 40%; height: 12px; margin-top: 8px;" />
      </div>
    </div>
    <div class="skeleton-card-body">
      <div class="skeleton-block" style="height: 80px;" />
    </div>
  </div>

  <!-- 表格骨架屏 -->
  <div v-else-if="type === 'table'" class="skeleton-table">
    <div class="skeleton-table-header">
      <div class="skeleton-line" style="width: 15%;" />
      <div class="skeleton-line" style="width: 25%;" />
      <div class="skeleton-line" style="width: 20%;" />
      <div class="skeleton-line" style="width: 20%;" />
      <div class="skeleton-line" style="width: 20%;" />
    </div>
    <div v-for="i in 5" :key="i" class="skeleton-table-row" :style="{ animationDelay: `${i * 0.1}s` }">
      <div class="skeleton-line" style="width: 15%;" />
      <div class="skeleton-line" style="width: 25%;" />
      <div class="skeleton-line" style="width: 20%;" />
      <div class="skeleton-line" style="width: 20%;" />
      <div class="skeleton-line" style="width: 20%;" />
    </div>
  </div>
</template>

<style scoped>
.skeleton-chart {
  display: flex;
  align-items: flex-end;
  gap: 4px;
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
}

.skeleton-bar {
  flex: 1;
  background: var(--bg-tertiary);
  border-radius: var(--radius-sm) var(--radius-sm) 0 0;
  position: relative;
  overflow: hidden;
}

.skeleton-bar::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.04) 50%, transparent 100%);
  background-size: 200% 100%;
  animation: skeleton-shimmer 1.8s ease-in-out infinite;
}

.skeleton-text {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px;
}

.skeleton-line {
  height: 16px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-sm);
  position: relative;
  overflow: hidden;
}

.skeleton-line::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.04) 50%, transparent 100%);
  background-size: 200% 100%;
  animation: skeleton-shimmer 1.5s ease-in-out infinite;
}

.skeleton-block {
  background: var(--bg-tertiary);
  border-radius: var(--radius-md);
  position: relative;
  overflow: hidden;
}

.skeleton-block::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.04) 50%, transparent 100%);
  background-size: 200% 100%;
  animation: skeleton-shimmer 1.5s ease-in-out infinite;
}

.skeleton-card {
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-lg);
  padding: 16px;
}

.skeleton-card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.skeleton-card-body {
  margin-top: 12px;
}

.skeleton-table {
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  padding: 16px;
}

.skeleton-table-header {
  display: flex;
  gap: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-default);
  margin-bottom: 8px;
}

.skeleton-table-row {
  display: flex;
  gap: 16px;
  padding: 12px 0;
  border-bottom: 1px solid var(--border-default);
  position: relative;
  overflow: hidden;
}

.skeleton-table-row::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.03) 50%, transparent 100%);
  background-size: 200% 100%;
  animation: skeleton-shimmer 1.5s ease-in-out infinite;
}

.w-full { width: 100%; }
.w-3\/4 { width: 75%; }
.w-3\/5 { width: 60%; }
.w-2\/5 { width: 40%; }

@keyframes skeleton-shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
</style>
