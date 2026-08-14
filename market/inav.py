from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

import requests


LOGGER = logging.getLogger(__name__)


@dataclass
class INAVData:
    symbol: str
    ltp: Optional[float]
    inav: Optional[float]
    premium_discount_pct: Optional[float]
    signal: str


class INAVService:
    """
    Fetch ETF iNAV data from NSE's ETF market-data endpoint.

    iNAV is an execution-quality signal.
    It does not modify the technical score.

    NSE's ETF market-data page exposes LTP and NAV/iNAV data,
    while NSE's market-feed documentation identifies iNAV as
    a separate instrument/value for ETFs.
    """

    ETF_PAGE_URL = (
        "https://www.nseindia.com/"
        "market-data/exchange-traded-funds-etf"
    )

    ETF_API_URL = (
        "https://www.nseindia.com/api/etf"
    )

    def __init__(self) -> None:

        self.session = requests.Session()

        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/151.0.0.0 Safari/537.36"
                ),
                "Accept": (
                    "application/json,text/plain,*/*"
                ),
                "Accept-Language": (
                    "en-US,en;q=0.9"
                ),
                "Accept-Encoding": (
                    "gzip, deflate"
                ),
                "Connection": "keep-alive",
                "Referer": (
                    "https://www.nseindia.com/"
                ),
            }
        )

        self._cache: dict[str, dict] = {}
        self._loaded = False

    def _load_etf_data(self) -> bool:
        """
        Load the complete NSE ETF table once.

        Returns True when data is successfully loaded.
        """

        if self._loaded:
            return bool(self._cache)

        try:

            # Prime NSE session using the actual ETF page.
            page_response = self.session.get(
                self.ETF_PAGE_URL,
                timeout=15,
            )

            page_response.raise_for_status()

            # Use cookies established by the ETF page.
            response = self.session.get(
                self.ETF_API_URL,
                timeout=15,
            )

            response.raise_for_status()

            payload = response.json()

            rows = payload.get(
                "data",
                [],
            )

            if not isinstance(rows, list):
                LOGGER.warning(
                    "Unexpected NSE ETF response format."
                )
                return False

            for row in rows:

                if not isinstance(row, dict):
                    continue

                symbol = (
                    row.get("symbol")
                    or row.get("SYMBOL")
                )

                if not symbol:
                    continue

                clean_symbol = (
                    str(symbol)
                    .replace(".NS", "")
                    .replace("-RR", "")
                    .strip()
                    .upper()
                )

                self._cache[
                    clean_symbol
                ] = row

            self._loaded = True

            LOGGER.info(
                "Loaded iNAV data for %d ETFs from NSE",
                len(self._cache),
            )

            return bool(self._cache)

        except requests.RequestException as exc:

            LOGGER.warning(
                "Unable to fetch NSE ETF data: %s",
                exc,
            )

        except ValueError as exc:

            LOGGER.warning(
                "Invalid NSE ETF response: %s",
                exc,
            )

        return False

    @staticmethod
    def _number(
        value,
    ) -> Optional[float]:
        """
        Convert NSE numeric fields safely.

        NSE may return '-' for unavailable values.
        """

        if value is None:
            return None

        if isinstance(value, str):

            value = value.strip()

            if value in {
                "",
                "-",
                "--",
                "NA",
                "N/A",
            }:
                return None

        try:
            return float(value)

        except (
            TypeError,
            ValueError,
        ):
            return None

    @staticmethod
    def _extract_inav(
        row: dict,
    ) -> Optional[float]:

        # NSE ETF endpoint field names can vary.
        # Check the known NAV/iNAV representations.

        possible_keys = [
            "nav",
            "iNav",
            "iNAV",
            "inav",
            "INAV",
            "indicativeNav",
            "indicativeNAV",
            "indicative_nav",
        ]

        for key in possible_keys:

            value = row.get(key)

            number = INAVService._number(
                value
            )

            if number is not None:
                return number

        return None

    @staticmethod
    def _extract_ltp(
        row: dict,
    ) -> Optional[float]:

        possible_keys = [
            "ltP",
            "ltp",
            "LTP",
            "lastPrice",
            "lastprice",
        ]

        for key in possible_keys:

            number = INAVService._number(
                row.get(key)
            )

            if number is not None:
                return number

        return None

    @staticmethod
    def _signal(
        premium_discount_pct: Optional[float],
    ) -> str:

        if premium_discount_pct is None:
            return "UNAVAILABLE"

        if premium_discount_pct > 0.50:
            return "PREMIUM"

        if premium_discount_pct >= 0:
            return "SLIGHT_PREMIUM"

        if premium_discount_pct >= -0.50:
            return "FAIR"

        return "DISCOUNT"

    def fetch(
        self,
        symbol: str,
        ltp: Optional[float] = None,
    ) -> INAVData:

        clean_symbol = (
            symbol
            .replace(".NS", "")
            .replace("-RR", "")
            .strip()
            .upper()
        )

        # Load the entire ETF table once.
        if not self._load_etf_data():

            return INAVData(
                symbol=clean_symbol,
                ltp=ltp,
                inav=None,
                premium_discount_pct=None,
                signal="UNAVAILABLE",
            )

        row = self._cache.get(
            clean_symbol
        )

        # Not an ETF / not present in NSE ETF table.
        if row is None:

            return INAVData(
                symbol=clean_symbol,
                ltp=ltp,
                inav=None,
                premium_discount_pct=None,
                signal="N/A",
            )

        if ltp is None:

            ltp = self._extract_ltp(
                row
            )

        inav = self._extract_inav(
            row
        )

        premium_discount = None

        if (
            ltp is not None
            and inav is not None
            and inav > 0
        ):

            premium_discount = round(
                (
                    (ltp - inav)
                    / inav
                )
                * 100,
                2,
            )

        signal = self._signal(
            premium_discount
        )

        return INAVData(
            symbol=clean_symbol,
            ltp=ltp,
            inav=inav,
            premium_discount_pct=(
                premium_discount
            ),
            signal=signal,
        )