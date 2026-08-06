from dataclasses import dataclass

from analytics.portfolio_context import PortfolioContext
from analytics.rules.base import InvestmentRule, RuleContribution, RuleResult


@dataclass(slots=True)
class MovingAverageResult:
    score: int
    reasons: list[str]


class MovingAverageRule(InvestmentRule):
    """Score a price trading below the existing moving-average thresholds."""

    MAX_SCORE = 15
    key = "moving_average"

    def evaluate(self, context: PortfolioContext) -> RuleResult:
        """Adapt the existing moving-average calculation to the rule interface."""
        result = self.calculate(context.current_price, context.dma50, context.dma200)
        below_dma50 = context.current_price < context.dma50
        below_dma200 = context.current_price < context.dma200
        return RuleResult(
            score=result.score,
            reasons=result.reasons,
            max_score=self.MAX_SCORE,
            contributions=[
                RuleContribution(
                    rule_key=self.key,
                    label="Moving Average (50 DMA)",
                    score=5 if below_dma50 else 0,
                    max_score=5,
                    reason=(
                        "Trading below 50 DMA"
                        if below_dma50
                        else "At or above 50 DMA"
                    ),
                ),
                RuleContribution(
                    rule_key=self.key,
                    label="Moving Average (200 DMA)",
                    score=10 if below_dma200 else 0,
                    max_score=10,
                    reason=(
                        "Trading below 200 DMA"
                        if below_dma200
                        else "At or above 200 DMA"
                    ),
                ),
            ],
        )

    @classmethod
    def calculate(
        cls,
        current: float,
        dma50: float,
        dma200: float,
    ) -> MovingAverageResult:

        score = 0

        reasons = []

        if current < dma50:

            score += 5
            reasons.append("Trading below 50 DMA")

        if current < dma200:

            score += 10
            reasons.append("Trading below 200 DMA")

        return MovingAverageResult(
            score=score,
            reasons=reasons,
        )
