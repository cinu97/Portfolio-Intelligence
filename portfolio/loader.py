"""
Portfolio Loader

Loads symbols from:
1. holdings.csv (your portfolio)
2. watchlist.csv (optional)

Returns a unique list of symbols.
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from config.settings import settings

LOGGER = logging.getLogger(__name__)


class PortfolioLoader:

    def __init__(self):

        self.holdings_file = settings.DATA_DIR / "holdings.csv"
        self.watchlist_file = settings.DATA_DIR / "watchlist.csv"

    def load_holdings(self) -> pd.DataFrame:

        if not self.holdings_file.exists():
            LOGGER.warning("holdings.csv not found")
            return pd.DataFrame()

        return pd.read_csv(self.holdings_file)

    def load_watchlist(self) -> pd.DataFrame:

        if not self.watchlist_file.exists():
            LOGGER.info("watchlist.csv not found")

            return pd.DataFrame(
                columns=["Symbol", "Name", "Category", "Enabled"]
            )

        return pd.read_csv(self.watchlist_file)

    def get_symbols(self) -> list[str]:

        symbols: set[str] = set()

        holdings = self.load_holdings()

        if not holdings.empty:

            possible_columns = [
                "Instrument",
                "Symbol",
                "Trading Symbol",
            ]

            column = next(
                (
                    c
                    for c in possible_columns
                    if c in holdings.columns
                ),
                None,
            )

            if column:

                holdings[column] = holdings[column].astype(str)

                symbols.update(
                    holdings[column]
                    .str.strip()
                    .str.upper()
                    .tolist()
                )

        watchlist = self.load_watchlist()

        if (
            not watchlist.empty
            and "Enabled" in watchlist.columns
        ):

            watchlist = watchlist[
                watchlist["Enabled"]
                .astype(str)
                .str.upper()
                == "TRUE"
            ]

        if (
            not watchlist.empty
            and "Symbol" in watchlist.columns
        ):

            symbols.update(
                watchlist["Symbol"]
                .astype(str)
                .str.strip()
                .str.upper()
                .tolist()
            )

        result = sorted(symbols)

        LOGGER.info(
            "Loaded %d unique symbols.",
            len(result),
        )

        return result