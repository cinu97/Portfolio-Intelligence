from __future__ import annotations

from dataclasses import dataclass

from analytics.portfolio_context import PortfolioContext
from analytics.rules.base import (
    InvestmentRule,
    RuleContribution,
    RuleResult,
)


@dataclass(slots=True)
class LongTermQualityResult:
    score: int
    reasons: list[str]


class LongTermQualityRule(InvestmentRule):
    """
    Long-term structural quality filter.

    This rule intentionally does NOT treat a price decline as a positive
    investment signal. A falling price must be supported by healthy trend
    structure before it can contribute positively.
    """

    MAX_SCORE = 20
    key = "long_term_quality"

    def evaluate(self, context: PortfolioContext) -> RuleResult:
        result = self.calculate(context)

        return RuleResult(
            score=result.score,
            reasons=result.reasons,
            max_score=self.MAX_SCORE,
            contributions=[
                RuleContribution(
                    rule_key=self.key,
                    label="Long-Term Quality",
                    score=result.score,
                    max_score=self.MAX_SCORE,
                    reason="; ".join(result.reasons),
                )
            ],
        )

    @classmethod
    def calculate(
        cls,
        context: PortfolioContext,
    ) -> LongTermQualityResult:

        score = 0
        reasons: list[str] = []

        # Healthy long-term trend.
        if context.current_price >= context.dma200:
            score += 8
            reasons.append("Price is above 200 DMA")
        else:
            reasons.append("Price is below 200 DMA")

        # Intermediate trend.
        if context.current_price >= context.dma50:
            score += 5
            reasons.append("Price is above 50 DMA")
        else:
            reasons.append("Price is below 50 DMA")

        # 50 DMA above 200 DMA is a healthier long-term structure.
        if context.dma50 > 0 and context.dma200 > 0:
            if context.dma50 >= context.dma200:
                score += 5
                reasons.append("50 DMA is above 200 DMA")
            else:
                reasons.append("50 DMA is below 200 DMA")

        # Positive recent trend earns a small confirmation.
        if context.t7_percent > 0:
            score += 2
            reasons.append("7-day momentum is positive")
        elif context.t7_percent < -7:
            reasons.append("7-day momentum is materially negative")

        return LongTermQualityResult(
            score=min(score, cls.MAX_SCORE),
            reasons=reasons,
        )