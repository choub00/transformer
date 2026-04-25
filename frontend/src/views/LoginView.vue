<template>
  <div class="login-page">
    <!-- Left Panel: Animated Characters & Branding -->
    <div class="left-panel">
      <AnimatedGradientBackground :breathing="true" />

      <!-- Decorative floating orbs -->
      <div class="orb orb-1"></div>
      <div class="orb orb-2"></div>
      <div class="orb orb-3"></div>

      <!-- Branding content -->
      <div class="left-content">
        <div class="brand">
          <div class="brand-icon">
            <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
              <rect width="48" height="48" rx="12" fill="rgba(0,209,255,0.15)" />
              <path d="M24 8L8 32h10v8l6-14l6 14v-8h10L24 8z" fill="url(#iconGrad)" />
              <defs>
                <linearGradient id="iconGrad" x1="8" y1="8" x2="40" y2="40">
                  <stop stop-color="#00D1FF"/>
                  <stop offset="1" stop-color="#00FFBD"/>
                </linearGradient>
              </defs>
            </svg>
          </div>
          <h1 class="brand-name">AlphaTransformer</h1>
          <p class="brand-tagline">AI 驱动的智能股票分析与量化交易平台</p>
        </div>

        <!-- Characters -->
        <div class="characters-wrapper">
          <AnimatedCharacters
            :is-typing="isTyping"
            :show-password="showPassword"
            :password-length="passwordLength"
          />
        </div>

        <!-- Feature pills -->
        <div class="feature-pills">
          <div class="pill">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
            </svg>
            实时行情分析
          </div>
          <div class="pill">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/>
            </svg>
            AI 量化策略
          </div>
          <div class="pill">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="2" y="3" width="20" height="14" rx="2"/><path d="m8 21 4-4 4 4"/>
            </svg>
            模拟交易
          </div>
        </div>

        <p class="privacy-links">
          <a href="#">隐私政策</a>
          <span>·</span>
          <a href="#">服务条款</a>
        </p>
      </div>
    </div>

    <!-- Right Panel: Login Form -->
    <div class="right-panel">
      <div class="login-card">
        <!-- Mobile logo -->
        <div class="mobile-logo">
          <span class="logo-icon-sm">α</span>
          <span>AlphaTransformer</span>
        </div>

        <div class="login-header">
          <h2>欢迎回来</h2>
          <p>登录您的账户，继续探索 AlphaTransformer</p>
        </div>

        <!-- Form -->
        <form class="login-form" @submit.prevent="handleLogin">
          <!-- Error message -->
          <div v-if="errorMsg" class="error-alert">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            {{ errorMsg }}
          </div>

          <!-- Email -->
          <div class="form-group">
            <label class="form-label">邮箱</label>
            <div class="input-wrapper" :class="{ focused: emailFocused }">
              <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/>
              </svg>
              <input
                v-model="form.email"
                type="email"
                placeholder="输入您的邮箱地址"
                class="form-input"
                @focus="emailFocused = true"
                @blur="emailFocused = false"
                autocomplete="email"
              />
            </div>
            <p v-if="errors.email" class="field-error">{{ errors.email }}</p>
          </div>

          <!-- Password -->
          <div class="form-group">
            <label class="form-label">密码</label>
            <div class="input-wrapper" :class="{ focused: passwordFocused }">
              <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>
              </svg>
              <input
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="输入您的密码"
                class="form-input"
                @focus="onPasswordFocus"
                @blur="onPasswordBlur"
                autocomplete="current-password"
              />
              <button type="button" class="toggle-password" @click="showPassword = !showPassword">
                <svg v-if="!showPassword" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-8z"/><circle cx="12" cy="12" r="3"/>
                </svg>
                <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/>
                </svg>
              </button>
            </div>
            <p v-if="errors.password" class="field-error">{{ errors.password }}</p>
          </div>

          <!-- Remember & Forgot -->
          <div class="form-options">
            <label class="remember-me">
              <input v-model="form.remember" type="checkbox" />
              <span class="checkmark"></span>
              记住我
            </label>
            <a href="#" class="forgot-link">忘记密码？</a>
          </div>

          <!-- Submit -->
          <InteractiveHoverButton
            text="登录"
            color="cyan"
            :loading="authStore.isLoading"
            :disabled="authStore.isLoading"
            type="submit"
          />
        </form>

        <!-- Sign up link -->
        <p class="signup-prompt">
          还没有账户？
          <router-link to="/register" class="signup-link">立即注册</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * LoginView
 * AlphaTransformer 登录页面，集成动画角色交互
 */

