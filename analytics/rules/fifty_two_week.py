from dataclasses import dataclass


@dataclass(slots=True)
class FiftyTwoWeekResult:
    score: int
    reasons: list[str]


class FiftyTwoWeekRule:

    @classmethod
    def calculate(
        cls,
        range_percent: float,
    ) -> FiftyTwoWeekResult:

        score = 0
        reasons = []

        if range_percent <= 20:

            score = 20
            reasons.append("Trading near 52-week low")

        elif range_percent <= 40:

            score = 15
            reasons.append("Trading in lower 40% of yearly range")

        elif range_percent <= 60:

            score = 10
            reasons.append("Trading in middle of yearly range")

        elif range_percent <= 80:

            score = 5
            reasons.append("Trading near yearly high")

        else:

            score = 0
            reasons.append("Trading close to 52-week high")

        return FiftyTwoWeekResult(
            score=score,
            reasons=reasons,
        )