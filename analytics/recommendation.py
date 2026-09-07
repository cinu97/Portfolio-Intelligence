from __future__ import annotations

from dataclasses import dataclass, field

from analytics.scoring import ScoringEngine
from analytics.portfolio_context import PortfolioContext
from analytics.rules.base import RuleContribution
from analytics.intelligence.models import (
    Confidence,
    IntelligenceSignal,
    SignalDirection,
)
from analytics.intelligence.intelligence import NewsIntelligence


@dataclass(slots=True)
class Recommendation:
    symbol: str
    buy_score: int
    action: str
    suggested_amount: int
    reasons: list[str]
    rule_breakdown: list[RuleContribution] = field(default_factory=list)
    intelligence: IntelligenceSignal | None = None


class RecommendationEngine:
    """Map portfolio score + bounded news intelligence to a recommendation."""

    def __init__(self) -> None:
        self.news_intelligence = NewsIntelligence()

    @staticmethod
    def _news_modifier(
        intelligence: IntelligenceSignal,
    ) -> int:
        """
        Convert news intelligence into a small bounded modifier.

        Technical/rule score remains the primary signal.
        News can influence the score by only +/- 1 to +/- 3.
        """

        if intelligence.direction == SignalDirection.NEUTRAL:
            return 0

        modifiers = {
            Confidence.HIGH: 3,
            Confidence.MEDIUM: 2,
            Confidence.LOW: 1,
        }

        modifier = modifiers.get(
            intelligence.confidence,
            0,
        )

        if intelligence.direction == SignalDirection.BEARISH:
            modifier = -modifier

        return modifier

    def generate(
        self,
        context: PortfolioContext,
        inav: float | None = None,
        inav_premium_discount_pct: float | None = None,
        inav_signal: str = "N/A",
    ) -> Recommendation:

        # ---------------------------------------------------------------
        # 1. Primary technical/rule score
        # ---------------------------------------------------------------
        score_result = ScoringEngine.evaluate(
            context
        )

        base_score = score_result.total_score

        reasons = list(
            score_result.reasons
        )

        # ---------------------------------------------------------------
        # 2. News intelligence
        # ---------------------------------------------------------------
        intelligence = self.news_intelligence.evaluate(
            context.symbol
        )

        news_modifier = self._news_modifier(
            intelligence
        )

        # ---------------------------------------------------------------
        # 3. Apply bounded news modifier
        # ---------------------------------------------------------------
        score = max(
            0,
            min(
                100,
                base_score + news_modifier,
            ),
        )

        if news_modifier != 0:

            reasons.append(
                f"News/Macro: "
                f"{intelligence.direction.value} "
                f"{news_modifier:+d} "
                f"({intelligence.confidence.value} confidence)"
            )

            reasons.extend(
                f"News evidence: {reason}"
                for reason in intelligence.reasons[:3]
            )

        # ---------------------------------------------------------------
        # 4. Existing recommendation policy
        # ---------------------------------------------------------------
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

        # ---------------------------------------------------------------
        # 5. iNAV execution filter
        # ---------------------------------------------------------------
        # iNAV is an execution filter, NOT part of the technical score.
        if (
            amount > 0
            and inav_premium_discount_pct is not None
            and inav_signal not in {
                "UNAVAILABLE",
                "N/A",
            }
        ):

            premium = (
                inav_premium_discount_pct
            )

            if premium > 0.50:

                action = "WAIT"
                amount = 0

                reasons.append(
                    f"iNAV execution filter: "
                    f"LTP is {premium:.2f}% above iNAV; "
                    "wait for a better entry."
                )

            elif premium > 0.25:

                action = "WAIT"
                amount = 0

                reasons.append(
                    f"iNAV execution filter: "
                    f"LTP is {premium:.2f}% above iNAV; "
                    "premium is above the 0.25% entry threshold."
                )

            elif premium <= 0:

                reasons.append(
                    f"iNAV execution filter: "
                    f"LTP is {abs(premium):.2f}% below iNAV; "
                    "favorable entry."
                )

            else:

                reasons.append(
                    f"iNAV execution filter: "
                    f"LTP is {premium:.2f}% above iNAV; "
                    "within the 0.25% tolerance."
                )

        return Recommendation(
            symbol=context.symbol,
            buy_score=score,
            action=action,
            suggested_amount=amount,
            reasons=reasons,
            rule_breakdown=score_result.rule_breakdown,
            intelligence=intelligence,
        )