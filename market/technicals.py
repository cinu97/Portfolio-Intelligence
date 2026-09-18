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
    rsi14: float
    ema63: float
    ema63_slope: float


class TechnicalService:
    """Calculate the existing technical indicator set from close prices."""

    @staticmethod
    def calculate(df: pd.DataFrame) -> dict[str, float]:
        """Return technical values, or the existing empty mapping for no closes."""

        close = pd.to_numeric(df["Close"], errors="coerce").dropna()

        if close.empty:
            return {}

        current = float(close.iloc[-1])
        high52 = float(close.max())
        low52 = float(close.min())

        dma50 = float(close.tail(50).mean()) if len(close) >= 50 else float(close.mean())
        dma200 = float(close.tail(200).mean()) if len(close) >= 200 else float(close.mean())

        range_percent = 0.0
        if high52 != low52:
            range_percent = ((current - low52) / (high52 - low52)) * 100

        rsi14 = TechnicalService._rsi(close, 14)
        ema63 = TechnicalService._ema(close, 63)
        ema63_slope = TechnicalService._ema_slope(close, 63)

        return {
            "week52_high": round(high52, 2),
            "week52_low": round(low52, 2),
            "dma50": round(dma50, 2),
            "dma200": round(dma200, 2),
            "range_percent": round(range_percent, 2),
            "rsi14": round(rsi14, 2),
            "ema63": round(ema63, 2),
            "ema63_slope": round(ema63_slope, 4),
        }

    @staticmethod
    def _rsi(series: pd.Series, period: int = 14) -> float:
        if len(series) < period + 1:
            return 50.0
        delta = series.diff()
        gains = delta.clip(lower=0)
        losses = (-delta).clip(lower=0)
        avg_gain = gains.rolling(window=period, min_periods=period).mean().iloc[-1]
        avg_loss = losses.rolling(window=period, min_periods=period).mean().iloc[-1]
        if avg_loss == 0:
            return 100.0
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    @staticmethod
    def _ema(series: pd.Series, span: int = 63) -> float:
        if len(series) < 2:
            return float(series.iloc[-1])
        return float(series.ewm(span=span, adjust=False).mean().iloc[-1])

    @staticmethod
    def _ema_slope(series: pd.Series, span: int = 63) -> float:
        if len(series) < 2:
            return 0.0
        ema = series.ewm(span=span, adjust=False).mean()
        if len(ema) < 2:
            return 0.0
        return float((ema.iloc[-1] - ema.iloc[-2]) / ema.iloc[-2]) * 100 if ema.iloc[-2] else 0.0
