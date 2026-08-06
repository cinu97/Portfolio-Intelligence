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

    week52_high: float = 0

    week52_low: float = 0

    dma50: float = 0

    dma200: float = 0

    range_percent: float = 0

    buy_score: int = 0
    recommendation: str = ""


@dataclass(slots=True)
class AnalyticsResult:
    """Legacy V1 analytics output retained for compatibility."""

    symbol: str
    live_price: float
    previous_close: float
    day_change_percent: float
    t2_percent: float
    t3_percent: float
    t5_percent: float
    t7_percent: float
    buy_score: int
    recommendation: str
