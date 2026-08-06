from __future__ import annotations

from dataclasses import dataclass

from analytics.scoring import ScoringEngine
from analytics.portfolio_context import PortfolioContext


@dataclass(slots=True)
class Recommendation:
    symbol: str
    buy_score: int
    action: str
    suggested_amount: int
    reasons: list[str]


class RecommendationEngine:

    def generate(self, portfolio: PortfolioContext) -> Recommendation:

        score, reasons = ScoringEngine.calculate(
            portfolio,
        )

        if score >= 90:

            action = "STRONG BUY"
            amount = 5000

        elif score >= 75:

            action = "BUY"
            amount = 3000

        elif score >= 60:

            action = "ACCUMULATE"
            amount = 2000

        elif score >= 40:

            action = "WATCH"
            amount = 1000

        else:

            action = "HOLD"
            amount = 0

        if not reasons:

            reasons.append(
                "No strong signal"
            )

        return Recommendation(

            symbol=portfolio.symbol,

            buy_score=score,

            action=action,

            suggested_amount=amount,

            reasons=reasons,
        )
