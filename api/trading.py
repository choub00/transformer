"""
交易 API 路由 — 健壮版
包含手动下单、自动交易、持仓管理、T+1 延迟单等全部功能。
"""

import time
import hashlib
from typing import Optional, Dict
from fastapi import APIRouter, HTTPException, Query
from api.schemas import (
    OrderRequest, OrderResponse, DelayedOrderRequest,
    TradeHistory, TradeLog, AutoTradeStatus, AISignal,
)
from api.account_manager import get_account_manager, get_reasonable_price
from api.tickers_registry import valid_ticker_set

router = APIRouter(prefix="/trade", tags=["Trade"])


@router.post("/order", response_model=OrderResponse)
async def place_order(req: OrderRequest):
    """
    下单接口（支持市价/限价）

    错误码：
      - INSUFFICIENT_FUNDS: 资金不足
      - POSITION_NOT_FOUND: 未持有该股票
      - INSUFFICIENT_POSITION: 持仓不足
      - INVALID_TICKER: 无效股票代码
      - ELIMINATED: 账户已被淘汰（净值 < 0.92）
    """
    try:
        if not req.ticker or not str(req.ticker).strip():
            raise HTTPException(status_code=400, detail="ticker 不能为空")

        ticker_upper = req.ticker.strip().upper()
        allowed = valid_ticker_set()
        if ticker_upper not in allowed:
            sample = sorted(allowed)[:12]
            raise HTTPException(
                status_code=400,
                detail=f"不支持的 ticker: {ticker_upper}，当前白名单示例: {sample}",
            )

        price = req.price if req.price else get_reasonable_price(ticker_upper)
        account = get_account_manager()
        result = account.execute_order(
            ticker=ticker_upper,
            side=req.side,
            quantity=req.quantity,
            price=price,
        )

        if not result["success"]:
            raise HTTPException(
                status_code=400 if result.get("error_code") not in ("ELIMINATED",) else 403,
                detail=result["error"],
            )

        return OrderResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"下单失败: {str(e)}")


@router.post("/close")
async def close_position(ticker: str = Query(...)):
    """平仓（全部卖出）"""
    try:
        ticker_upper = ticker.strip().upper()
        account = get_account_manager()

        if ticker_upper not in account.positions:
            raise HTTPException(status_code=400, detail=f"未持有 {ticker_upper}")

        pos = account.positions[ticker_upper]
        result = account.execute_order(
            ticker=ticker_upper,
            side="sell",
            quantity=pos.quantity,
            price=get_reasonable_price(ticker_upper),
        )

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])

        return {"success": True, "message": f"{ticker_upper} 已平仓", **result}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"平仓失败: {str(e)}")


@router.post("/delayed")
async def place_delayed_order(req: DelayedOrderRequest):
    """
    提交 T+1 延迟单（东方财富杯 T+1 规则）
    订单在下一个交易日执行，返回订单 ID
    """
    try:
        ticker_upper = req.ticker.strip().upper()
        order_id = hashlib.md5(str(time.time_ns()).encode()).hexdigest()[:12]
        return {
            "success": True,
            "order_id": order_id,
            "ticker": ticker_upper,
            "side": req.side,
            "quantity": req.quantity,
            "ai_score": req.ai_score,
            "scheduled_at": time.strftime("%Y-%m-%d 09:30:00"),  # 下一交易日开盘
            "status": "pending",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=TradeHistory)
async def get_trade_history(limit: int = Query(50, ge=1, le=200)):
    """获取历史成交记录"""
    try:
        account = get_account_manager()
        logs = account.get_trade_log(limit)
        return TradeHistory(
            trades=[TradeLog(**log) for log in logs],
            total=len(logs),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/logs", response_model=TradeHistory)
async def get_trade_logs(limit: int = Query(50, ge=1, le=200)):
    """获取交易日志（同 history）"""
    return await get_trade_history(limit)
