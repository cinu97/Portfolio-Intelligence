from dataclasses import dataclass

from analytics.portfolio_context import PortfolioContext
from analytics.rules.base import InvestmentRule, RuleContribution, RuleResult


@dataclass(slots=True)
class AverageBuyResult:
    score: int
    reason: str


class AverageBuyRule(InvestmentRule):
    """Score a price's discount relative to the average buy price."""

    MAX_SCORE = 30
    key = "average_buy"

    def evaluate(self, context: PortfolioContext) -> RuleResult:
        """Adapt the existing average-buy calculation to the rule interface."""
        result = self.calculate(context.average_price, context.current_price)
        return RuleResult(
            score=result.score,
            reasons=[result.reason],
            max_score=self.MAX_SCORE,
            contributions=[
                RuleContribution(
                    rule_key=self.key,
                    label="Average Buy",
                    score=result.score,
                    max_score=self.MAX_SCORE,
                    reason=result.reason,
                )
            ],
        )

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
