from __future__ import annotations

import logging
import re
from typing import Optional

import requests


LOGGER = logging.getLogger(__name__)


class InvescoINAVProvider:
    """
    Invesco India ETF iNAV provider.

    Supported ETFs:
        IVZSENSEX
        IVZBANKNF
    """

    OFFICIAL_URLS = {
        "IVZSENSEX": (
            "https://www.invescomutualfund.com/"
            "our-funds/fund/exchange-traded-fund/"
        ),
        "IVZBANKNF": (
            "https://www.invescomutualfund.com/"
            "our-funds/fund/exchange-traded-fund/"
        ),
    }

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/151.0.0.0 Safari/537.36"
        ),
        "Accept": (
            "text/html,application/xhtml+xml,"
            "application/xml;q=0.9,*/*;q=0.8"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    }

    def __init__(self, timeout: int = 20) -> None:
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

        self._cache: dict[str, float] = {}
        self._loaded = False

    @staticmethod
    def _parse_number(value: object) -> Optional[float]:
        if value is None:
            return None

        text = str(value).strip()

        if not text:
            return None

        text = (
            text
            .replace("₹", "")
            .replace(",", "")
            .strip()
        )

        try:
            return float(text)
        except ValueError:
            return None

    @classmethod
    def _extract_inav(cls, html: str) -> Optional[float]:
        patterns = [
            re.compile(
                r"Real\s+Time\s+iNAV"
                r".{0,1500}?"
                r"(?:₹|&#8377;|Rs\.?\s*)?"
                r"([0-9]+(?:\.[0-9]+)?)",
                re.IGNORECASE | re.DOTALL,
            ),
            re.compile(
                r'"(?:iNAV|inav|real_time_inav|realtime_inav)"'
                r"\s*:\s*"
                r'"?'
                r"([0-9]+(?:\.[0-9]+)?)"
                r'"?',
                re.IGNORECASE,
            ),
            re.compile(
                r"iNAV"
                r".{0,500}?"
                r"(?:₹|&#8377;|Rs\.?\s*)"
                r"([0-9]+(?:\.[0-9]+)?)",
                re.IGNORECASE | re.DOTALL,
            ),
        ]

        for pattern in patterns:
            match = pattern.search(html)

            if not match:
                continue

            value = cls._parse_number(match.group(1))

            if value is not None and value > 0:
                return value

        return None

    def _fetch_page(self, symbol: str) -> Optional[str]:
        url = self.OFFICIAL_URLS.get(symbol)

        if not url:
            LOGGER.warning(
                "No Invesco URL configured for %s",
                symbol,
            )
            return None

        try:
            response = self.session.get(
                url,
                timeout=self.timeout,
            )

            response.raise_for_status()

            return response.text

        except requests.RequestException as exc:
            LOGGER.warning(
                "Invesco request failed for %s: %s",
                symbol,
                exc,
            )

            return None

    def _load(self) -> bool:
        if self._loaded:
            return bool(self._cache)

        for symbol in self.OFFICIAL_URLS:
            html = self._fetch_page(symbol)

            if not html:
                continue

            inav = self._extract_inav(html)

            if inav is None:
                LOGGER.warning(
                    "Unable to extract Invesco iNAV for %s",
                    symbol,
                )
                continue

            self._cache[symbol] = inav

            LOGGER.info(
                "Invesco iNAV %s = %.4f",
                symbol,
                inav,
            )

        self._loaded = True

        return bool(self._cache)

    def fetch(self, symbol: str) -> Optional[float]:
        clean_symbol = (
            symbol
            .replace(".NS", "")
            .strip()
            .upper()
        )

        if not self._load():
            return None

        return self._cache.get(clean_symbol)

    def dump_schemes(self) -> None:
        self._load()

        for symbol in sorted(self.OFFICIAL_URLS):
            value = self._cache.get(symbol)

            if value is None:
                print(f"{symbol}: None")
            else:
                print(f"{symbol}: {value:.4f}")