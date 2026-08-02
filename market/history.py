"""
Historical market data.
"""

from __future__ import annotations

from dataclasses import dataclass

import yfinance as yf


@dataclass
class HistoricalDay:
    date: str
    close: float


def load_history(symbol: str, days: int = 7) -> list[HistoricalDay]:

    ticker = yf.Ticker(f"{symbol}.NS")

    history = ticker.history(period=f"{days + 5}d")

    if history.empty:
        return []

    history = history.tail(days)

    output: list[HistoricalDay] = []

    for date, row in history.iterrows():
        output.append(
            HistoricalDay(
                date=date.strftime("%Y-%m-%d"),
                close=round(float(row["Close"]), 2),
            )
        )

    return output