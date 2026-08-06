from dataclasses import dataclass

from analytics.portfolio_context import PortfolioContext
from analytics.rules.base import InvestmentRule, RuleContribution, RuleResult


@dataclass(slots=True)
class AllocationResult:
    score: int
    reason: str


class AllocationRule(InvestmentRule):
    """Score a holding against the existing target allocation bands."""

    MAX_SCORE = 20
    key = "allocation"

    def evaluate(self, context: PortfolioContext) -> RuleResult:
        """Adapt the existing allocation calculation to the rule interface."""
        result = self.calculate(context.allocation_percent)
        return RuleResult(
            score=result.score,
            reasons=[result.reason],
            max_score=self.MAX_SCORE,
            contributions=[
                RuleContribution(
                    rule_key=self.key,
                    label="Allocation",
                    score=result.score,
                    max_score=self.MAX_SCORE,
                    reason=result.reason,
                )
            ],
        )

    @classmethod
    def calculate(
        cls,
        allocation_percent: float,
        target_percent: float = 5.0,
    ) -> AllocationResult:

        if allocation_percent <= target_percent * 0.40:
            return AllocationResult(
                20,
                "Significantly underweight",
            )

        if allocation_percent <= target_percent * 0.60:
            return AllocationResult(
                15,
                "Underweight",
            )

        if allocation_percent <= target_percent:
            return AllocationResult(
                10,
                "Near target allocation",
            )

        if allocation_percent <= target_percent * 1.20:
            return AllocationResult(
                5,
                "Slightly overweight",
            )

        return AllocationResult(
            0,
            "Overweight",
        )
