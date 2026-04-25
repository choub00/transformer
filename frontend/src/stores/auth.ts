import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '../api'

export interface UserInfo {
  id: number
  username: string
  email: string
  is_active: boolean
  is_admin: boolean
  created_at: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  user: UserInfo
}

const STORAGE_KEY_TOKEN = 'at_access_token'
const STORAGE_KEY_REFRESH = 'at_refresh_token'
const STORAGE_KEY_USER = 'at_user'

function loadFromStorage() {
  return {
    token: localStorage.getItem(STORAGE_KEY_TOKEN) || '',
    refreshToken: localStorage.getItem(STORAGE_KEY_REFRESH) || '',
    user: (() => {
      const raw = localStorage.getItem(STORAGE_KEY_USER)
      return raw ? (JSON.parse(raw) as UserInfo) : null
    })(),
  }
}

function saveToStorage(token: string, refreshToken: string, user: UserInfo) {
  localStorage.setItem(STORAGE_KEY_TOKEN, token)
  localStorage.setItem(STORAGE_KEY_REFRESH, refreshToken)
  localStorage.setItem(STORAGE_KEY_USER, JSON.stringify(user))
}

function clearStorage() {
  localStorage.removeItem(STORAGE_KEY_TOKEN)
  localStorage.removeItem(STORAGE_KEY_REFRESH)
  localStorage.removeItem(STORAGE_KEY_USER)
}

export const useAuthStore = defineStore('auth', () => {
  const { token: initToken, refreshToken: initRefresh, user: initUser } = loadFromStorage()

  const token = ref(initToken)
  const refreshToken = ref(initRefresh)
  const user = ref<UserInfo | null>(initUser)
  const isLoading = ref(false)
  const errorMsg = ref('')

  const isAuthenticated = computed(() => !!token.value && !!user.value)

  async function login(usernameOrEmail: string, password: string) {
    isLoading.value = true
    errorMsg.value = ''
    try {
      const res = await api.post<TokenResponse>('/auth/login', {
        username_or_email: usernameOrEmail,
        password,
      })
      const { access_token, refresh_token, user: userData } = res.data
      token.value = access_token
      refreshToken.value = refresh_token
      user.value = userData
      saveToStorage(access_token, refresh_token, userData)
      return true
    } catch (err: any) {
      const detail = err.response?.data?.detail || err.message || '登录失败'
      errorMsg.value = detail
      return false
    } finally {
      isLoading.value = false
    }
  }

  async function register(username: string, email: string, password: string) {
    isLoading.value = true
    errorMsg.value = ''
    try {
      const res = await api.post<TokenResponse>('/auth/register', {
        username,
        email,
        password,
      })
      const { access_token, refresh_token, user: userData } = res.data
      token.value = access_token
      refreshToken.value = refresh_token
      user.value = userData
      saveToStorage(access_token, refresh_token, userData)
      return true
    } catch (err: any) {
      const detail = err.response?.data?.detail || err.message || '注册失败'
      errorMsg.value = detail
      return false
    } finally {
      isLoading.value = false
    }
  }

  async function refreshAccessToken() {
    if (!refreshToken.value) return false
    try {
      const res = await api.post<TokenResponse>('/auth/refresh', {
        refresh_token: refreshToken.value,
      })
      const { access_token, refresh_token, user: userData } = res.data
      token.value = access_token
      refreshToken.value = refresh_token
      user.value = userData
      saveToStorage(access_token, refresh_token, userData)
      return true
    } catch {
      logout()
      return false
    }
  }

  async function fetchCurrentUser() {
    if (!token.value) return
    try {
      const res = await api.get<UserInfo>('/auth/me')
      user.value = res.data
      const stored = localStorage.getItem(STORAGE_KEY_USER)
      if (stored) {
        const old = JSON.parse(stored) as UserInfo
        saveToStorage(token.value, refreshToken.value, { ...old, ...res.data })
      }
    } catch {
      // token 失效
    }
  }

  function logout() {
    token.value = ''
    refreshToken.value = ''
    user.value = null
    errorMsg.value = ''
    clearStorage()
  }

  return {
    token,
    refreshToken,
    user,
    isLoading,
    errorMsg,
    isAuthenticated,
    login,
    register,
    refreshAccessToken,
    fetchCurrentUser,
    logout,
  }
})
