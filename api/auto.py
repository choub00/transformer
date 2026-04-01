"""
自动交易 API 路由
定时轮询 AlphaTransformer 预测信号，自动执行 Top-K 多空策略。
"""

import time
from fastapi import APIRouter, HTTPException
from api.schemas import AutoTradeStatus, AISignal
from api.account_manager import get_account_manager
from api.dashboard import _generate_predictions, _TICKERS

router = APIRouter(prefix="/auto", tags=["AutoTrade"])

# 内部状态（生产环境建议使用 Redis 持久化）
_auto_state = {
    "enabled": False,
    "interval": 300,  # 5 分钟轮询
    "top_n": 2,
    "last_run": None,
    "signals_generated": 0,
}


@router.get("/status", response_model=AutoTradeStatus)
async def get_auto_status():
    """获取自动交易状态"""
    return AutoTradeStatus(
        enabled=_auto_state["enabled"],
        interval=_auto_state["interval"],
        top_n=_auto_state["top_n"],
        last_run=_auto_state["last_run"],
        signals=[],
    )


@router.post("/start")
async def start_auto_trade(body: dict = {}):
    """启动自动交易"""
    _auto_state["enabled"] = True
    _auto_state["interval"] = body.get("interval", _auto_state["interval"])
    _auto_state["top_n"] = body.get("top_n", _auto_state["top_n"])
    _auto_state["last_run"] = time.strftime("%Y-%m-%d %H:%M:%S")
    return {
        "success": True,
        "message": "AI 自动交易已启动",
        "status": _auto_state,
    }


@router.post("/stop")
async def stop_auto_trade():
    """停止自动交易"""
    _auto_state["enabled"] = False
    return {
        "success": True,
        "message": "AI 自动交易已停止",
        "status": _auto_state,
    }


@router.get("/signals")
async def get_auto_signals():
    """
    获取当前 AI 自动交易信号（Top-K 多空）
    模拟：按 AI 评分排序，取 top_n 做多，做空 bottom_n
    """
    try:
        predictions = _generate_predictions()
        top_n = _auto_state.get("top_n", 2)
        long_signals = predictions[:top_n]
        short_signals = predictions[-top_n:]

        signals = []
        for p in long_signals:
            signals.append({
                "ticker": p.ticker,
                "ai_score": p.score,
                "direction": "bullish",
                "confidence": p.confidence,
                "reason": f"AI 评分 {p.score:.4f}，置信度 {p.confidence:.0f}%",
            })
        for p in short_signals:
            signals.append({
                "ticker": p.ticker,
                "ai_score": p.score,
                "direction": "bearish",
                "confidence": p.confidence,
                "reason": f"AI 评分 {p.score:.4f}，置信度 {p.confidence:.0f}%",
            })

        _auto_state["signals_generated"] += len(signals)
        _auto_state["last_run"] = time.strftime("%Y-%m-%d %H:%M:%S")

        return {
            "signals": signals,
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "count": len(signals),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"信号生成失败: {str(e)}")
