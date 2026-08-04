from dataclasses import dataclass


@dataclass(slots=True)
class PortfolioAnalysis:

    symbol: str

    quantity: float

    average_price: float

    current_price: float

    invested_value: float

    current_value: float

    pnl: float

    pnl_percent: float

    allocation_percent: float

    discount_from_average: float

    day_percent: float

    t5_percent: float

    t7_percent: float


class PortfolioAnalyzer:

    @staticmethod
    def analyze(
        holding,
        market,
        total_portfolio_value,
    ):

        current_value = (
            holding.quantity
            * market.live_price
        )

        pnl = (
            current_value
            - holding.invested_value
        )

        pnl_percent = 0

        if holding.invested_value:

            pnl_percent = (
                pnl
                / holding.invested_value
            ) * 100

        allocation = 0

        if total_portfolio_value:

            allocation = (
                current_value
                / total_portfolio_value
            ) * 100

        discount = (
            (
                market.live_price
                - holding.average_price
            )
            / holding.average_price
        ) * 100

        return PortfolioAnalysis(

            symbol=holding.symbol,

            quantity=holding.quantity,

            average_price=holding.average_price,

            current_price=market.live_price,

            invested_value=holding.invested_value,

            current_value=current_value,

            pnl=pnl,

            pnl_percent=pnl_percent,

            allocation_percent=allocation,

            discount_from_average=discount,

            day_percent=market.day_change_percent,

            t5_percent=market.t5_percent,

            t7_percent=market.t7_percent,
        )