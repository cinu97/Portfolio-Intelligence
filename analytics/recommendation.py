from __future__ import annotations

from dataclasses import dataclass

from market.models import MarketData


@dataclass(slots=True)
class Recommendation:
    symbol: str
    buy_score: int
    action: str
    suggested_amount: int
    reasons: list[str]


class RecommendationEngine:
    """
    Portfolio Intelligence Recommendation Engine (Version 1)

    Calculates:
    - Buy Score (0-100)
    - Action
    - Suggested investment amount
    - Reasons
    """

    def generate(self, market: MarketData) -> Recommendation:

        score = 50
        reasons: list[str] = []

        # -------------------------
        # Daily movement
        # -------------------------
        if market.day_change_percent <= -2:
            score += 20
            reasons.append("Strong correction today")

        elif market.day_change_percent <= -1:
            score += 10
            reasons.append("Price corrected today")

        elif market.day_change_percent >= 2:
            score -= 15
            reasons.append("Sharp rally today")

        elif market.day_change_percent >= 1:
            score -= 5
            reasons.append("Positive momentum today")

        # -------------------------
        # 5-Day comparison
        # -------------------------
        if market.t5_percent <= -5:
            score += 20
            reasons.append("Trading below 5-day close")

        elif market.t5_percent >= 5:
            score -= 10
            reasons.append("Already above 5-day close")

        # -------------------------
        # 7-Day comparison
        # -------------------------
        if market.t7_percent <= -7:
            score += 20
            reasons.append("Large 7-day correction")

        elif market.t7_percent >= 7:
            score -= 10
            reasons.append("Strong 7-day rally")

        # -------------------------
        # Clamp score
        # -------------------------
        score = max(0, min(score, 100))

        # -------------------------
        # Action
        # -------------------------
        if score >= 85:
            action = "STRONG BUY"
            amount = 5000

        elif score >= 75:
            action = "BUY"
            amount = 3000

        elif score >= 65:
            action = "ACCUMULATE"
            amount = 2000

        elif score >= 55:
            action = "WATCH"
            amount = 1000

        else:
            action = "HOLD"
            amount = 0

        if not reasons:
            reasons.append("No strong signal")

        return Recommendation(
            symbol=market.symbol,
            buy_score=score,
            action=action,
            suggested_amount=amount,
            reasons=reasons,
        )