import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import AnimatedGradientBackground from '../components/ui/AnimatedGradientBackground.vue'
import AnimatedCharacters from '../components/ui/AnimatedCharacters.vue'
import InteractiveHoverButton from '../components/ui/InteractiveHoverButton.vue'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  email: '',
  password: '',
  remember: false,
})

const errors = ref({
  email: '',
  password: '',
})

// 动画角色交互状态
const isTyping = ref(false)
const showPassword = ref(false)
const emailFocused = ref(false)
const passwordFocused = ref(false)

const passwordLength = computed(() => form.value.password.length)
const errorMsg = computed(() => authStore.errorMsg)

// 密码框焦点处理 - 触发角色捂眼睛动画
const onPasswordFocus = () => {
  passwordFocused.value = true
  isTyping.value = true
}

const onPasswordBlur = () => {
  passwordFocused.value = false
  isTyping.value = false
}

const validate = (): boolean => {
  let valid = true
  errors.value = { email: '', password: '' }

  if (!form.value.email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.value.email)) {
    errors.value.email = '请输入有效的邮箱地址'
    valid = false
  }

  if (!form.value.password) {
    errors.value.password = '请输入密码'
    valid = false
  }

  return valid
}

const handleLogin = async () => {
  if (!validate()) return
  const success = await authStore.login(
    form.value.email.trim(),
    form.value.password
  )
  if (success) {
    router.push('/')
  }
}
</script>

<style scoped>
/* ─── Page layout ──────────────────────────────────────────────────────────── */
.login-page {
  display: flex;
  min-height: 100vh;
  width: 100%;
}

/* ─── Left panel ─────────────────────────────────────────────────────────── */
.left-panel {
  position: relative;
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 48px;
  overflow: hidden;
  background: #0a0a0f;
}

.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.35;
  animation: float 6s ease-in-out infinite;
}

.orb-1 {
  width: 300px;
  height: 300px;
  background: rgba(0, 209, 255, 0.4);
  top: -80px;
  left: -60px;
  animation-delay: 0s;
}

.orb-2 {
  width: 240px;
  height: 240px;
  background: rgba(0, 255, 189, 0.3);
  bottom: 80px;
  right: -40px;
  animation-delay: -2s;
}

.orb-3 {
  width: 180px;
  height: 180px;
  background: rgba(168, 85, 247, 0.25);
  top: 40%;
  right: 20%;
  animation-delay: -4s;
}

@keyframes float {
  0%, 100% { transform: translateY(0) scale(1); }
  50% { transform: translateY(-20px) scale(1.05); }
}

.left-content {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 32px;
  max-width: 480px;
  width: 100%;
}

.brand {
  text-align: center;
}

.brand-icon {
  display: flex;
  justify-content: center;
  margin-bottom: 16px;
}

.brand-icon svg {
  width: 64px;
  height: 64px;
  filter: drop-shadow(0 0 20px rgba(0, 209, 255, 0.5));
}

.brand-name {
  font-size: 32px;
  font-weight: 700;
  background: linear-gradient(135deg, #00D1FF, #00FFBD);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 8px;
  letter-spacing: -1px;
}

.brand-tagline {
  font-size: 15px;
  color: #9AA0AB;
  line-height: 1.6;
}

.characters-wrapper {
  display: flex;
  justify-content: center;
  align-items: flex-end;
}

.feature-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
}

.pill {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 9999px;
  background: rgba(0, 209, 255, 0.08);
  border: 1px solid rgba(0, 209, 255, 0.2);
  color: #9AA0AB;
  font-size: 13px;
  font-weight: 500;
  backdrop-filter: blur(8px);
}

