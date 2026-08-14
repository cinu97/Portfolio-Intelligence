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

    week52_high: float
    week52_low: float

    dma50: float
    dma200: float

    range_percent: float

    buy_score: int
    recommendation: str

    # iNAV fields MUST be after all required fields
    inav: float | None = None
    inav_premium_discount_pct: float | None = None
    inav_signal: str = "N/A"

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
