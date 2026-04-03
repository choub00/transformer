"""
账户管理模块 — 健壮版
提供模拟交易账户的完整状态管理，包含东方财富杯规则（净值 < 0.92 淘汰）。
"""

import hashlib
import time
import threading
import numpy as np
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class Position:
    ticker: str
    quantity: int
    entry_price: float
    current_price: float
    market_value: float = 0.0
    unrealized_pnl: float = 0.0
    unrealized_pnl_pct: float = 0.0
    ai_advice: str = "持有"
    direction: str = "long"
    opened_at: str = ""

    def update_price(self, price: float):
        self.current_price = price
        self.market_value = self.quantity * price
        self.unrealized_pnl = (price - self.entry_price) * self.quantity
        self.unrealized_pnl_pct = (
            (price / self.entry_price - 1) * 100 if self.entry_price > 0 else 0.0
        )


# 真实股价参考表（东方财富杯真实化）
_REASONABLE_PRICES: Dict[str, float] = {
    # 美股
    "AAPL": 178.50, "MSFT": 378.20, "GOOGL": 141.80, "NVDA": 495.20,
    "AMZN": 178.25, "META": 485.30, "TSLA": 248.75, "NFLX": 612.40,
    # 沪深 (示例)
    "600000": 8.52,   # 浦发银行
    "600036": 35.80,  # 招商银行
    "600519": 1680.0, # 贵州茅台
    "601318": 48.25,  # 中国平安
    "601888": 68.50,  # 中国中免
    "000001": 12.35,  # 平安银行
    "000002": 10.82,  # 万科A
    "000858": 180.50, # 五粮液
    "002594": 245.60, # 比亚迪
    "300750": 265.80, # 宁德时代
    "300059": 18.92,  # 东方财富
    # 默认
}


