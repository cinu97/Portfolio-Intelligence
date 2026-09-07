from __future__ import annotations

import logging

import pandas as pd
import yfinance as yf

LOGGER = logging.getLogger(__name__)


class HistoryService:
    """Retrieve clean price history from Yahoo Finance."""

    def get_history(
        self,
        symbol: str,
    ) -> pd.DataFrame | None:
        """Return clean historical OHLC data, or None when unavailable."""

        try:
            # Yahoo Finance uses the base ticker for REIT/InvIT symbols.
            # Portfolio holdings may contain the "-RR" suffix.
            yahoo_symbol = symbol.removesuffix("-RR")

            ticker = yf.Ticker(
                f"{yahoo_symbol}.NS"
            )

            df = ticker.history(
                period="1y"
            )

            if df.empty:
                LOGGER.warning(
                    "Yahoo Finance returned no history for %s",
                    symbol,
                )
                return None

            # Remove rows where the closing price is unavailable.
            # This prevents weekend/holiday/incomplete provider rows
            # from becoming the portfolio's live price.
            if "Close" not in df.columns:
                LOGGER.warning(
                    "No Close column returned for %s",
                    symbol,
                )
                return None

            df = df.dropna(
                subset=["Close"]
            ).copy()

            if df.empty:
                LOGGER.warning(
                    "No valid closing prices found for %s",
                    symbol,
                )
                return None

            # Ensure the data is chronologically ordered.
            df = df.sort_index()

            LOGGER.debug(
                "%s: %d valid historical rows",
                symbol,
                len(df),
            )

            return df

        except Exception as ex:

            LOGGER.error(
                "%s : %s",
                symbol,
                ex,
            )

            return None