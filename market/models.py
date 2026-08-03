from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class MarketData:
    symbol: str

    live_price: float
    previous_close: float
    day_change_percent: float

    t2_close: float
    t2_percent: float

    t3_close: float
    t3_percent: float

    t5_close: float
    t5_percent: float

    t7_close: float
    t7_percent: float

    buy_score: int = 0
    recommendation: str = ""