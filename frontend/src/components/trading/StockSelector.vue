<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { api as apiClient } from '../../api'

interface TickerInfo {
  ticker: string
  name: string
  price?: number
  change?: number
  sector?: string
}

interface Props {
  modelValue?: string
  placeholder?: string
  recentLabel?: string
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  placeholder: '搜索股票代码或名称...',
  recentLabel: '最近访问',
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
  'select': [ticker: TickerInfo]
}>()

const RECENT_TICKERS_KEY = 'alpha-transformer:recent-tickers'

const tickerSearch = ref('')
const tickerList = ref<TickerInfo[]>([])
const recentTickers = ref<string[]>([])
const isLoading = ref(false)
const isExpanded = ref(false)

const recentStocks = computed(() =>
  recentTickers.value
    .map((t) => tickerList.value.find((s) => s.ticker === t) || { ticker: t, name: t })
    .filter((s, i, arr) => arr.findIndex((item) => item.ticker === s.ticker) === i)
    .slice(0, 6)
)

const filteredStocks = computed(() => {
  if (!tickerSearch.value) return tickerList.value.slice(0, 20)
  const q = tickerSearch.value.toUpperCase()
  return tickerList.value.filter(
    (s) =>
      s.ticker.toUpperCase().includes(q) ||
      s.name.toUpperCase().includes(q) ||
      s.sector?.toUpperCase().includes(q)
  )
})

async function loadTickers() {
  isLoading.value = true
  try {
    const [dashRes, marketRes] = await Promise.allSettled([
      apiClient.get('/dashboard/tickers'),
      apiClient.get('/market/tickers'),
    ])

    const items: TickerInfo[] = []
    if (dashRes.status === 'fulfilled') {
      for (const t of dashRes.value.data.data ?? []) {
        items.push({ ticker: t.ticker, name: t.name || t.ticker, sector: t.sector })
      }
    }
    if (marketRes.status === 'fulfilled') {
      for (const t of marketRes.value.data.data ?? []) {
        if (!items.find((x) => x.ticker === t.ticker)) {
          items.push({ ticker: t.ticker, name: t.name || t.ticker })
        }
      }
    }
    tickerList.value = items
  } catch {
    tickerList.value = []
  } finally {
    isLoading.value = false
  }
}

function loadRecentTickers() {
  try {
    const raw = localStorage.getItem(RECENT_TICKERS_KEY)
    recentTickers.value = raw ? JSON.parse(raw) : []
  } catch {
    recentTickers.value = []
  }
}

function saveRecentTicker(ticker: string) {
  const updated = [ticker, ...recentTickers.value.filter((t) => t !== ticker)].slice(0, 10)
  recentTickers.value = updated
  try {
    localStorage.setItem(RECENT_TICKERS_KEY, JSON.stringify(updated))
  } catch {}
}

function selectTicker(ticker: string) {
  const stock = tickerList.value.find((s) => s.ticker === ticker)
  emit('update:modelValue', ticker)
  emit('select', stock || { ticker, name: ticker })
  if (stock) {
    saveRecentTicker(ticker)
  }
  tickerSearch.value = ''
  isExpanded.value = false
}

function handleFocus() {
  isExpanded.value = true
  if (tickerList.value.length === 0) {
    void loadTickers()
  }
}

function handleBlur() {
  setTimeout(() => {
    isExpanded.value = false
  }, 200)
}

watch(() => props.modelValue, (val) => {
  if (val && !tickerList.value.find((s) => s.ticker === val)) {
    void loadTickers()
  }
}, { immediate: true })

// 初始化
loadRecentTickers()
void loadTickers()
</script>

<template>
  <div class="stock-selector" :class="{ expanded: isExpanded }">
    <div class="stock-search-row">
      <div class="recent-chips" v-if="!isExpanded && recentStocks.length > 0">
        <span class="recent-label">{{ recentLabel }}</span>
        <button
          v-for="stock in recentStocks"
          :key="stock.ticker"
          class="recent-chip"
          :class="{ active: stock.ticker === modelValue }"
          @click="selectTicker(stock.ticker)"
          type="button"
        >
          {{ stock.ticker }}
        </button>
      </div>

      <div v-if="isExpanded || !recentStocks.length" class="search-input-wrapper">
        <svg class="search-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
        </svg>
        <input
          v-model="tickerSearch"
          type="text"
          class="stock-search"
          :placeholder="placeholder"
          @focus="handleFocus"
          @blur="handleBlur"
          autocomplete="off"
          spellcheck="false"
        />
        <div v-if="isLoading" class="loading-spinner" />
      </div>
    </div>

    <div v-if="isExpanded && filteredStocks.length > 0" class="stock-dropdown">
      <div
        v-for="stock in filteredStocks"
        :key="stock.ticker"
        class="stock-option"
        :class="{ selected: stock.ticker === modelValue }"
        @mousedown.prevent="selectTicker(stock.ticker)"
      >
        <div class="option-main">
          <span class="option-ticker">{{ stock.ticker }}</span>
          <span class="option-name">{{ stock.name }}</span>
        </div>
        <span v-if="stock.sector" class="option-sector">{{ stock.sector }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.stock-selector {
  position: relative;
}

.stock-search-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  transition: border-color var(--transition-fast);
  min-height: 52px;
}

.stock-selector.expanded .stock-search-row {
  border-color: var(--accent-cyan);
  box-shadow: 0 0 0 3px var(--accent-cyan-dim);
}

.recent-label {
  font-size: 11px;
  color: var(--text-tertiary);
  margin-right: 4px;
}

.recent-chip {
  padding: 4px 10px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-full);
  color: var(--text-secondary);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
  font-family: 'JetBrains Mono', monospace;
}

.recent-chip:hover {
  background: var(--accent-cyan-dim);
  border-color: var(--accent-cyan);
  color: var(--accent-cyan);
}

.recent-chip.active {
  background: var(--accent-cyan-dim);
  border-color: var(--accent-cyan);
  color: var(--accent-cyan);
}

.search-input-wrapper {
  position: relative;
  flex: 1;
  min-width: 160px;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 10px;
  color: var(--text-tertiary);
  pointer-events: none;
}

.stock-search {
  width: 100%;
  padding: 8px 10px 8px 32px;
  background: transparent;
  border: none;
  color: var(--text-primary);
  font-size: 14px;
  outline: none;
  font-family: 'JetBrains Mono', monospace;
}

.stock-search::placeholder {
  color: var(--text-tertiary);
}

.loading-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid var(--border-default);
  border-top-color: var(--accent-cyan);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-left: auto;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.stock-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  right: 0;
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  max-height: 300px;
  overflow-y: auto;
  z-index: 1000;
  scrollbar-width: thin;
}

.stock-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  cursor: pointer;
  transition: background-color var(--transition-micro);
  border-bottom: 1px solid var(--border-default);
}

.stock-option:last-child {
  border-bottom: none;
}

.stock-option:hover {
  background: var(--bg-hover);
}

.stock-option.selected {
  background: var(--accent-cyan-dim);
}

.option-main {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.option-ticker {
  font-size: 13px;
  font-weight: 700;
  font-family: 'JetBrains Mono', monospace;
  color: var(--text-primary);
}

.option-name {
  font-size: 11px;
  color: var(--text-tertiary);
}

.option-sector {
  font-size: 10px;
  padding: 2px 6px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-sm);
  color: var(--text-tertiary);
}
</style>