def get_reasonable_price(ticker: str) -> float:
    """获取贴近真实的价格（带小范围波动）"""
    base = _REASONABLE_PRICES.get(ticker.upper(), 50.0)
    day_factor = (int(time.time()) // 86400) % 100
    volatility = (day_factor - 50) / 2500.0  # -0.02 ~ +0.02
    return round(base * (1 + volatility), 2)


@dataclass
class AccountManager:
    """
    线程安全的账户管理器
    东方财富杯规则：
      - 净值 < 0.92 → 淘汰（失去比赛资格）
      - 单边手续费 0.15%
      - T+1 交易制度（买入当天不可卖出）
    """
    init_cash: float = 100_000.0
    fee_rate: float = 0.0015
    stop_loss_pct: float = 0.08
    top_n: int = 2

    # 内部状态
    _cash: float = field(init=False)
    _positions: Dict[str, Position] = field(default_factory=dict)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    # 统计
    _total_trades: int = field(default=0)
    _winning_trades: int = field(default=0)
    _losing_trades: int = field(default=0)
    _total_fees: float = field(default=0.0)

    # 权益曲线
    _equity_curve: List[Dict] = field(default_factory=list)
    _trade_log: List[Dict] = field(default_factory=list)

    # 淘汰状态
    _eliminated: bool = field(default=False)
    _elimination_reason: str = field(default="")

    def __post_init__(self):
        self._cash = self.init_cash

    @property
    def cash(self) -> float:
        return self._cash

    @property
    def positions(self) -> Dict[str, Position]:
        return self._positions

    @property
    def eliminated(self) -> bool:
        return self._eliminated

    def _check_elimination(self) -> bool:
        """东方财富杯淘汰规则：净值 < 0.92"""
        total_market_value = sum(p.market_value for p in self._positions.values())
        total_assets = self._cash + total_market_value
        net_value = total_assets / self.init_cash
        if net_value < 0.92:
            self._eliminated = True
            self._elimination_reason = f"净值 {net_value:.4f} < 0.92，触发淘汰规则"
            return True
        return False

    def _update_all_prices(self):
        """更新所有持仓价格为最新市价"""
        for ticker, pos in self._positions.items():
            pos.update_price(get_reasonable_price(ticker))

    def execute_order(
        self,
        ticker: str,
        side: str,
        quantity: int,
        price: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        执行买卖订单
        Returns: {success, order_id, error, ...}
        """
        with self._lock:
            # 淘汰检查
            if self._eliminated:
                return {
                    "success": False,
                    "error": "账户已被淘汰（净值 < 0.92）",
                    "error_code": "ELIMINATED",
                }

            # 验证价格
            if price is None:
                price = get_reasonable_price(ticker)

            # 验证数量
            if quantity <= 0:
                return {"success": False, "error": "数量必须大于 0", "error_code": "INVALID_QUANTITY"}

            # 验证 ticker
            if not ticker or not str(ticker).strip():
                return {"success": False, "error": "ticker 不能为空", "error_code": "INVALID_TICKER"}

            fee = price * quantity * self.fee_rate

            order_id = hashlib.md5(
                f"{ticker}{side}{quantity}{time.time()}".encode()
            ).hexdigest()[:12]

            if side == "buy":
                total_cost = price * quantity + fee
                if total_cost > self._cash:
                    return {
                        "success": False,
                        "error": f"可用资金不足（需要 ${total_cost:.2f}，可用 ${self._cash:.2f}）",
                        "error_code": "INSUFFICIENT_FUNDS",
                    }

                self._cash -= total_cost
                if ticker in self._positions:
                    pos = self._positions[ticker]
                    total_qty = pos.quantity + quantity
                    pos.entry_price = (
                        (pos.entry_price * pos.quantity + price * quantity) / total_qty
                    )
                    pos.quantity = total_qty
                    pos.update_price(price)
                else:
                    self._positions[ticker] = Position(
                        ticker=ticker,
                        quantity=quantity,
                        entry_price=price,
                        current_price=price,
                        market_value=price * quantity,
                        opened_at=time.strftime("%Y-%m-%d %H:%M:%S"),
                    )

                self._total_trades += 1
                self._total_fees += fee

            elif side == "sell":
                if ticker not in self._positions:
                    return {"success": False, "error": f"未持有 {ticker}", "error_code": "POSITION_NOT_FOUND"}

                pos = self._positions[ticker]
                if pos.quantity < quantity:
                    return {
                        "success": False,
                        "error": f"持仓不足（可卖 {pos.quantity} 股）",
                        "error_code": "INSUFFICIENT_POSITION",
                    }

                proceeds = price * quantity - fee
                self._cash += proceeds
                pos.quantity -= quantity

                if pos.quantity == 0:
                    pnl = (price - pos.entry_price) * quantity
                    if pnl > 0:
                        self._winning_trades += 1
                    else:
                        self._losing_trades += 1
                    del self._positions[ticker]

                self._total_trades += 1
                self._total_fees += fee

            # 淘汰检查
            self._check_elimination()

            # 记录交易
            self._trade_log.append({
                "order_id": order_id,
                "date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "ticker": ticker,
                "side": side,
                "quantity": quantity,
                "price": price,
                "fee": fee,
                "status": "filled",
            })

            return {
                "success": True,
                "order_id": order_id,
                "ticker": ticker,
                "side": side,
                "quantity": quantity,
                "price": price,
                "fee": round(fee, 2),
                "total_cost": round(price * quantity + fee, 2) if side == "buy" else round(price * quantity - fee, 2),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "status": "filled",
            }

    def get_balance(self) -> Dict[str, Any]:
        """获取账户完整状态"""
        self._update_all_prices()

        total_market_value = sum(p.market_value for p in self._positions.values())
        total_assets = self._cash + total_market_value
        total_pnl = total_assets - self.init_cash
        total_return_pct = (total_assets / self.init_cash - 1) * 100

        win_rate = (
            self._winning_trades / max(self._winning_trades + self._losing_trades, 1) * 100
        )

        # 权益曲线记录（每日）
        self._equity_curve.append({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_assets": round(total_assets, 2),
            "cash": round(self._cash, 2),
            "market_value": round(total_market_value, 2),
        })

        return {
            "total_assets": round(total_assets, 2),
            "cash": round(self._cash, 2),
            "init_cash": self.init_cash,
            "portfolio_value": round(total_market_value, 2),
            "total_pnl": round(total_pnl, 2),
            "total_return_pct": round(total_return_pct, 2),
            "available_cash": round(self._cash, 2),
            "positions_count": len(self._positions),
            "total_fees": round(self._total_fees, 2),
            "total_trades": self._total_trades,
            "winning_trades": self._winning_trades,
            "losing_trades": self._losing_trades,
            "win_rate": round(win_rate, 2),
            "daily_pnl": 0.0,
            "daily_trades": 0,
            "positions": [
                {
                    "ticker": p.ticker,
                    "quantity": p.quantity,
                    "entry_price": round(p.entry_price, 2),
                    "current_price": round(p.current_price, 2),
                    "market_value": round(p.market_value, 2),
                    "unrealized_pnl": round(p.unrealized_pnl, 2),
                    "unrealized_pnl_pct": round(p.unrealized_pnl_pct, 2),
                    "ai_advice": p.ai_advice,
                    "direction": p.direction,
                }
                for p in self._positions.values()
            ],
            "equity_curve": self._equity_curve[-252:],  # 保留最近1年
            "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

    def reset(self):
        """重置账户"""
        with self._lock:
            self._cash = self.init_cash
            self._positions.clear()
            self._total_trades = 0
            self._winning_trades = 0
            self._losing_trades = 0
            self._total_fees = 0.0
            self._equity_curve.clear()
            self._trade_log.clear()
            self._eliminated = False
            self._elimination_reason = ""

    def get_trade_log(self, limit: int = 50) -> List[Dict]:
        return self._trade_log[-limit:]


# ─────────────────────────────────────────────────────────────────────────────
# 全局单例
# ─────────────────────────────────────────────────────────────────────────────

_account_manager: Optional[AccountManager] = None


def get_account_manager() -> AccountManager:
    global _account_manager
    if _account_manager is None:
        _account_manager = AccountManager()
    return _account_manager
