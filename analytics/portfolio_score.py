from dataclasses import dataclass


@dataclass(slots=True)
class PortfolioAnalysis:

    symbol: str

    average_price: float

    current_price: float

    quantity: float

    invested_value: float

    current_value: float

    pnl: float

    pnl_percent: float

    discount_from_average: float

    allocation_percent: float


class PortfolioScore:

    @staticmethod
    def analyze(
        holding,
        live_price,
        total_portfolio_value,
    ):

        current_value = holding.quantity * live_price

        allocation = 0

        if total_portfolio_value > 0:

            allocation = (
                current_value
                / total_portfolio_value
            ) * 100

        discount = (
            (
                live_price
                - holding.average_price
            )
            / holding.average_price
        ) * 100

        pnl = current_value - holding.invested_value

        pnl_percent = (
            pnl
            / holding.invested_value
        ) * 100

        return PortfolioAnalysis(
            symbol=holding.symbol,
            average_price=holding.average_price,
            current_price=live_price,
            quantity=holding.quantity,
            invested_value=holding.invested_value,
            current_value=current_value,
            pnl=pnl,
            pnl_percent=pnl_percent,
            discount_from_average=discount,
            allocation_percent=allocation,
        )