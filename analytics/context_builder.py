from analytics.portfolio_context import PortfolioContext
from market.models import MarketData
from portfolio.loader import Holding


class ContextBuilder:
    """Build the immutable V2 scoring context from holding and market data."""

    @staticmethod
    def build(
        holding: Holding,
        market: MarketData,
        total_portfolio_value: float,
    ) -> PortfolioContext:
        """Calculate portfolio-derived values without mutating either input."""

        current_value = (
            holding.quantity
            * market.live_price
        )

        pnl = (
            current_value
            - holding.invested_value
        )

        pnl_percent = 0

        if holding.invested_value > 0:

            pnl_percent = (
                pnl
                / holding.invested_value
            ) * 100

        allocation = 0

        if total_portfolio_value > 0:

            allocation = (
                current_value
                / total_portfolio_value
            ) * 100

        discount = 0

        if holding.average_price > 0:

            discount = (
                (
                    market.live_price
                    - holding.average_price
                )
                / holding.average_price
            ) * 100

        return PortfolioContext(

            symbol=holding.symbol,

            quantity=holding.quantity,

            average_price=holding.average_price,

            invested_value=holding.invested_value,

            current_value=current_value,

            current_price=market.live_price,

            previous_close=market.previous_close,

            pnl=pnl,

            pnl_percent=pnl_percent,

            allocation_percent=allocation,

            discount_from_average=discount,

            day_percent=market.day_change_percent,

            t5_percent=market.t5_percent,

            t7_percent=market.t7_percent,

            week52_high=market.week52_high,

            week52_low=market.week52_low,

            range_percent=market.range_percent,

            dma50=market.dma50,

            dma200=market.dma200,
        )
