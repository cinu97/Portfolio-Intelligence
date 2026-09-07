from __future__ import annotations

from dataclasses import dataclass

from analytics.portfolio_context import PortfolioContext


@dataclass(slots=True)
class ExitAssessment:
    score: int
    action: str
    reasons: list[str]


class ExitRule:
    """
    Portfolio exit / profit-booking assessment.

    This is intentionally separate from the entry score.
    A weak entry score does not automatically mean SELL.
    """

    @staticmethod
    def evaluate(context: PortfolioContext) -> ExitAssessment:

        score = 0
        reasons: list[str] = []

        current = context.current_price
        dma50 = context.dma50
        dma200 = context.dma200

        # ---------------------------------------------------------
        # Trend deterioration
        # ---------------------------------------------------------

        if dma200 > 0 and current < dma200:
            score += 30
            reasons.append("Price is below 200 DMA")

        elif dma50 > 0 and current < dma50:
            score += 15
            reasons.append("Price is below 50 DMA")

        # 50 DMA below 200 DMA is a negative long-term structure.
        if dma50 > 0 and dma200 > 0 and dma50 < dma200:
            score += 20
            reasons.append("50 DMA is below 200 DMA")

        # ---------------------------------------------------------
        # Momentum deterioration
        # ---------------------------------------------------------

        if context.t5_percent <= -5:
            score += 10
            reasons.append("5-day momentum is materially negative")

        if context.t7_percent <= -7:
            score += 10
            reasons.append("7-day momentum is materially negative")

        # ---------------------------------------------------------
        # Profit-booking / extension
        # ---------------------------------------------------------

        if context.pnl_percent >= 25:
            if context.range_percent >= 80:
                score += 10
                reasons.append(
                    "Profit is above 25% and price is near the 52-week high"
                )

            if dma50 > 0:
                distance_from_50 = ((current - dma50) / dma50) * 100

                if distance_from_50 >= 10:
                    score += 10
                    reasons.append(
                        "Profit is above 25% and price is materially extended "
                        "above 50 DMA"
                    )

        # ---------------------------------------------------------
        # Position concentration
        # ---------------------------------------------------------

        if context.allocation_percent >= 10:
            score += 10
            reasons.append("Position is materially overweight")

        # ---------------------------------------------------------
        # Decision
        # ---------------------------------------------------------

        if score >= 70:
            action = "SELL"

        elif score >= 50:
            action = "REDUCE"

        elif score >= 30 and context.pnl_percent >= 20:
            action = "PROFIT BOOK"

        else:
            action = "HOLD"

        if not reasons:
            reasons.append("No significant exit or profit-booking condition")

        return ExitAssessment(
            score=min(score, 100),
            action=action,
            reasons=reasons,
        )