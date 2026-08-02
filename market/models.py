"""Data models used across the project."""

from dataclasses import dataclass


@dataclass
class MarketData:
    """Simple container for market quote data."""

    symbol: str
    price: float
    timestamp: str | None = None
