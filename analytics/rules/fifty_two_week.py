from dataclasses import dataclass

from analytics.portfolio_context import PortfolioContext
from analytics.rules.base import InvestmentRule, RuleContribution, RuleResult


@dataclass(slots=True)
class FiftyTwoWeekResult:
    score: int
    reasons: list[str]


class FiftyTwoWeekRule(InvestmentRule):
    """Score the existing position-within-range bands."""

    MAX_SCORE = 20
    key = "fifty_two_week"

    def evaluate(self, context: PortfolioContext) -> RuleResult:
        """Adapt the existing range-position calculation to the rule interface."""
        result = self.calculate(context.range_percent)
        return RuleResult(
            score=result.score,
            reasons=result.reasons,
            max_score=self.MAX_SCORE,
            contributions=[
                RuleContribution(
                    rule_key=self.key,
                    label="52 Week",
                    score=result.score,
                    max_score=self.MAX_SCORE,
                    reason=result.reasons[0],
                )
            ],
        )

    @classmethod
    def calculate(
        cls,
        range_percent: float,
    ) -> FiftyTwoWeekResult:

        score = 0
        reasons = []

        if range_percent <= 20:

            score = 20
            reasons.append("Trading near 52-week low")

        elif range_percent <= 40:

            score = 15
            reasons.append("Trading in lower 40% of yearly range")

        elif range_percent <= 60:

            score = 10
            reasons.append("Trading in middle of yearly range")

        elif range_percent <= 80:

            score = 5
            reasons.append("Trading near yearly high")

        else:

            score = 0
            reasons.append("Trading close to 52-week high")

        return FiftyTwoWeekResult(
            score=score,
            reasons=reasons,
        )
