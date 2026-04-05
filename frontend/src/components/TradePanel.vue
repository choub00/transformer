<template>
  <div class="trade-panel glass-card">
    <!-- ══════════════════════════════════════════════════════════════════════════
         标题栏
         ══════════════════════════════════════════════════════════════════════════ -->
    <div class="panel-header">
      <div class="ticker-info">
        <span class="ticker-code">{{ ticker }}</span>
        <span class="ticker-name">{{ tickerName }}</span>
      </div>
      <div class="ticker-price">
        <span class="price-label">当前价</span>
        <span class="price-value" :class="priceDirection">
          ${{ formatNumber(currentPrice) }}
          <span class="price-arrow">{{ priceDirection === 'up' ? '▲' : priceDirection === 'down' ? '▼' : '' }}</span>
        </span>
      </div>
    </div>

    <!-- ══════════════════════════════════════════════════════════════════════════
         AI 信心评分区
         ══════════════════════════════════════════════════════════════════════════ -->
    <div class="ai-confidence-section">
      <div class="confidence-header">
        <span class="section-label">&#63720; AI 信心评分</span>
        <span class="confidence-value" :class="confidenceClass">
          {{ aiScore >= 0 ? '+' : '' }}{{ aiScore.toFixed(4) }}
        </span>
      </div>

      <!-- 置信度进度条 -->
      <div class="confidence-bar-wrap">
        <div class="confidence-bar-bg">
          <div
            class="confidence-bar-fill"
            :class="confidenceClass"
            :style="{ width: confidencePct + '%' }"
          ></div>
        </div>
        <div class="confidence-marks">
          <span>0%</span>
          <span>{{ confidencePct }}%</span>
          <span>100%</span>
        </div>
      </div>

      <!-- AI 信号标签 -->
      <div class="ai-signals">
        <span class="signal-tag direction-tag" :class="direction">
          {{ direction === 'bullish' ? '&#128200; 看多' : direction === 'bearish' ? '&#128201; 看空' : '&#10140; 中性' }}
        </span>
        <span class="signal-tag confidence-tag" :class="confidenceClass">
          置信度 {{ confidencePct }}%
        </span>
        <span class="signal-tag risk-tag" :class="riskLevel">
          {{ riskLevel === 'low' ? '低风险' : riskLevel === 'medium' ? '中风险' : '高风险' }}
        </span>
      </div>
    </div>

    <!-- ══════════════════════════════════════════════════════════════════════════
         交易表单
         ══════════════════════════════════════════════════════════════════════════ -->
    <div class="trade-form">
      <!-- 持仓信息 -->
      <div class="position-info" v-if="currentPosition">
        <div class="position-row">
          <span class="pos-label">持仓数量</span>
          <span class="pos-value">{{ currentPosition.quantity }} 股</span>
        </div>
        <div class="position-row">
          <span class="pos-label">持仓市值</span>
          <span class="pos-value">${{ formatNumber(currentPosition.market_value) }}</span>
        </div>
        <div class="position-row">
          <span class="pos-label">浮动盈亏</span>
          <span class="pos-value" :class="currentPosition.unrealized_pnl >= 0 ? 'profit-up' : 'profit-down'">
            {{ currentPosition.unrealized_pnl >= 0 ? '+' : '' }}${{ formatNumber(Math.abs(currentPosition.unrealized_pnl)) }}
            ({{ currentPosition.unrealized_pnl_pct >= 0 ? '+' : '' }}{{ currentPosition.unrealized_pnl_pct.toFixed(2) }}%)
          </span>
        </div>
      </div>

      <!-- 方向选择 -->
      <div class="side-selector">
        <button
          class="side-btn buy-btn"
          :class="{ active: side === 'buy' }"
          @click="side = 'buy'"
        >
          &#128640; 买入
        </button>
        <button
          class="side-btn sell-btn"
          :class="{ active: side === 'sell' }"
          @click="side = 'sell'"
        >
          &#128465; 卖出
        </button>
      </div>

      <!-- 数量输入 -->
      <div class="quantity-group">
        <label class="field-label">数量（股）</label>
        <div class="quantity-input-wrap">
          <button class="qty-btn" @click="adjustQty(-10)">-10</button>
          <input
            v-model.number="quantity"
            type="number"
            min="1"
            step="1"
            class="qty-input"
            placeholder="输入数量"
          />
          <button class="qty-btn" @click="adjustQty(10)">+10</button>
        </div>
        <!-- 快捷数量 -->
        <div class="qty-shortcuts">
          <button class="shortcut-btn" @click="quantity = 100">100</button>
          <button class="shortcut-btn" @click="quantity = 500">500</button>
          <button type="button" class="full-allin-btn" @click="applyMaxBuy" :disabled="side !== 'buy'">
            {{ side === 'buy' ? '按可买上限' : '—' }}
          </button>
        </div>
      </div>

      <!-- ══════════════════════════════════════════════════════════════════════════
           成本预览（0.0015 手续费）
           ══════════════════════════════════════════════════════════════════════════ -->
      <div class="cost-preview" v-if="quantity > 0">
        <div class="cost-row">
          <span class="cost-label">{{ side === 'buy' ? '买入' : '卖出' }}金额</span>
          <span class="cost-value">${{ formatNumber(tradeAmount) }}</span>
        </div>
        <div class="cost-row">
          <span class="cost-label-with-hint" @mouseenter="showFeeHint = true" @mouseleave="showFeeHint = false">
            <span>手续费（0.15%）</span>
            <span class="cost-hint-icon">i</span>
            <div class="fee-tooltip" v-if="showFeeHint">
              <strong>费率说明</strong>
              东方财富杯规则：单边 0.15%，买卖双向收取。<br/>
              不足 $1 按 $1 收取（最低消费）。
            </div>
          </span>
          <span class="cost-value fee">-${{ formatNumber(tradeFee) }}</span>
        </div>
        <div class="cost-divider"></div>
        <div class="cost-row total">
          <span class="cost-label">实际{{ side === 'buy' ? '扣款' : '回款' }}</span>
          <span class="cost-value total">${{ formatNumber(totalCost) }}</span>
        </div>
        <div class="cost-row" v-if="side === 'buy'">
          <span class="cost-label">预计持仓成本</span>
          <span class="cost-value">${{ formatNumber(avgCost) }}/股</span>
        </div>
      </div>

      <!-- 操作按钮 -->
      <button
        class="submit-btn"
        :class="[side, { loading: submitting, disabled: !canSubmit }]"
        :disabled="!canSubmit || submitting"
        @click="handleSubmit"
      >
        <span class="loading-spinner" v-if="submitting"></span>
        <span v-else>
          {{ side === 'buy' ? '&#128640; 确认买入' : '&#128465; 确认卖出' }}
          {{ quantity > 0 ? `${quantity} 股` : '' }}
        </span>
      </button>

      <p class="submit-hint" v-if="errorMsg">{{ errorMsg }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import ElNotification from 'element-plus/es/components/notification/index'
import { apiTrade } from '../api'
import type { Position } from '../types/api'

// ─── Props & Emits ────────────────────────────────────────────────────
const props = defineProps<{
  ticker: string
  tickerName?: string
  currentPrice: number
  aiScore: number
  confidencePct: number
  direction: 'bullish' | 'bearish' | 'neutral'
  riskLevel?: 'low' | 'medium' | 'high'
  currentPosition?: Position | null
  availableCash: number
}>()

const emit = defineEmits<{
  tradeSuccess: []
}>()

// ─── State ─────────────────────────────────────────────────────────────
const side = ref<'buy' | 'sell'>('buy')
const quantity = ref<number>(100)
const submitting = ref(false)
const errorMsg = ref('')
const showFeeHint = ref(false)

// ─── 常量 ─────────────────────────────────────────────────────────────
const FEE_RATE = 0.0015  // 东方财富杯规则：单边 0.15%

// ─── 计算属性 ─────────────────────────────────────────────────────────
const priceDirection = computed(() => {
  if (props.aiScore > 0.02) return 'up'
  if (props.aiScore < -0.02) return 'down'
  return 'neutral'
})

const confidenceClass = computed(() => {
  if (props.confidencePct >= 70) return 'high'
  if (props.confidencePct >= 40) return 'medium'
  return 'low'
})

const tradeAmount = computed(() => props.currentPrice * quantity.value)
const tradeFee = computed(() => tradeAmount.value * FEE_RATE)
const totalCost = computed(() =>
  side.value === 'buy' ? tradeAmount.value + tradeFee.value : tradeAmount.value - tradeFee.value
)
const avgCost = computed(() =>
  totalCost.value / Math.max(quantity.value, 1)
)

const canSubmit = computed(() => {
  if (quantity.value <= 0) return false
  if (side.value === 'buy' && totalCost.value > props.availableCash) return false
  if (side.value === 'sell' && (!props.currentPosition || props.currentPosition.quantity < quantity.value)) return false
  return true
})

// ─── 方法 ─────────────────────────────────────────────────────────────
function adjustQty(delta: number) {
  quantity.value = Math.max(0, quantity.value + delta)
}

function applyMaxBuy() {
  if (side.value !== 'buy') return
  const price = props.currentPrice
  if (price <= 0) return
  const maxShares = Math.floor(props.availableCash / (price * (1 + FEE_RATE)))
  quantity.value = Math.max(0, maxShares)
}

function formatNumber(n: number): string {
  return n.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

async function handleSubmit() {
  if (!canSubmit.value) return
  errorMsg.value = ''
  submitting.value = true

  try {
    const data = await apiTrade.order({
      ticker: props.ticker,
      side: side.value,
      quantity: quantity.value,
      price: props.currentPrice,
    })

    ElNotification({
      title: side.value === 'buy' ? '买入成功' : '卖出成功',
      message: `${props.ticker} × ${quantity.value}股 @ $${formatNumber(data.data.price)}`,
      type: 'success',
      duration: 3000,
    })

    quantity.value = side.value === 'buy' ? 100 : 0
    emit('tradeSuccess')

  } catch {
    errorMsg.value = '下单失败，请重试'
  } finally {
    submitting.value = false
  }
}

// ─── 监听：切换方向时重置数量 ───────────────────────────────────────
watch(side, () => {
  quantity.value = side.value === 'buy' ? 100 : 0
  errorMsg.value = ''
})

watch(
  () => props.ticker,
  () => {
    quantity.value = side.value === 'buy' ? 100 : 0
    errorMsg.value = ''
  },
)
</script>

<style lang="scss" scoped>
.trade-panel {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

// ─── 标题栏 ──────────────────────────────────────────────────────────
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.ticker-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.ticker-code {
  font-size: 20px;
  font-weight: 700;
  font-family: 'JetBrains Mono', monospace;
  color: var(--text-primary);
}

.ticker-name {
  font-size: 12px;
  color: var(--text-tertiary);
}

.ticker-price {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.price-label {
  font-size: 11px;
  color: var(--text-tertiary);
}

.price-value {
  font-size: 20px;
  font-weight: 700;
  font-family: 'JetBrains Mono', monospace;
  color: var(--text-primary);

  &.up { color: var(--accent-green); }
  &.down { color: var(--accent-red); }
}

.price-arrow {
  font-size: 14px;
  margin-left: 4px;
}

// ─── AI 置信度 ────────────────────────────────────────────────────────
.ai-confidence-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.confidence-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.confidence-value {
  font-size: 16px;
  font-weight: 700;
  font-family: 'JetBrains Mono', monospace;

  &.high { color: var(--accent-green); }
  &.medium { color: var(--accent-gold); }
  &.low { color: var(--accent-red); }
}

.confidence-bar-wrap {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.confidence-bar-bg {
  height: 8px;
  background: var(--bg-secondary);
  border-radius: 4px;
  overflow: hidden;
}

.confidence-bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.6s ease;

  &.high { background: linear-gradient(90deg, var(--accent-green), var(--accent-cyan)); }
  &.medium { background: linear-gradient(90deg, var(--accent-gold), #FF9500); }
  &.low { background: linear-gradient(90deg, var(--accent-red), #FF6B6B); }
}

.confidence-marks {
  display: flex;
  justify-content: space-between;
  font-size: 10px;
  color: var(--text-tertiary);
  font-family: 'JetBrains Mono', monospace;
}

.ai-signals {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.signal-tag {
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

.direction-tag {
  &.bullish { background: var(--accent-green-dim); color: var(--accent-green); }
  &.bearish { background: var(--accent-red-dim); color: var(--accent-red); }
  &.neutral { background: var(--bg-secondary); color: var(--text-secondary); }
}

.confidence-tag {
  &.high { background: var(--accent-cyan-dim); color: var(--accent-cyan); }
  &.medium { background: var(--accent-gold-dim); color: var(--accent-gold); }
  &.low { background: var(--accent-red-dim); color: var(--accent-red); }
}

.risk-tag {
  &.low { background: var(--accent-green-dim); color: var(--accent-green); }
  &.medium { background: var(--accent-gold-dim); color: var(--accent-gold); }
  &.high { background: var(--accent-red-dim); color: var(--accent-red); }
}

// ─── 交易表单 ────────────────────────────────────────────────────────
.trade-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.position-info {
  background: var(--bg-secondary);
  border-radius: 10px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.position-row {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
}

.pos-label { color: var(--text-tertiary); }
.pos-value { color: var(--text-primary); font-weight: 500; font-family: 'JetBrains Mono', monospace; }
.pos-value.profit-up { color: var(--accent-red); }
.pos-value.profit-down { color: var(--accent-green); }

// ─── 方向选择 ────────────────────────────────────────────────────────
.side-selector {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.side-btn {
  padding: 12px;
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.16);
  background: rgba(13,17,23,0.82);
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: inset 0 0 0 1px rgba(255,255,255,0.03);
  transition: all 0.2s ease;

  &.buy-btn {
    color: rgba(240,246,252,0.82);
    &:hover {
      border-color: rgba(0,255,189,0.5);
      color: var(--accent-green);
      background: rgba(0,255,189,0.10);
    }
    &.active {
      border-color: rgba(0,255,189,0.7);
      color: var(--accent-green);
      background: rgba(0,255,189,0.14);
      box-shadow: 0 0 0 1px rgba(0,255,189,0.12), 0 10px 24px rgba(0,255,189,0.08);
    }
  }

  &.sell-btn {
    color: rgba(240,246,252,0.82);
    &:hover {
      border-color: rgba(255,59,48,0.5);
      color: var(--accent-red);
      background: rgba(255,59,48,0.10);
    }
    &.active {
      border-color: rgba(255,59,48,0.65);
      color: var(--accent-red);
      background: rgba(255,59,48,0.14);
      box-shadow: 0 0 0 1px rgba(255,59,48,0.12), 0 10px 24px rgba(255,59,48,0.08);
    }
  }
}

// ─── 数量输入（步进器 + 快捷胶囊）────────────────────────────────────
.quantity-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.field-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

// 步进器主行
.quantity-input-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
}

// 步进按钮：≥44×44px 触摸友好
.qty-btn {
  width: 44px;
  height: 44px;
  min-width: 44px;
  flex-shrink: 0;
  border-radius: 10px;
  border: 1px solid rgba(255,255,255,0.16);
  background: rgba(13,17,23,0.82);
  color: var(--text-primary);
  font-size: 18px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
  display: flex;
  align-items: center;
  justify-content: center;

  &:hover {
    border-color: rgba(0,209,255,0.5);
    color: var(--accent-cyan);
    background: rgba(0,209,255,0.10);
  }
  &:active { transform: scale(0.94); }
}

.qty-input {
  flex: 1;
  height: 44px;
  padding: 0 8px;
  border-radius: 10px;
  border: 1px solid var(--border-default);
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 18px;
  font-weight: 700;
  font-family: 'JetBrains Mono', monospace;
  text-align: center;
  outline: none;

  &:focus {
    border-color: var(--accent-cyan);
    box-shadow: 0 0 0 3px var(--accent-cyan-glow);
  }

  &::placeholder { color: var(--text-tertiary); font-weight: 400; }
  &::-webkit-outer-spin-button,
  &::-webkit-inner-spin-button { -webkit-appearance: none; margin: 0; }
}

// 快捷数量：胶囊按钮，选中态填充
.qty-shortcuts {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.shortcut-btn {
  height: 36px;
  padding: 0 12px;
  border-radius: 20px;
  border: 1px solid rgba(255,255,255,0.18);
  background: rgba(13,17,23,0.82);
  color: rgba(240,246,252,0.82);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.18s;
  display: flex;
  align-items: center;
  justify-content: center;

  &:hover:not(:disabled) {
    border-color: rgba(0,209,255,0.5);
    color: var(--accent-cyan);
    background: rgba(0,209,255,0.10);
  }

  &:disabled {
    opacity: 0.35;
    cursor: not-allowed;
  }
}

// 满仓：两次确认文案弱化
.full-allin-btn {
  grid-column: 1 / -1;
  height: 32px;
  padding: 0 12px;
  border-radius: 16px;
  border: 1px dashed rgba(255,255,255,0.22);
  background: rgba(13,17,23,0.72);
  color: rgba(240,246,252,0.68);
  font-size: 11px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.18s;
  letter-spacing: 0.02em;

  &:hover:not(:disabled) {
    border-color: var(--accent-amber, #FFB800);
    color: var(--accent-amber, #FFB800);
    background: rgba(255,184,0,0.08);
  }
  &:disabled { opacity: 0.3; cursor: not-allowed; }
}

// ─── 成本预览（明细 → 分割线 → 实际扣款）──────────────────────────────────
.cost-preview {
  background: var(--bg-secondary);
  border-radius: 12px;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.cost-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;

  &.total {
    padding-top: 10px;
    margin-top: 2px;
    border-top: 2px solid var(--border-hover);
  }
}

.cost-label {
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  gap: 4px;
}

.cost-label-with-hint {
  display: flex;
  align-items: center;
  gap: 5px;
  cursor: pointer;
  position: relative;
}

.cost-hint-icon {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  border: 1px solid var(--text-tertiary);
  color: var(--text-tertiary);
  font-size: 9px;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: help;
  transition: color 0.15s;

  &:hover { color: var(--text-secondary); }
}

.fee-tooltip {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  z-index: 10;
  width: 200px;
  background: var(--bg-card);
  border: 1px solid var(--border-default);
  border-radius: 8px;
  padding: 10px 12px;
  font-size: 11px;
  color: var(--text-secondary);
  line-height: 1.5;
  box-shadow: 0 4px 16px rgba(0,0,0,0.4);
  pointer-events: none;

  strong { color: var(--text-primary); display: block; margin-bottom: 4px; }
}

.cost-value {
  color: var(--text-primary);
  font-family: 'JetBrains Mono', monospace;
  font-weight: 600;
}
.cost-value.fee { color: var(--text-tertiary); }
.cost-value.total { font-weight: 700; font-size: 15px; color: var(--text-primary); }

.cost-divider {
  height: 1px;
  background: transparent;  // 分割线移至 .cost-row.total 内
}

// ─── 提交按钮（高对比 WCAG AA，CTA 层级）────────────────────────────────
.submit-btn {
  padding: 16px;
  border-radius: 12px;
  border: none;
  font-size: 15px;
  font-weight: 700;
  letter-spacing: 0.02em;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 52px;   // 移动端大字友好

  // 买入：深色底 + 近白字（最强对比，WCAG AA+）
  &.buy {
    background: #0D1117;
    color: #F0F6FC;
    border: 2px solid var(--accent-green);
    &:hover:not(:disabled) {
      background: var(--accent-green);
      color: #0D1117;
      box-shadow: 0 0 24px var(--accent-green-glow);
    }
    &:active:not(:disabled) { transform: scale(0.98); }
  }

  // 卖出：琥珀/橙底 + 深色字（危险操作，但与买入同高对比）
  &.sell {
    background: #FF9500;
    color: #3D1800;
    &:hover:not(:disabled) {
      background: #FFB340;
      box-shadow: 0 0 24px rgba(255,149,0,0.5);
    }
    &:active:not(:disabled) { transform: scale(0.98); }
  }

  &.disabled, &:disabled {
    opacity: 0.4;
    cursor: not-allowed;
    pointer-events: none;
  }

  &.loading {
    cursor: wait;
    opacity: 0.8;
  }
}

.submit-hint {
  font-size: 12px;
  color: var(--accent-red);
  text-align: center;
  margin: 0;
}
</style>
