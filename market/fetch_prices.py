from __future__ import annotations

import logging

from market.history import HistoryService
from market.models import MarketData
from market.technicals import TechnicalService

LOGGER = logging.getLogger(__name__)


class MarketDataService:
    """Build market snapshots from provider history."""

    def __init__(self) -> None:
        self.history = HistoryService()

    @staticmethod
    def _pct(current: float, reference: float) -> float:
        if reference == 0:
            return 0.0
        return round(((current - reference) / reference) * 100, 2)

    def fetch(self, symbols: list[str]) -> list[MarketData]:
        """Fetch and transform market data for the supplied symbols."""

        results: list[MarketData] = []

        for symbol in symbols:

            df = self.history.get_history(symbol)

            if df is None or df.empty:
                LOGGER.warning("No history found for %s", symbol)
                continue

            technical = TechnicalService.calculate(df)
            df = df.tail(8)

            if len(df) < 8:
                LOGGER.warning(
                    "Skipping %s. Need 8 trading days, got %d",
                    symbol,
                    len(df),
                )
                continue

            closes = [round(float(x), 2) for x in df["Close"].tolist()]

            live = closes[-1]
            previous = closes[-2]

            t2 = closes[-3]
            t3 = closes[-4]
            t5 = closes[-6]
            t7 = closes[-8]
            results.append(
                MarketData(
                    symbol=symbol,

                    live_price=live,

                    previous_close=previous,

                    day_change_percent=self._pct(
                        live,
                        previous,
                    ),

                    t2_close=t2,
                    t2_percent=self._pct(
                        live,
                        t2,
                    ),

                    t3_close=t3,
                    t3_percent=self._pct(
                        live,
                        t3,
                    ),

                    t5_close=t5,
                    t5_percent=self._pct(
                        live,
                        t5,
                    ),

                    t7_close=t7,
                    t7_percent=self._pct(
                        live,
                        t7,
                    ),
                    week52_high=technical["week52_high"],

                    week52_low=technical["week52_low"],

                    dma50=technical["dma50"],

                    dma200=technical["dma200"],

                    range_percent=technical["range_percent"],
                    buy_score=0,

                    recommendation="",
                )
            )

        LOGGER.info(
            "Fetched market data for %d symbols",
            len(results),
        )

        return results
