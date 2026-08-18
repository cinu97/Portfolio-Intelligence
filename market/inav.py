from __future__ import annotations
from market.inav_providers.nippon import NipponINAVProvider
from market.inav_providers.mirae import MiraeINAVProvider
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
    Fetch live ETF iNAV/NAV data from NSE's ETF market-data endpoint.

    iNAV is treated as an execution-quality signal.
    It does not modify the technical score.
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

        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/151.0.0.0 Safari/537.36"
            ),
            "Accept": (
                "application/json, text/plain, */*"
            ),
            "Accept-Language": (
                "en-US,en;q=0.9"
            ),
            "Accept-Encoding": (
                "gzip, deflate, br"
            ),
            "Referer": self.ETF_PAGE_URL,
            "Connection": "keep-alive",
        }

        self.session.headers.update(
            self.headers
        )

        self._cache: dict[str, dict] = {}
        self._loaded = False
        self.nippon = NipponINAVProvider()
        self.mirae = MiraeINAVProvider()

    def _prime_session(self) -> None:
        """
        Establish NSE cookies by visiting the ETF page first.
        """

        response = self.session.get(
            self.ETF_PAGE_URL,
            timeout=15,
        )

        response.raise_for_status()

    def _load_etf_data(self) -> bool:
        """
        Download NSE's complete ETF table once and cache it.

        NSE's ETF page exposes ETF LTP and NAV data.
        """

        if self._loaded:
            return bool(self._cache)

        try:

            self._prime_session()

            response = self.session.get(
                self.ETF_API_URL,
                headers={
                    **self.headers,
                    "Referer": self.ETF_PAGE_URL,
                },
                timeout=15,
            )

            response.raise_for_status()

            payload = response.json()

            rows = payload.get(
                "data",
                [],
            )

            if not isinstance(
                rows,
                list,
            ):
                LOGGER.warning(
                    "Unexpected NSE ETF response format."
                )
                return False

            for row in rows:

                if not isinstance(
                    row,
                    dict,
                ):
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
                "Loaded NSE ETF data for %d symbols",
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
                "Invalid NSE ETF JSON response: %s",
                exc,
            )

        return False

    @staticmethod
    def _number(
        value,
    ) -> Optional[float]:

        if value is None:
            return None

        if isinstance(
            value,
            str,
        ):

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

    @classmethod
    def _find_number(
        cls,
        row: dict,
        keys: list[str],
    ) -> Optional[float]:

        for key in keys:

            if key not in row:
                continue

            value = cls._number(
                row.get(key)
            )

            if value is not None:
                return value

        return None

    @classmethod
    def _extract_ltp(
        cls,
        row: dict,
    ) -> Optional[float]:

        return cls._find_number(
            row,
            [
                "ltP",
                "ltp",
                "LTP",
                "lastPrice",
                "lastprice",
            ],
        )

    @classmethod
    def _extract_inav(
        cls,
        row: dict,
    ) -> Optional[float]:

        # NSE ETF endpoint has historically exposed NAV
        # using different field naming conventions.
        #
        # Check all known representations rather than
        # assuming one exact JSON key.

        return cls._find_number(
            row,
            [
                "nav",
                "NAV",
                "iNav",
                "iNAV",
                "inav",
                "INAV",
                "indicativeNav",
                "indicativeNAV",
                "indicative_nav",
            ],
        )

    @staticmethod
    def _calculate_signal(
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

        # ---------------------------------------------------------
        # AMC-specific iNAV providers
        # ---------------------------------------------------------
        # Try Nippon first.
        inav = self.nippon.fetch(clean_symbol)

        # If Nippon does not cover the symbol, try Mirae.
        if inav is None:
            inav = self.mirae.fetch(clean_symbol)

        if inav is None:
            return INAVData(
                symbol=clean_symbol,
                ltp=ltp,
                inav=None,
                premium_discount_pct=None,
                signal="UNAVAILABLE",
            )

        premium_discount = None

        if (
            ltp is not None
            and inav > 0
        ):
            premium_discount = round(
                (
                    (ltp - inav)
                    / inav
                ) * 100,
                2,
            )

        signal = self._calculate_signal(
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