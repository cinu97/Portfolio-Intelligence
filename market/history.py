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

            # Yahoo Finance uses the base ticker for REIT/InvIT symbols.
            # Portfolio holdings may contain the "-RR" suffix.
            yahoo_symbol = symbol.removesuffix("-RR")
            ticker = yf.Ticker(f"{yahoo_symbol}.NS")
            
            df = ticker.history(period="1y")

            if df.empty:
                return None

            return df

        except Exception as ex:

            LOGGER.error("%s : %s", symbol, ex)

            return None
