from dataclasses import dataclass


@dataclass(slots=True)
class MomentumResult:
    score: int
    reasons: list[str]


class MomentumRule:

    MAX_SCORE = 30

    @classmethod
    def calculate(
        cls,
        day_percent: float,
        t5_percent: float,
        t7_percent: float,
    ) -> MomentumResult:

        score = 0
        reasons = []

        # Today's correction
        if day_percent <= -3:
            score += 10
            reasons.append("Strong correction today")

        elif day_percent <= -1:
            score += 5
            reasons.append("Minor correction today")

        # 5-day momentum
        if t5_percent <= -5:
            score += 10
            reasons.append("Weak 5-day momentum")

        elif t5_percent <= -2:
            score += 5
            reasons.append("Moderate 5-day pullback")

        # 7-day momentum
        if t7_percent <= -7:
            score += 10
            reasons.append("Strong weekly correction")

        elif t7_percent <= -3:
            score += 5
            reasons.append("Weekly pullback")

        return MomentumResult(
            score=score,
            reasons=reasons,
        )