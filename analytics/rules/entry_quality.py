from __future__ import annotations

from dataclasses import dataclass

from analytics.portfolio_context import PortfolioContext


@dataclass(slots=True)
class EntryQualityResult:
    eligible: bool
    score: int
    reasons: list[str]


class EntryQualityRule:
    """
    Determines whether an otherwise positive technical signal
    is suitable for fresh capital deployment.

    This is a gate, not another buy-score component.
    """

    @staticmethod
    def evaluate(context: PortfolioContext) -> EntryQualityResult:

        score = 100
        reasons: list[str] = []

        # Long-term trend penalty.
        if (
            context.dma200 > 0
            and context.current_price < context.dma200
        ):
            score -= 20
            reasons.append(
                "Price is below 200 DMA; reduce entry conviction"
            )

        # Intermediate trend.
        if (
            context.dma50 > 0
            and context.current_price < context.dma50
        ):
            score -= 10
            reasons.append(
                "Price is below 50 DMA"
            )

        # 50/200 DMA structure.
        if (
            context.dma50 > 0
            and context.dma200 > 0
            and context.dma50 < context.dma200
        ):
            score -= 15
            reasons.append(
                "50 DMA is below 200 DMA"
            )

        # Short-term deterioration.
        if context.t7_percent <= -7:
            score -= 15
            reasons.append(
                "7-day momentum is materially negative"
            )

        elif context.t7_percent <= -4:
            score -= 8
            reasons.append(
                "7-day momentum is weak"
            )

        # Don't reject a pullback by itself.
        if (
            context.t7_percent < 0
            and context.t7_percent > -4
        ):
            reasons.append(
                "Moderate pullback may provide an accumulation opportunity"
            )

        score = max(0, min(score, 100))

        # We allow accumulation during moderate weakness.
        eligible = score >= 60

        if eligible:
            reasons.append(
                "Entry quality is acceptable for staged deployment"
            )
        else:
            reasons.append(
                "Entry quality is too weak for fresh capital"
            )

        return EntryQualityResult(
            eligible=eligible,
            score=score,
            reasons=reasons,
        )