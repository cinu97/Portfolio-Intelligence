from __future__ import annotations

import pandas as pd
from typing import TypedDict


class TechnicalIndicators(TypedDict):
    """Technical values attached to a market-data record."""

    week52_high: float
    week52_low: float
    dma50: float
    dma200: float
    range_percent: float


class TechnicalService:
    """Calculate the existing technical indicator set from close prices."""

    @staticmethod
    def calculate(df: pd.DataFrame) -> dict[str, float]:
        """Return technical values, or the existing empty mapping for no closes."""

        close = df["Close"].dropna()

        if close.empty:
            return {}

        current = float(close.iloc[-1])

        high52 = float(close.max())

        low52 = float(close.min())

        dma50 = float(
            close.tail(50).mean()
        )

        dma200 = float(
            close.tail(200).mean()
        )

        range_percent = 0

        if high52 != low52:

            range_percent = (
                (current - low52)
                /
                (high52 - low52)
            ) * 100

        return {

            "week52_high": round(high52, 2),

            "week52_low": round(low52, 2),

            "dma50": round(dma50, 2),

            "dma200": round(dma200, 2),

            "range_percent": round(range_percent, 2),

        }
