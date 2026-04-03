import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useTickerStore = defineStore('ticker', () => {
  const selectedTicker = ref<string>('AAPL')
  const selectedTickerName = ref<string>('Apple Inc.')
  function selectTicker(ticker: string, name?: string) {
    selectedTicker.value = ticker.toUpperCase().trim()
    if (name) {
      selectedTickerName.value = name
    }
  }
  return { selectedTicker, selectedTickerName, selectTicker }
})
