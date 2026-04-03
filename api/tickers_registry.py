"""
可交易 / 可展示标的列表 — 单一数据源。
优先读取 data/watchlist.json（UTF-8），便于后续替换为数据库同步脚本写入同一文件。
文件变更后会在下一次请求时自动重新加载（按 mtime 缓存）。
"""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parent.parent
_WATCHLIST_PATH = _ROOT / "data" / "watchlist.json"

_DEFAULT: list[dict[str, Any]] = [
    {"ticker": "AAPL", "name": "Apple Inc.", "sector": "科技"},
    {"ticker": "MSFT", "name": "Microsoft Corp.", "sector": "科技"},
    {"ticker": "GOOGL", "name": "Alphabet Inc.", "sector": "科技"},
    {"ticker": "NVDA", "name": "NVIDIA Corp.", "sector": "科技"},
    {"ticker": "AMZN", "name": "Amazon.com Inc.", "sector": "消费"},
    {"ticker": "META", "name": "Meta Platforms", "sector": "科技"},
    {"ticker": "TSLA", "name": "Tesla Inc.", "sector": "汽车"},
    {"ticker": "JPM", "name": "JPMorgan Chase", "sector": "金融"},
    {"ticker": "V", "name": "Visa Inc.", "sector": "金融"},
    {"ticker": "JNJ", "name": "Johnson & Johnson", "sector": "医药"},
    {"ticker": "WMT", "name": "Walmart Inc.", "sector": "消费"},
    {"ticker": "PG", "name": "Procter & Gamble", "sector": "消费"},
    {"ticker": "MA", "name": "Mastercard Inc.", "sector": "金融"},
    {"ticker": "UNH", "name": "UnitedHealth Group", "sector": "医药"},
    {"ticker": "HD", "name": "Home Depot Inc.", "sector": "消费"},
    {"ticker": "DIS", "name": "Walt Disney Co.", "sector": "传媒"},
]

_cache_list: list[dict[str, Any]] | None = None
_cache_mtime: float | None = None


def load_tickers() -> list[dict[str, Any]]:
    """返回标的列表；watchlist.json 存在则使用（字段至少含 ticker、name）。"""
    global _cache_list, _cache_mtime
    path = _WATCHLIST_PATH
    if path.is_file():
        try:
            mtime = path.stat().st_mtime
            if _cache_list is not None and _cache_mtime == mtime:
                return _cache_list
            raw = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(raw, list) and len(raw) > 0:
                out = []
                for row in raw:
                    if not isinstance(row, dict):
                        continue
                    t = str(row.get("ticker", "")).strip().upper()
                    if not t:
                        continue
                    out.append({
                        "ticker": t,
                        "name": str(row.get("name", t)),
                        "sector": str(row.get("sector", "—")),
                    })
                if out:
                    _cache_list = out
                    _cache_mtime = mtime
                    return out
        except Exception:
            pass
    _cache_list = [dict(x) for x in _DEFAULT]
    _cache_mtime = None
    return _cache_list


def valid_ticker_set() -> set[str]:
    return {t["ticker"] for t in load_tickers()}


def enrich_ticker_row(t: dict[str, Any], price: float) -> dict[str, Any]:
    """为前端行情条附加现价与涨跌幅（演示用随机小幅波动）。"""
    rng = random.Random(hash(t["ticker"]) % (2**32))
    change = round(rng.uniform(-3.5, 3.5), 2)
    return {
        **t,
        "price": round(price, 2),
        "change_pct": change,
    }
