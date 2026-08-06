from __future__ import annotations

import logging

import pandas as pd
import yfinance as yf

LOGGER = logging.getLogger(__name__)


class HistoryService:
    """Retrieve price history from the configured Yahoo Finance market suffix."""

    def get_history(self, symbol: str) -> pd.DataFrame | None:
        """Return the existing history window, or ``None`` when unavailable."""

        try:

            ticker = yf.Ticker(f"{symbol}.NS")

            df = ticker.history(period="15d")

            if df.empty:
                return None

            return df

        except Exception as ex:

            LOGGER.error("%s : %s", symbol, ex)

            return None
