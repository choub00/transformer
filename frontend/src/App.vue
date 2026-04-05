<template>
  <el-config-provider :locale="zhCn">
    <div class="app-container">
      <!-- 背景装饰 -->
      <div class="bg-effects">
        <div class="bg-gradient"></div>
        <div class="bg-grid"></div>
        <div class="bg-glow bg-glow-1"></div>
        <div class="bg-glow bg-glow-2"></div>
        <canvas v-if="enableNoiseCanvas" ref="noiseCanvasRef" class="noise-canvas"></canvas>
      </div>

      <!-- 顶部导航 -->
      <header class="app-header">
        <div class="header-content">
          <div class="logo">
            <span class="logo-icon" ref="logoIconRef">α</span>
            <span class="logo-text">AlphaTransformer</span>
          </div>

          <nav class="nav-links">
            <router-link to="/" class="nav-item" :class="{ active: $route.path === '/' }">
              <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
                <polyline points="9 22 9 12 15 12 15 22"/>
              </svg>
              <span>仪表盘</span>
            </router-link>

            <router-link to="/analysis" class="nav-item" :class="{ active: $route.path === '/analysis' }">
              <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="20" x2="18" y2="10"/>
                <line x1="12" y1="20" x2="12" y2="4"/>
                <line x1="6" y1="20" x2="6" y2="14"/>
              </svg>
              <span>股票分析</span>
            </router-link>

            <router-link to="/trade" class="nav-item" :class="{ active: $route.path === '/trade' }">
              <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/>
                <polyline points="17 6 23 6 23 12"/>
              </svg>
              <span>模拟交易</span>
            </router-link>
          </nav>

          <!-- 系统状态 -->
          <div class="system-status">
            <div class="status-indicator" :class="{ active: isConnected }">
              <span class="status-dot"></span>
              <span class="status-text">{{ connectionText }}</span>
            </div>
          </div>
        </div>
      </header>

      <!-- 主内容区 -->
      <main class="app-main">
        <router-view v-slot="{ Component, route }">
          <transition name="fade" mode="out-in">
            <component :is="Component" :key="route.fullPath" />
          </transition>
        </router-view>
      </main>

      <!-- 底部状态栏 -->
      <footer class="app-footer">
        <div class="footer-content">
          <div class="footer-item">
            <span class="footer-label">AI 模型状态</span>
            <span class="footer-value status-online">运行中</span>
          </div>
          <div class="footer-item">
            <span class="footer-label">实时行情</span>
            <span class="footer-value">已同步</span>
          </div>
          <div class="footer-item">
            <span class="footer-label">数据更新</span>
            <span class="footer-value">{{ currentTime }}</span>
          </div>
        </div>
      </footer>
    </div>
  </el-config-provider>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import ElConfigProvider from 'element-plus/es/components/config-provider/index'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import gsap from 'gsap'
import { api } from './api'

// ─── Refs ─────────────────────────────────────────────────────────────────
const logoIconRef = ref<HTMLElement | null>(null)
const noiseCanvasRef = ref<HTMLCanvasElement | null>(null)

/** 关闭全屏 Canvas 噪声可避免部分环境下 rAF + putImageData 卡顿或异常 */
const enableNoiseCanvas = false

// ─── State ──────────────────────────────────────────────────────────────
const isConnected = ref(false)
const connectionText = ref('连接检查中')
const currentTime = ref('')
let timeInterval: number | undefined
let noiseAnimationId: number | undefined
let healthInterval: number | undefined

// ─── WebGL 噪声背景 ────────────────────────────────────────────────────
const initNoiseBackground = () => {
  const canvas = noiseCanvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  canvas.width = window.innerWidth
  canvas.height = window.innerHeight

  let frame = 0
  const W = canvas.width
  const H = canvas.height

  const animate = () => {
    // 每 3 帧更新一次（节省性能）
    if (frame % 3 === 0) {
      const imageData = ctx.createImageData(W, H)
      const data = imageData.data

      for (let i = 0; i < data.length; i += 4) {
        const noise = Math.random() * 255
        data[i] = noise       // R
        data[i + 1] = noise  // G
        data[i + 2] = noise  // B
        data[i + 3] = 6      // Alpha — 极低透明度，肉眼几乎不可见但增加质感
      }

      ctx.putImageData(imageData, 0, 0)
    }

    frame++
    noiseAnimationId = requestAnimationFrame(animate)
  }

  animate()
}

// ─── Logo 呼吸光效 ────────────────────────────────────────────────────
const initLogoAnimation = () => {
  if (!logoIconRef.value) return

  // 初始入场：从下方浮入
  gsap.fromTo(logoIconRef.value,
    { y: -10, opacity: 0 },
    { y: 0, opacity: 1, duration: 1, ease: 'power2.out' }
  )

  // 持续光效循环
  gsap.to(logoIconRef.value, {
    textShadow: '0 0 40px rgba(0, 209, 255, 0.9), 0 0 80px rgba(0, 255, 189, 0.4)',
    duration: 2,
    repeat: -1,
    yoyo: true,
    ease: 'sine.inOut',
  })
}

