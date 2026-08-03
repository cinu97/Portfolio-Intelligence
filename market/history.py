from __future__ import annotations

import logging

import yfinance as yf

LOGGER = logging.getLogger(__name__)


class HistoryService:

    def get_history(self, symbol: str):

        try:

            ticker = yf.Ticker(f"{symbol}.NS")

            df = ticker.history(period="15d")

            if df.empty:
                return None

            return df

        except Exception as ex:

            LOGGER.error("%s : %s", symbol, ex)

            return None