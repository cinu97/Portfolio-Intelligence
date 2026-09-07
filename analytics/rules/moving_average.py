from __future__ import annotations

from dataclasses import dataclass

from analytics.portfolio_context import PortfolioContext
from analytics.rules.base import InvestmentRule, RuleContribution, RuleResult


@dataclass(slots=True)
class MovingAverageResult:
    score: int
    reasons: list[str]


class MovingAverageRule(InvestmentRule):
    """
    Score long-term trend health.

    Being below a moving average is now negative evidence rather than a
    reason to award additional BUY points.
    """

    MAX_SCORE = 15
    key = "moving_average"

    def evaluate(self, context: PortfolioContext) -> RuleResult:
        result = self.calculate(
            context.current_price,
            context.dma50,
            context.dma200,
        )

        above_dma50 = (
            context.dma50 > 0
            and context.current_price >= context.dma50
        )

        above_dma200 = (
            context.dma200 > 0
            and context.current_price >= context.dma200
        )

        return RuleResult(
            score=result.score,
            reasons=result.reasons,
            max_score=self.MAX_SCORE,
            contributions=[
                RuleContribution(
                    rule_key=self.key,
                    label="Moving Average (50 DMA)",
                    score=5 if above_dma50 else 0,
                    max_score=5,
                    reason=(
                        "Trading above 50 DMA"
                        if above_dma50
                        else "Trading below 50 DMA"
                    ),
                ),
                RuleContribution(
                    rule_key=self.key,
                    label="Moving Average (200 DMA)",
                    score=10 if above_dma200 else 0,
                    max_score=10,
                    reason=(
                        "Trading above 200 DMA"
                        if above_dma200
                        else "Trading below 200 DMA"
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
        reasons: list[str] = []

        if dma50 > 0:
            if current >= dma50:
                score += 5
                reasons.append("Trading above 50 DMA")
            else:
                reasons.append("Trading below 50 DMA")

        if dma200 > 0:
            if current >= dma200:
                score += 10
                reasons.append("Trading above 200 DMA")
            else:
                reasons.append("Trading below 200 DMA")

        return MovingAverageResult(
            score=score,
            reasons=reasons,
        )