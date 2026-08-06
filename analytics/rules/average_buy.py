from dataclasses import dataclass


@dataclass(slots=True)
class AverageBuyResult:
    score: int
    reason: str


class AverageBuyRule:

    MAX_SCORE = 30

    @classmethod
    def calculate(cls, average_price: float, current_price: float) -> AverageBuyResult:

        if average_price <= 0:
            return AverageBuyResult(
                score=0,
                reason="No average price",
            )

        discount = (
            (current_price - average_price)
            / average_price
        ) * 100

        if discount <= -15:
            return AverageBuyResult(
                cls.MAX_SCORE,
                "Trading >15% below average buy",
            )

        if discount <= -10:
            return AverageBuyResult(
                25,
                "Trading 10-15% below average buy",
            )

        if discount <= -5:
            return AverageBuyResult(
                20,
                "Trading 5-10% below average buy",
            )

        if discount <= -2:
            return AverageBuyResult(
                10,
                "Trading slightly below average buy",
            )

        return AverageBuyResult(
            0,
            "Above average buy price",
        )