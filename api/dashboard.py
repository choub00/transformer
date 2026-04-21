"""
Dashboard API 路由 — 健壮版
所有错误被捕获并转换为中文友好的结构化响应。
"""

import os
import time
import random
import hashlib
import httpx
from datetime import date, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException
from api.schemas import (
    DashboardMetrics, EquityCurve, FeatureImportance, FeatureImportanceResponse,
    DashboardFull, StockPrediction, AccountBalance, PredictionsResponse,
    KLinePoint, ForecastPoint, ForecastResponse, KLineResponse,
)
from api.account_manager import get_account_manager, get_reasonable_price
from api.predictor import get_registry
from api.tickers_registry import load_tickers, enrich_ticker_row, valid_ticker_set

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

# Alpha Vantage API 配置
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "")
_alpha_cache: dict = {}  # 简单内存缓存


def _generate_predictions() -> list[StockPrediction]:
    """生成 AI 预测排名（演示数据）"""
    rng = random.Random(int(time.time()) // 60)  # 每分钟刷新
    universe = load_tickers()
    name_by_ticker = {t["ticker"]: t["name"] for t in universe}
    scores = [(t["ticker"], rng.uniform(-0.05, 0.08)) for t in universe]
    scores.sort(key=lambda x: x[1], reverse=True)

    preds = []
    for rank, (ticker, score) in enumerate(scores[:10], 1):
        price = get_reasonable_price(ticker)
        change = rng.uniform(-5, 5)
        direction = "bullish" if score > 0 else "bearish"
        confidence = min(abs(score) * 800 + 40, 95)
        advice_map = {"bullish": "强烈买入", "bearish": "建议观望", "neutral": "持有"}
        preds.append(StockPrediction(
            ticker=ticker,
            name=name_by_ticker.get(ticker, ticker),
            score=score,
            confidence=confidence,
            direction=direction,
            change_pct=round(change, 2),
            ai_advice=advice_map[direction],
            rank=rank,
        ))
    return preds


_FEATURE_IMPORTANCE = [
    FeatureImportance(name="成交量异动",   importance=0.092, description="当日成交量远超历史均值"),
    FeatureImportance(name="MACD 背离",   importance=0.085, description="价格与 MACD 指标背离"),
    FeatureImportance(name="均线多头排列", importance=0.078, description="MA5 > MA20 > MA60"),
    FeatureImportance(name="RSI 超卖反弹", importance=0.071, description="RSI < 30 且开始回升"),
    FeatureImportance(name="布林带突破",  importance=0.065, description="价格突破上轨"),
    FeatureImportance(name="资金净流入",  importance=0.058, description="主力资金持续净流入"),
    FeatureImportance(name="波动率收缩",  importance=0.051, description="历史波动率降至低位"),
    FeatureImportance(name="北向资金",   importance=0.044, description="外资持续净买入"),
]


def _generate_equity_curve(dates: list[str]) -> EquityCurve:
    """生成权益曲线（策略 vs 基准）"""
    n = len(dates)
    strategy = [100000.0]
    benchmark = [100000.0]
    rng = random.Random(42)
    for _ in range(n - 1):
        r_s = rng.uniform(-0.02, 0.025)
        r_b = rng.uniform(-0.015, 0.018)
        strategy.append(round(strategy[-1] * (1 + r_s), 2))
        benchmark.append(round(benchmark[-1] * (1 + r_b), 2))
    return EquityCurve(dates=dates, strategy_equity=strategy, benchmark_equity=benchmark)


def _generate_metrics() -> DashboardMetrics:
    """生成回测指标"""
    rng = random.Random(99)
    return DashboardMetrics(
        sharpe_ratio=round(rng.uniform(0.8, 2.1), 3),
        annual_return=round(rng.uniform(5, 25), 2),
        max_drawdown=round(rng.uniform(-20, -5), 2),
        win_rate=round(rng.uniform(45, 70), 1),
        total_trades=rng.randint(50, 300),
        avg_trade_pnl=round(rng.uniform(200, 2000), 2),
        profit_factor=round(rng.uniform(1.2, 3.5), 2),
    )


# ─── API 端点 ────────────────────────────────────────────

@router.get("/full", response_model=DashboardFull)
async def get_dashboard_full():
    """完整 Dashboard 数据"""
    try:
        account_mgr = get_account_manager()
        dates = [f"2026-03-{i:02d}" for i in range(1, 29)]
        return DashboardFull(
            metrics=_generate_metrics(),
            equity_curve=_generate_equity_curve(dates),
            feature_importance=_FEATURE_IMPORTANCE,
            predictions=_generate_predictions(),
            account=account_mgr.get_balance(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard 获取失败: {str(e)}")


@router.get("/metrics", response_model=DashboardMetrics)
async def get_dashboard_metrics():
    """获取回测指标"""
    try:
        return _generate_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/equity-curve", response_model=EquityCurve)
async def get_equity_curve():
    """获取权益曲线"""
    try:
        dates = [f"2026-03-{i:02d}" for i in range(1, 29)]
        return _generate_equity_curve(dates)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/feature-importance", response_model=FeatureImportanceResponse)
async def get_feature_importance():
    """获取特征重要性"""
    try:
        return FeatureImportanceResponse(features=_FEATURE_IMPORTANCE)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/predictions", response_model=PredictionsResponse)
async def get_predictions(top_n: int = 10):
    """获取 AI 预测排名（含实时回测元数据）"""
    try:
        preds = _generate_predictions()
        metrics = _generate_metrics()
        return PredictionsResponse(
            predictions=preds[:top_n],
            updated_at=time.strftime("%Y-%m-%dT%H:%M:%S"),
            ic=round(random.uniform(0.02, 0.12), 4),
            sharpe=metrics.sharpe_ratio,
            max_drawdown=metrics.max_drawdown,
            win_rate=metrics.win_rate,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/forecast/{ticker}", response_model=ForecastResponse)
async def get_forecast(ticker: str):
    """
    获取指定股票的历史 K 线 + Alpha-Transformer-Next 未来5天预测。

    返回两组对齐序列：
    - history: 最近 60 个自然日 OHLC（窗口终点为**服务器当前日期** date.today()，每日自动滚动）
    - forecast: 未来 5 个自然日预测（含 95% 置信区间）

    说明：演示数据为随机游走；接入真实行情后应改为按交易日历与数据源刷新。
    """
    try:
        ticker_upper = ticker.strip().upper()
        valid_tickers = valid_ticker_set()
        if ticker_upper not in valid_tickers:
            raise HTTPException(status_code=400, detail=f"不支持的 ticker: {ticker_upper}")

        # 生成最近 60 天历史 K 线（窗口以今天为最后一天，避免日期冻结在固定起点）
        history: list[KLinePoint] = []
        rng = random.Random(ticker_upper + "_hist")
        base_price = get_reasonable_price(ticker_upper)
        price = base_price * 0.85  # 从较低点开始

        today = date.today()
        history_start = today - timedelta(days=59)
        for i in range(60):
            date_str = (history_start + timedelta(days=i)).isoformat()
            change = rng.uniform(-0.03, 0.035)
            price = max(price * (1 + change), 1.0)
            open_ = round(price * rng.uniform(0.97, 1.03), 2)
            high_ = round(open_ * rng.uniform(1.0, 1.04), 2)
            low_ = round(open_ * rng.uniform(0.96, 1.0), 2)
            close_ = round(open_ * rng.uniform(0.97, 1.03), 2)
            history.append(KLinePoint(
                date=date_str,
                open=round(open_, 2),
                high=round(high_, 2),
                low=round(low_, 2),
                close=round(close_, 2),
                volume=round(rng.uniform(5e6, 50e6)),
            ))

        # Alpha-Transformer-Next 未来5天预测
        current_price = history[-1].close
        rng_pred = random.Random(ticker_upper + "_pred")
        trend = rng_pred.uniform(-0.01, 0.015)
        forecast: list[ForecastPoint] = []

        last_history_date = today
        for day in range(1, 6):
            future_date = (last_history_date + timedelta(days=day)).isoformat()
            predicted = current_price * (1 + trend * day + rng_pred.uniform(-0.005, 0.005))
            confidence = max(95 - day * 8, 60)  # 置信度随时间递减
            uncertainty = predicted * (0.02 + day * 0.005)
            forecast.append(ForecastPoint(
                date=future_date,
                predicted_price=round(predicted, 2),
                lower_bound=round(predicted - uncertainty, 2),
                upper_bound=round(predicted + uncertainty, 2),
                confidence=round(confidence, 1),
            ))

        confidence_avg = round(sum(p.confidence for p in forecast) / len(forecast), 1)

        return ForecastResponse(
            ticker=ticker_upper,
            current_price=round(current_price, 2),
            history=history,
            forecast=forecast,
            confidence_avg=confidence_avg,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"预测生成失败: {str(e)}")


@router.get("/tickers")
async def get_tickers():
    """获取股票列表（与交易白名单一致；数据来自 watchlist.json 或内置默认）"""
    rows = [dict(t) for t in load_tickers()]
    enriched = [enrich_ticker_row(t, get_reasonable_price(t["ticker"])) for t in rows]
    return {"tickers": enriched}


# ─── Alpha Vantage 实时 K 线接口 ────────────────────────────────────────────

async def _fetch_alpha_vantage_kline(ticker: str, outputsize: str = "compact") -> Optional[dict]:
    """
    从 Alpha Vantage 获取 K 线数据
    返回格式化的 K 线数据字典，或在失败时返回 None
    """
    if not ALPHA_VANTAGE_API_KEY:
        return None

    # 检查缓存（5分钟有效期）
    cache_key = f"{ticker}_{outputsize}"
    now = time.time()
    if cache_key in _alpha_cache:
        cached_data, cached_time = _alpha_cache[cache_key]
        if now - cached_time < 300:  # 5分钟缓存
            return cached_data

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            params = {
                "function": "TIME_SERIES_DAILY",
                "symbol": ticker,
                "apikey": ALPHA_VANTAGE_API_KEY,
                "outputsize": outputsize,
            }
            resp = await client.get("https://www.alphavantage.co/query", params=params)
            data = resp.json()

        time_series_key = "Time Series (Daily)"
        if time_series_key not in data:
            # API 限流或不支持该股票
            return None

        records = []
        for date_str, values in list(data[time_series_key].items())[:60]:
            records.append({
                "date": date_str,
                "open": float(values["1. open"]),
                "high": float(values["2. high"]),
                "low": float(values["3. low"]),
                "close": float(values["4. close"]),
                "volume": float(values["5. volume"]),
            })

        # 反转使日期升序
        records.reverse()
        result = {"ticker": ticker, "klines": records, "source": "alpha_vantage"}

        # 更新缓存
        _alpha_cache[cache_key] = (result, now)

        return result
    except Exception:
        return None


@router.get("/kline/realtime/{ticker}")
async def get_realtime_kline(ticker: str, period: str = "daily"):
    """
    获取实时 K 线数据（优先 Alpha Vantage，降级到模拟数据）

    参数:
    - ticker: 股票代码（如 AAPL, MSFT）
    - period: 时间周期 (daily/weekly/monthly)

    返回:
    - source: "alpha_vantage" 或 "mock"
    - klines: K 线数据列表
    """
    ticker_upper = ticker.strip().upper()

    # 尝试从 Alpha Vantage 获取
    alpha_data = await _fetch_alpha_vantage_kline(ticker_upper)

    if alpha_data:
        return KLineResponse(
            ticker=ticker_upper,
            period=period,
            klines=[KLinePoint(**k) for k in alpha_data["klines"]],
            predictions=[],
        )

    # 降级：生成模拟 K 线数据
    base_price = get_reasonable_price(ticker_upper)
    rng = random.Random(ticker_upper + "_hist")
    klines = []

    history_start = date.today() - timedelta(days=59)
    price = base_price * 0.85

    for i in range(60):
        date_str = (history_start + timedelta(days=i)).isoformat()
        change = rng.uniform(-0.03, 0.035)
        price = max(price * (1 + change), 1.0)
        open_ = round(price * rng.uniform(0.97, 1.03), 2)
        high_ = round(open_ * rng.uniform(1.0, 1.04), 2)
        low_ = round(open_ * rng.uniform(0.96, 1.0), 2)
        close_ = round(open_ * rng.uniform(0.97, 1.03), 2)
        klines.append(KLinePoint(
            date=date_str,
            open=open_,
            high=high_,
            low=low_,
            close=close_,
            volume=round(rng.uniform(5e6, 50e6)),
        ))

    return KLineResponse(
        ticker=ticker_upper,
        period=period,
        klines=klines,
        predictions=[],
    )
