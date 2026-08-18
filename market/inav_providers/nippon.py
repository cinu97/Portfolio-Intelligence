from __future__ import annotations

import logging
from typing import Optional

import requests


LOGGER = logging.getLogger(__name__)


class NipponINAVProvider:
    """Fetch current iNAV values from Nippon India's RealtimeNAV service."""

    PAGE_URL = (
        "https://etf.nipponindiaim.com/"
        "RealtimeNAV/nav/index"
    )

    DETAILS_URL = (
        "https://etf.nipponindiaim.com/"
        "RealtimeNAV/Nav/DetailsFill"
    )

    # Nippon ETF scheme-name -> our NSE symbol.
    # We will expand this mapping as needed.
    # Only exact, verified symbol -> Nippon scheme mappings belong here.
    # Do NOT map similarly named ETFs from other AMCs.
    SCHEME_MAP = {
        "GOLDBEES": "Nippon India ETF Gold BeES",
        "NIFTYBEES": "Nippon India ETF Nifty 50 BeES",
        "BANKBEES": "Nippon India ETF Nifty Bank BeES",
        "JUNIORBEES": "Nippon India ETF Nifty Next 50 Junior BeES",
        "PHARMABEES": "Nippon India Nifty Pharma ETF",
        "CPSEETF": "CPSE ETF",
        "DIVOPPBEES": "Nippon India ETF Nifty Dividend Opportunities 50",
        "NV20BEES": "Nippon India ETF Nifty 50 Value 20",
        "MID150BEES": "Nippon India ETF Nifty Midcap 150",
        "LIQUIDBEES": "Nippon India ETF Nifty 1D Rate Liquid BeES",
    }

    def __init__(self) -> None:
        self.session = requests.Session()

        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/151.0.0.0 Safari/537.36"
                ),
                "Accept": (
                    "application/json, text/javascript, */*; q=0.01"
                ),
                "Accept-Language": "en-US,en;q=0.9",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": self.PAGE_URL,
            }
        )

        self._cache: dict[str, float] = {}
        self._loaded = False

    @staticmethod
    def _normalise(value: object) -> str:
        if value is None:
            return ""

        return (
            str(value)
            .strip()
            .replace("&amp;", "&")
            .upper()
        )

    @staticmethod
    def _parse_number(value: object) -> Optional[float]:
        if value is None:
            return None

        text = str(value).strip()

        if not text or text in {"-", "--", "NA", "N/A"}:
            return None

        text = text.replace(",", "")

        try:
            return float(text)
        except ValueError:
            return None

    def _load(self) -> bool:
        """Fetch the complete Nippon iNAV table once."""

        if self._loaded:
            return bool(self._cache)

        try:
            # Establish session/cookies first.
            page = self.session.get(
                self.PAGE_URL,
                timeout=15,
            )
            page.raise_for_status()

            # The page JavaScript explicitly uses POST with
            # application/json and no request body.
            response = self.session.post(
                self.DETAILS_URL,
                data="",
                headers={
                    "Content-Type": "application/json",
                },
                timeout=15,
            )

            response.raise_for_status()

            payload = response.json()

            rows = payload.get(
                "RVDetailsList",
                [],
            )

            if not isinstance(rows, list):
                LOGGER.warning(
                    "Unexpected Nippon iNAV response structure"
                )
                return False

            LOGGER.info(
                "Nippon returned %d iNAV records",
                len(rows),
            )

            for row in rows:
                if not isinstance(row, dict):
                    continue

                scheme_name = (
                    row.get("SchName")
                    or row.get("schName")
                    or row.get("SchemeName")
                )

                inav = (
                    row.get("CNav")
                    or row.get("cnav")
                    or row.get("CurrentNAV")
                )

                if not scheme_name:
                    continue

                inav_value = self._parse_number(inav)

                if inav_value is None:
                    continue

                scheme_normalised = self._normalise(
                    scheme_name
                )

                for symbol, expected_name in self.SCHEME_MAP.items():

                    expected_normalised = self._normalise(
                        expected_name
                    )

                    if scheme_normalised == expected_normalised:
                        self._cache[symbol] = inav_value
                        break

            self._loaded = True

            LOGGER.info(
                "Mapped %d Nippon ETFs to iNAV",
                len(self._cache),
            )

            return bool(self._cache)

        except requests.RequestException as exc:
            LOGGER.warning(
                "Nippon iNAV request failed: %s",
                exc,
            )

        except ValueError as exc:
            LOGGER.warning(
                "Invalid Nippon iNAV JSON response: %s",
                exc,
            )

        return False


    def dump_schemes(self) -> None:
        """Print all schemes currently returned by Nippon RealtimeNAV."""
        try:
            page = self.session.get(
                self.PAGE_URL,
                timeout=15,
            )
            page.raise_for_status()

            response = self.session.post(
                self.DETAILS_URL,
                data="",
                headers={
                    "Content-Type": "application/json",
                },
                timeout=15,
            )
            response.raise_for_status()

            payload = response.json()
            rows = payload.get("RVDetailsList", [])

            if not isinstance(rows, list):
                print("Unexpected Nippon iNAV response structure")
                return

            for row in rows:
                if not isinstance(row, dict):
                    continue

                print(
                    f"{row.get('SchName')} => "
                    f"{row.get('CNav')}"
                )

        except requests.RequestException as exc:
            print(f"Unable to fetch Nippon iNAV data: {exc}")

        except ValueError as exc:
            print(f"Invalid Nippon iNAV JSON response: {exc}")

    def fetch(
        self,
        symbol: str,
    ) -> Optional[float]:
        """Return current iNAV for an ETF symbol."""

        clean_symbol = (
            symbol
            .replace(".NS", "")
            .replace("-RR", "")
            .strip()
            .upper()
        )

        if not self._load():
            return None

        return self._cache.get(
            clean_symbol
        )