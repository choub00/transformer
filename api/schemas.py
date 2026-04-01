"""
Pydantic 数据模型 — 所有 API 请求/响应的类型安全定义
"""

from pydantic import BaseModel, Field
from typing import Optional


# ─────────────────────────────────────────────────────────────────────────────
# 账户
# ─────────────────────────────────────────────────────────────────────────────

class AccountConfig(BaseModel):
    init_cash: float = Field(100_000.0, ge=0, description="初始资金")
    fee_rate: float = Field(0.0015, ge=0, le=0.1, description="手续费率（单边）")
    stop_loss_pct: float = Field(0.08, ge=0, le=1.0, description="止损比例")
    top_n: int = Field(2, ge=1, le=10, description="每次做多/做空的资产数量")


class Position(BaseModel):
    ticker: str
    quantity: int = Field(..., ge=0)
    entry_price: float = Field(..., gt=0)
    current_price: float = Field(..., gt=0)
    market_value: float = Field(..., ge=0)
    unrealized_pnl: float
    unrealized_pnl_pct: float
    ai_advice: str = "持有"
    direction: str = "long"


class AccountBalance(BaseModel):
    total_assets: float
    cash: float
    init_cash: float
    portfolio_value: float
    total_pnl: float
    total_return_pct: float
    available_cash: float
    positions_count: int
    total_fees: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    daily_pnl: float
    daily_trades: int
    positions: list[Position] = []
    equity_curve: list[dict] = []
    updated_at: str = ""


# ─────────────────────────────────────────────────────────────────────────────
# 市场 & 预测
# ─────────────────────────────────────────────────────────────────────────────

class StockPrediction(BaseModel):
    ticker: str
    name: str
    score: float
    confidence: float = Field(..., ge=0, le=100)
    direction: str  # bullish / bearish / neutral
    change_pct: float
    ai_advice: str
    rank: int = 0


class KLinePoint(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: float


class KLineResponse(BaseModel):
    ticker: str
    period: str
    klines: list[KLinePoint]
    predictions: list[dict] = []  # AI 预测数据


class ForecastPoint(BaseModel):
    """单日预测数据点"""
    date: str
    predicted_price: float
    lower_bound: float  # 95% 置信区间下界
    upper_bound: float  # 95% 置信区间上界
    confidence: float = Field(..., ge=0, le=100)


class ForecastResponse(BaseModel):
    """
    /forecast/{ticker} 响应
    两组对齐序列：历史 OHLC（最近60天）+ Alpha-Transformer-Next 预测（未来5天）
    """
    ticker: str
    current_price: float
    # 历史 K 线（最近60天）
    history: list[KLinePoint]
    # 模型预测（未来5天）
    forecast: list[ForecastPoint]
    # 模型元数据
    model_version: str = "AlphaTransformer-2026"
    confidence_avg: float = Field(..., ge=0, le=100)


class TickerList(BaseModel):
    tickers: list[dict]  # [{ticker, name, sector, price}]


# ─────────────────────────────────────────────────────────────────────────────
# 交易
# ─────────────────────────────────────────────────────────────────────────────

class OrderRequest(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=20)
    side: str = Field(..., pattern="^(buy|sell)$")
    quantity: int = Field(..., ge=1)
    price: Optional[float] = Field(None, gt=0, description="限价（不填则市价）")


class OrderResponse(BaseModel):
    order_id: str
    ticker: str
    side: str
    quantity: int
    price: float
    fee: float
    total_cost: float
    timestamp: str
    status: str  # filled / pending / rejected


class DelayedOrderRequest(BaseModel):
    ticker: str = Field(..., min_length=1)
    side: str = Field(..., pattern="^(buy|sell)$")
    quantity: int = Field(..., ge=1)
    ai_score: Optional[float] = None


class TradeLog(BaseModel):
    date: str
    ticker: str
    side: str
    quantity: int
    price: float
    fee: float
    pnl: Optional[float] = None


class TradeHistory(BaseModel):
    trades: list[TradeLog]
    total: int


# ─────────────────────────────────────────────────────────────────────────────
# 自动交易
# ─────────────────────────────────────────────────────────────────────────────

class AutoTradeStart(BaseModel):
    interval: int = Field(300, ge=60, description="轮询间隔（秒）")
    top_n: int = Field(2, ge=1, le=10)
    stop_loss_pct: float = Field(0.08, ge=0, le=1.0)


class AutoTradeStatus(BaseModel):
    enabled: bool
    interval: int
    top_n: int
    last_run: Optional[str] = None
    signals: list[dict] = []


class AISignal(BaseModel):
    ticker: str
    ai_score: float
    direction: str  # bullish / bearish
    confidence: float
    reason: str


# ─────────────────────────────────────────────────────────────────────────────
# Dashboard
# ─────────────────────────────────────────────────────────────────────────────

class DashboardMetrics(BaseModel):
    sharpe_ratio: float
    annual_return: float
    max_drawdown: float
    win_rate: float
    total_trades: int
    avg_trade_pnl: float
    profit_factor: float


class EquityCurve(BaseModel):
    dates: list[str]
    strategy_equity: list[float]
    benchmark_equity: list[float]


class FeatureImportance(BaseModel):
    name: str
    importance: float
    description: str = ""


class FeatureImportanceResponse(BaseModel):
    features: list[FeatureImportance]


class PredictionsResponse(BaseModel):
    predictions: list[StockPrediction]
    updated_at: str = ""
    # 回测元数据（2026 规范：每次预测返回实时回测统计）
    ic: float = Field(0.0, description="Information Coefficient（信息系数）")
    sharpe: float = Field(0.0, description="年化 Sharpe Ratio")
    max_drawdown: float = Field(0.0, description="最大回撤（%）")
    win_rate: float = Field(0.0, ge=0, le=100, description="胜率（%）")


class DashboardFull(BaseModel):
    metrics: DashboardMetrics
    equity_curve: EquityCurve
    feature_importance: list[FeatureImportance]
    predictions: list[StockPrediction]
    account: AccountBalance


# ─────────────────────────────────────────────────────────────────────────────
# 通用
# ─────────────────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_device: str
    uptime_seconds: float


class ErrorResponse(BaseModel):
    error: str
    detail: str
    code: str  # e.g. "MODEL_NOT_LOADED", "INVALID_TICKER", "INSUFFICIENT_FUNDS"
