from dataclasses import dataclass


@dataclass(slots=True)
class PortfolioContext:
    """All normalized portfolio and market inputs required by V2 rules."""

    # Portfolio
    symbol: str
    quantity: float
    average_price: float
    invested_value: float
    current_value: float

    # Market
    current_price: float
    previous_close: float

    # Returns
    pnl: float
    pnl_percent: float

    # Allocation
    allocation_percent: float
    discount_from_average: float

    # Momentum
    day_percent: float
    t5_percent: float
    t7_percent: float

    # Technicals
    week52_high: float
    week52_low: float
    range_percent: float

    dma50: float
    dma200: float
