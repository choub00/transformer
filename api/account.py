"""
账户 API 路由
"""

import time
from fastapi import APIRouter, HTTPException
from api.schemas import AccountBalance, AccountConfig
from api.account_manager import get_account_manager

router = APIRouter(prefix="/account", tags=["Account"])


@router.get("", response_model=AccountBalance)
async def get_account():
    """获取账户状态"""
    try:
        return get_account_manager().get_balance()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/config")
async def configure_account(cfg: AccountConfig):
    """修改账户配置"""
    try:
        mgr = get_account_manager()
        mgr.init_cash = cfg.init_cash
        mgr.fee_rate = cfg.fee_rate
        mgr.stop_loss_pct = cfg.stop_loss_pct
        mgr.top_n = cfg.top_n
        return {"success": True, "message": "配置已更新"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset")
async def reset_account():
    """重置账户"""
    try:
        get_account_manager().reset()
        return {"success": True, "message": "账户已重置"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
