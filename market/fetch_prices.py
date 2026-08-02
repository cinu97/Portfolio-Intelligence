"""
Market data retrieval using Yahoo Finance.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import yfinance as yf


@dataclass
class LivePrice:
    symbol: str
    live_price: float
    previous_close: float
    day_change_percent: float


def fetch_latest_prices(symbols: Iterable[str]) -> list[LivePrice]:
    """
    Fetch latest prices for NSE symbols.

    Example input:
        ["NIFTYBEES", "BANKBEES"]
    """

    output: list[LivePrice] = []

    for symbol in symbols:
        ticker = yf.Ticker(f"{symbol}.NS")

        try:
            info = ticker.fast_info

            live = float(info["lastPrice"])
            previous = float(info["previousClose"])

            if previous:
                change = round(((live - previous) / previous) * 100, 2)
            else:
                change = 0.0

            output.append(
                LivePrice(
                    symbol=symbol,
                    live_price=round(live, 2),
                    previous_close=round(previous, 2),
                    day_change_percent=change,
                )
            )

        except Exception as exc:
            print(f"Unable to fetch {symbol}: {exc}")

    return output