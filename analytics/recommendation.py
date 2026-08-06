from __future__ import annotations

from dataclasses import dataclass, field

from analytics.scoring import ScoringEngine
from analytics.portfolio_context import PortfolioContext
from analytics.rules.base import RuleContribution


@dataclass(slots=True)
class Recommendation:
    symbol: str
    buy_score: int
    action: str
    suggested_amount: int
    reasons: list[str]
    rule_breakdown: list[RuleContribution] = field(default_factory=list)


class RecommendationEngine:
    """Map a V2 portfolio context score to the existing recommendation policy."""

    def generate(self, context: PortfolioContext) -> Recommendation:
        """Generate an action, amount, and reasons for a scoring context."""

        score_result = ScoringEngine.evaluate(context)
        score = score_result.total_score
        reasons = score_result.reasons

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

            symbol=context.symbol,

            buy_score=score,

            action=action,

            suggested_amount=amount,

            reasons=reasons,

            rule_breakdown=score_result.rule_breakdown,
        )
