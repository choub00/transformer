# AlphaTransformer - Project Overview

## Project Summary

AlphaTransformer is a quantitative stock alpha prediction system that uses Transformer models to rank stocks and predict future price trends.

- **Type**: Quantitative Trading / AI Stock Prediction
- **Backend**: Python + FastAPI
- **Frontend**: Vue 3 (to be built)
- **Model**: PatchTSTHybrid (Transformer-based)

---

## Project Structure

```
D:/transformer/
├── Stock Forecast/                    # Backend (Python/FastAPI)
│   ├── api/
│   │   ├── server.py                 # Main FastAPI server
│   │   ├── dashboard.py              # Dashboard API endpoints
│   │   ├── trading.py                # Trading API endpoints
│   │   ├── predictor.py               # AlphaPredictor (model inference)
│   │   ├── account_manager.py         # Account management singleton
│   │   ├── preprocessing.py           # Feature preprocessing
│   │   └── schemas.py                  # Pydantic models
│   ├── models/
│   │   ├── alpha_transformer.py       # PatchTSTHybrid model
│   │   ├── patch_tst.py               # PatchTST components
│   │   └── simple_alpha_net.py        # Simple MLP baseline
│   ├── data/                          # Data processing
│   ├── evaluation/                    # Backtest engine
│   ├── checkpoints/                   # Model weights (.pt, .lgb)
│   ├── configs/
│   │   └── config.yaml               # Model configuration
│   └── requirements.txt
├── frontend/                         # Frontend (Vue 3) - TO BE CREATED
│   ├── src/
│   │   ├── views/                    # Page components
│   │   ├── components/               # Reusable components
│   │   ├── stores/                   # Pinia state management
│   │   ├── api/                     # API client
│   │   └── styles/                  # Theme styles
│   └── package.json
└── .cursor/skills/                  # Agent skills
```

---

## Backend Architecture

### API Endpoints

#### Dashboard APIs (for Vue frontend)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/dashboard/full` | GET | Complete dashboard data |
| `/api/v1/dashboard/equity-curve` | GET | Strategy vs benchmark equity |
| `/api/v1/dashboard/feature-importance` | GET | Top features by importance |
| `/api/v1/dashboard/predictions` | GET | 16 stock predictions |
| `/api/v1/dashboard/ai-insights` | POST | AI investment advice |

#### Trading APIs
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/account/balance` | GET | Account balance + positions |
| `/api/v1/account/config` | POST | Update initial capital/fee |
| `/api/v1/account/reset` | POST | Reset account |
| `/api/v1/trade/manual` | POST | Manual order |
| `/api/v1/trade/auto-toggle` | POST | Toggle AI auto-trading |
| `/api/v1/trade/close-position` | POST | Close position |
| `/api/v1/positions` | GET | Current positions |
| `/api/v1/trade/history` | GET | Trade history |

#### Prediction APIs
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/predict` | POST | Stock ranking prediction |
| `/api/v1/forecast/{ticker}` | GET | K-line + 5-day forecast |
| `/api/v1/health` | GET | Health check |

#### Auto-Trading APIs
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auto-trading/status` | GET | Auto-trading status |
| `/api/v1/auto-trading/start` | POST | Start auto-trading |
| `/api/v1/auto-trading/stop` | POST | Stop auto-trading |
| `/api/v1/auto-trading/logs` | GET | Auto-trading logs |

---

## Data Models

### StockPrediction
```python
{
    "ticker": str,           # Stock symbol
    "rank": int,            # 1-16 ranking
    "score": float,          # Alpha score
    "direction": str,        # bullish/bearish/neutral
    "conf_pct": float,       # Confidence percentage
}
```

### AccountBalance
```python
{
    "cash": float,
    "total_assets": float,
    "total_pnl": float,
    "total_return_pct": float,
    "total_fees": float,
    "positions": [Position],
}
```

### Position
```python
{
    "ticker": str,
    "quantity": float,
    "entry_price": float,
    "current_price": float,
    "market_value": float,
    "unrealized_pnl": float,
    "unrealized_pnl_pct": float,
    "ai_advice": str,
    "ai_score": float,
}
```

---

## Model Features (40 dimensions)

### Price/EMA
`open`, `high`, `low`, `close`, `volume`, `ema_5`, `ema_10`, `ema_20`

### Momentum
`momentum_5`, `momentum_10`, `momentum_20`, `momentum_accel`, `macd`, `macd_signal`, `rsi`

### Volatility
`volatility`, `atr`, `vol_5`, `vol_10`, `vol_20`, `vol_regime`

### Volume
`volume_change`, `volume_surge`

### Bollinger Bands
`bb_upper`, `bb_lower`, `bb_width`

### Bias
`bias_ratio`, `bias_5`, `bias_10`, `bias_20`

### Patterns
`breakout_high`, `breakout_low`, `price_position`

### Cross-Section
`market_return`, `market_vol`, `market_breadth`, `excess_return`, `vol_scaled_return`, `vol_rank`, `ret_rank`

---

## Trading Rules

### Risk Management
- **Single trade limit**: 8% of total assets
- **Max positions**: 10 stocks
- **Daily trade limit**: 20 trades
- **Stop loss**: 5% (auto-sell)
- **Take profit**: 15% (auto-sell)
- **Fee rate**: 0.15% (0.0015)

### East Money Competition Rules (Reference)
- **Tradable**: A-shares (沪深A股)
- **Elimination**: Net value < 0.92 (loss > 8%)
- **Return formula**: Modified Dietz \((1+r_1)(1+r_2)...(1+r_n)-1\)

---

## Frontend Design

### Theme: Bloomberg Terminal Dark Mode

```scss
$bg-primary: #0a1628;     // Deep blue background
$bg-secondary: #132743;   // Card background
$bg-card: #1a3050;        // Component background
$accent-gold: #d4af37;    // Gold for highlights
$accent-green: #00ff88;    // Green for gains
$accent-red: #ff4444;      // Red for losses
```

### UI Framework
- **Element Plus** (Chinese localization)
- **ECharts** for charts
- **Pinia** for state management
- **Vue Router** for navigation

---

## Key Singletons

### AlphaPredictor
- Model inference engine
- Located: `api/predictor.py`
- Methods: `rank_stocks()`, `_run_model()`

### AccountManager
- Account state management
- Located: `api/account_manager.py`
- Methods: `place_order()`, `get_stats()`, `get_mock_price()`

---

## Configuration

### Model Config (`configs/config.yaml`)
```yaml
model:
  name: "PatchTSTHybrid"
  d_model: 128
  n_heads: 4
  d_ff: 256
  patch_len: 16
  stride: 8
  n_layers: 2

training:
  loss_weight_margin: 0.50
  loss_weight_listnet: 0.50
  label_smoothing: 0.05

backtest:
  initial_capital: 100000
  transaction_cost: 0.0002
  top_k: 10
  stop_loss_pct: 0.03
```

---

## Known Issues

1. **Random mock prices**: `get_mock_price()` generates unrealistic prices (50~549 RMB)
2. **Null ticker validation**: Some predictions return null tickers
3. **Feature dimension mismatch**: Can cause 500 errors during inference

---

## Dependencies

### Backend
```
fastapi>=0.100
uvicorn
torch
lightgbm
pandas
numpy
scikit-learn
```

### Frontend (to install)
```
vue@3
vue-router@4
pinia
element-plus
echarts
axios
@vitejs/plugin-vue
typescript
sass
```