// ─── 导航入场动画 ────────────────────────────────────────────────────
const initNavAnimation = () => {
  gsap.fromTo('.nav-item',
    { y: -16, opacity: 0 },
    { y: 0, opacity: 1, duration: 0.5, stagger: 0.08, ease: 'power2.out' }
  )
  gsap.fromTo('.status-indicator',
    { x: 20, opacity: 0 },
    { x: 0, opacity: 1, duration: 0.6, ease: 'power2.out' }
  )
}

// ─── 更新时间 ──────────────────────────────────────────────────────────
const updateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// ─── 检查连接状态 ────────────────────────────────────────────────────
const checkConnection = async () => {
  try {
    await api.get('/health')
    isConnected.value = true
    connectionText.value = '系统正常'
  } catch {
    isConnected.value = false
    connectionText.value = '后端未连接'
  }
}

// ─── 窗口大小调整 ────────────────────────────────────────────────────
const handleResize = () => {
  const canvas = noiseCanvasRef.value
  if (!canvas) return
  canvas.width = window.innerWidth
  canvas.height = window.innerHeight
}

// ─── 生命周期 ─────────────────────────────────────────────────────────
onMounted(() => {
  if (enableNoiseCanvas) initNoiseBackground()
  initLogoAnimation()
  initNavAnimation()
  updateTime()
  timeInterval = window.setInterval(updateTime, 1000)
  checkConnection()
  healthInterval = window.setInterval(checkConnection, 15000)
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  if (timeInterval) clearInterval(timeInterval)
  if (healthInterval) clearInterval(healthInterval)
  if (noiseAnimationId) cancelAnimationFrame(noiseAnimationId)
  window.removeEventListener('resize', handleResize)
})
</script>

<style lang="scss">
/* App.vue layout-specific styles — global CSS vars are in style.css */

/* ─── 背景效果 ────────────────────────────────────────────────────────────── */
.app-container {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
}

.bg-effects {
  position: fixed;
  inset: 0;
  z-index: -1;
  overflow: hidden;
}

.bg-gradient {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse 80% 50% at 50% -20%, rgba(0, 209, 255, 0.15), transparent),
    radial-gradient(ellipse 60% 40% at 100% 50%, rgba(0, 255, 189, 0.08), transparent),
    radial-gradient(ellipse 60% 40% at 0% 100%, rgba(255, 59, 48, 0.05), transparent),
    var(--bg-primary);
}

.bg-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
  background-size: 50px 50px;
}

.bg-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  opacity: 0.5;
  animation: pulse 8s ease-in-out infinite;
}

.bg-glow-1 {
  width: 600px;
  height: 600px;
  background: var(--accent-cyan-dim);
  top: -200px;
  left: -200px;
  animation-delay: 0s;
}

.bg-glow-2 {
  width: 500px;
  height: 500px;
  background: var(--accent-green-dim);
  bottom: -150px;
  right: -150px;
  animation-delay: -4s;
}

@keyframes pulse {
  0%, 100% { opacity: 0.3; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.1); }
}

.noise-canvas {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  opacity: 0.35;
  mix-blend-mode: overlay;
}

/* ─── 顶部导航 ───────────────────────────────────────────────────────────── */
.app-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--glass-border);
}

.header-content {
  max-width: 1600px;
  margin: 0 auto;
  padding: 0 24px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, var(--accent-cyan), var(--accent-green));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 0 30px var(--accent-cyan-glow);
}

.logo-text {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: -0.5px;
}

.nav-links {
  display: flex;
  gap: 8px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 12px;
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: all var(--transition-fast);
  border: 1px solid transparent;
}

.nav-item:hover {
  color: var(--text-primary);
  background: var(--bg-hover);
}

.nav-item.active {
  color: var(--accent-cyan);
  background: var(--accent-cyan-dim);
  border-color: var(--accent-cyan-dim);
}

.nav-icon {
  width: 18px;
  height: 18px;
}

.system-status {
  display: flex;
  align-items: center;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 20px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--text-tertiary);
  transition: all var(--transition-fast);
}

.status-indicator.active .status-dot {
  background: var(--accent-green);
  box-shadow: 0 0 10px var(--accent-green-glow);
  animation: blink 2s ease-in-out infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.status-text {
  font-size: 12px;
  color: var(--text-secondary);
}

.status-indicator.active .status-text {
  color: var(--accent-green);
}

/* ─── 主内容区 ────────────────────────────────────────────────────────────── */
.app-main {
  position: relative;
  z-index: 1;
  max-width: 1600px;
  margin: 0 auto;
  padding: 24px;
  min-height: calc(100vh - 64px - 48px);
}

/* 页面切换动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity var(--transition-normal), transform var(--transition-normal);
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* ─── 底部状态栏 ───────────────────────────────────────────────────────────── */
.app-footer {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-top: 1px solid var(--glass-border);
  z-index: 100;
}

.footer-content {
  max-width: 1600px;
  margin: 0 auto;
  padding: 0 24px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 48px;
}

.footer-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.footer-label {
  font-size: 12px;
  color: var(--text-tertiary);
}

.footer-value {
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 500;
  font-family: 'JetBrains Mono', monospace;
}

.status-online {
  color: var(--accent-green);
}
</style>
