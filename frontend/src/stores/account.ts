/**
 * Account Pinia Store — 严格类型版
 * 管理账户余额、持仓、下单状态
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'
import { apiAccount } from '../api'
import type { AccountBalance } from '../types/api'

export const useAccountStore = defineStore('account', () => {
  // ─── State ────────────────────────────────────────────────────────────────
  const balance = ref<AccountBalance | null>(null)
  const isLoading = ref(false)

  // ─── Actions ──────────────────────────────────────────────────────────────

  /** 获取账户状态 */
  async function fetchBalance() {
    isLoading.value = true
    try {
      const res = await apiAccount.get()
      balance.value = res.data
    } catch {
      // 后端未启动时静默失败，视图层已有 mock 数据兜底
    } finally {
      isLoading.value = false
    }
  }

  /** 重置账户状态 */
  function $reset() {
    balance.value = null
    isLoading.value = false
  }

  return {
    balance,
    isLoading,
    fetchBalance,
    $reset,
  }
})
