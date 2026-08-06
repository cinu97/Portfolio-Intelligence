"""
Portfolio Loader

Loads symbols from:
1. holdings.csv (your portfolio)
2. watchlist.csv (optional)

Returns a unique list of symbols.
"""

from __future__ import annotations

import logging
import pandas as pd

from config.settings import settings

LOGGER = logging.getLogger(__name__)

from dataclasses import dataclass


@dataclass(slots=True)
class Holding:
    symbol: str
    quantity: float
    average_price: float
    invested_value: float
    current_value: float
    pnl: float
    pnl_percent: float

    quantity: float = 0.0
    average_price: float = 0.0
    invested_value: float = 0.0
    current_value: float = 0.0
    pnl: float = 0.0
    pnl_percent: float = 0.0

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

    def load_holding_records(self) -> dict[str, Holding]:
        """Convert the holdings CSV into the typed model used by V2."""
        dataframe = self.load_holdings()

        if dataframe.empty:
            return {}

        required_columns = {
            "symbol": ("Instrument", "Symbol", "Trading Symbol"),
            "quantity": ("Qty.", "Quantity"),
            "average_price": ("Avg. cost", "Average Price"),
            "invested_value": ("Invested", "Invested Value"),
            "current_value": ("Cur. val", "Current Value"),
            "pnl": ("P&L", "PnL"),
            "pnl_percent": ("Net chg.", "PnL %"),
        }

        columns = {
            name: next((column for column in candidates if column in dataframe.columns), None)
            for name, candidates in required_columns.items()
        }
        missing = [name for name, column in columns.items() if column is None]

        if missing:
            LOGGER.warning("Cannot build typed holdings; missing columns: %s", ", ".join(missing))
            return {}

        records: dict[str, Holding] = {}
        for _, row in dataframe.iterrows():
            symbol = str(row[columns["symbol"]]).strip().upper()
            if not symbol:
                continue

            records[symbol] = Holding(
                symbol=symbol,
                quantity=float(row[columns["quantity"]]),
                average_price=float(row[columns["average_price"]]),
                invested_value=float(row[columns["invested_value"]]),
                current_value=float(row[columns["current_value"]]),
                pnl=float(row[columns["pnl"]]),
                pnl_percent=float(row[columns["pnl_percent"]]),
            )

        LOGGER.info("Built %d typed holding records.", len(records))
        return records

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

        
