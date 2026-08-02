"""Portfolio holdings management."""

from typing import Any


def add_holding(portfolio: dict[str, Any], symbol: str, quantity: float, price: float) -> None:
    """Add or update a holding in a portfolio dictionary."""
    portfolio[symbol] = {"quantity": quantity, "price": price}
