from __future__ import annotations

import re
from typing import Optional

import requests


class MiraeINAVProvider:
    """
    Mirae Asset ETF iNAV provider.

    Mirae embeds ETF information in its Next.js HTML payload.
    We extract exact NSE symbol -> nav_value pairs.
    """

    URL = "https://miraeassetetf.co.in/inav-baskets?tab=inav&category=&search="

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/151.0.0.0 Safari/537.36"
        ),
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;"
            "q=0.9,*/*;q=0.8"
        ),
    }

    def __init__(self, timeout: int = 20):
        self.timeout = timeout
        self._cache: dict[str, float] | None = None

    def _load_data(self) -> dict[str, float]:
        try:
            response = requests.get(
                self.URL,
                headers=self.HEADERS,
                timeout=self.timeout,
            )
            response.raise_for_status()

        except requests.RequestException as exc:
            print(f"Unable to fetch Mirae ETF data: {exc}")
            return {}

        html = response.text

        result: dict[str, float] = {}

        # Find every NSE symbol in the Mirae payload.
        symbol_pattern = re.compile(
            r'\\"nse_symbol\\":\\"([^\\"]+)\\"',
            re.IGNORECASE,
        )

        for match in symbol_pattern.finditer(html):
            symbol = match.group(1).strip().upper()

            # Limit the search to the current ETF record.
            # This prevents accidentally taking nav_value
            # from another ETF.
            record_start = html.rfind(
                '\\"etf_fund_name\\"',
                0,
                match.start(),
            )

            if record_start == -1:
                record_start = max(0, match.start() - 10000)

            record = html[record_start:match.end() + 200]

            nav_match = re.search(
                r'\\"nav_value\\":([0-9]+(?:\.[0-9]+)?)',
                record,
                re.IGNORECASE,
            )

            if not nav_match:
                continue

            try:
                result[symbol] = float(nav_match.group(1))
            except ValueError:
                continue

        return result

    def _get_data(self) -> dict[str, float]:
        if self._cache is None:
            self._cache = self._load_data()

        return self._cache

    def fetch(self, symbol: str) -> Optional[float]:
        symbol = symbol.strip().upper()
        return self._get_data().get(symbol)

    def dump_schemes(self) -> None:
        for symbol, value in sorted(self._get_data().items()):
            print(f"{symbol}: {value:.4f}")