.pill svg {
  color: #00D1FF;
}

.privacy-links {
  font-size: 13px;
  color: #6E7681;
}

.privacy-links a {
  color: #6E7681;
  text-decoration: none;
  transition: color 0.2s;
}

.privacy-links a:hover {
  color: #00D1FF;
}

.privacy-links span {
  margin: 0 6px;
}

/* ─── Right panel ─────────────────────────────────────────────────────────── */
.right-panel {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px 32px;
  background: #0D1117;
}

.login-card {
  width: 100%;
  max-width: 420px;
}

.mobile-logo {
  display: none;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #F0F6FC;
  margin-bottom: 32px;
}

.logo-icon-sm {
  font-size: 24px;
  font-weight: 700;
  background: linear-gradient(135deg, #00D1FF, #00FFBD);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.login-header {
  margin-bottom: 32px;
}

.login-header h2 {
  font-size: 28px;
  font-weight: 700;
  color: #F0F6FC;
  margin-bottom: 8px;
}

.login-header p {
  font-size: 14px;
  color: #9AA0AB;
}

/* ─── Form ─────────────────────────────────────────────────────────────── */
.login-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.error-alert {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  border-radius: 10px;
  background: rgba(255, 59, 48, 0.1);
  border: 1px solid rgba(255, 59, 48, 0.3);
  color: #FF3B30;
  font-size: 13px;
}

.field-error {
  font-size: 12px;
  color: #FF3B30;
  margin-top: 4px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-label {
  font-size: 13px;
  font-weight: 500;
  color: #9AA0AB;
}

.input-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 16px;
  height: 48px;
  border-radius: 12px;
  background: rgba(22, 27, 34, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.08);
  transition: border-color 0.2s, box-shadow 0.2s;
}

.input-wrapper.focused {
  border-color: #00D1FF;
  box-shadow: 0 0 0 3px rgba(0, 209, 255, 0.15);
}

.input-icon {
  color: #6E7681;
  flex-shrink: 0;
}

.form-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  font-size: 14px;
  color: #F0F6FC;
  font-family: inherit;
}

.form-input::placeholder {
  color: #6E7681;
}

.toggle-password {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  color: #6E7681;
  display: flex;
  align-items: center;
  transition: color 0.2s;
}

.toggle-password:hover {
  color: #9AA0AB;
}

/* ─── Form options ─────────────────────────────────────────────────────── */
.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: -4px;
}

.remember-me {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #9AA0AB;
  cursor: pointer;
}

.remember-me input {
  width: 16px;
  height: 16px;
  accent-color: #00D1FF;
  cursor: pointer;
}

.forgot-link {
  font-size: 13px;
  color: #00D1FF;
  text-decoration: none;
  transition: opacity 0.2s;
}

.forgot-link:hover {
  opacity: 0.8;
}

/* ─── Sign up ─────────────────────────────────────────────────────────────── */
.signup-prompt {
  text-align: center;
  margin-top: 24px;
  font-size: 14px;
  color: #6E7681;
}

.signup-link {
  color: #00D1FF;
  text-decoration: none;
  font-weight: 500;
  transition: opacity 0.2s;
}

.signup-link:hover {
  opacity: 0.8;
}

/* ─── Responsive ─────────────────────────────────────────────────────────── */
@media (max-width: 900px) {
  .login-page {
    flex-direction: column;
  }

  .left-panel {
    min-height: 40vh;
    padding: 32px 24px;
  }

  .brand-name {
    font-size: 24px;
  }

  .left-content {
    gap: 20px;
  }

  .mobile-logo {
    display: flex;
  }

  .right-panel {
    padding: 32px 24px;
  }

  .brand {
    display: none;
  }
}

@media (max-width: 480px) {
  .left-panel {
    padding: 24px 16px;
  }

  .right-panel {
    padding: 24px 16px;
  }

  .login-header h2 {
    font-size: 24px;
  }

  .feature-pills {
    gap: 8px;
  }

  .pill {
    padding: 6px 12px;
    font-size: 12px;
  }
}
</style>
