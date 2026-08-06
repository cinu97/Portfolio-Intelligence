from dataclasses import dataclass


@dataclass(slots=True)
class MovingAverageResult:
    score: int
    reasons: list[str]


class MovingAverageRule:

    @classmethod
    def calculate(
        cls,
        current: float,
        dma50: float,
        dma200: float,
    ):

        score = 0

        reasons = []

        if current < dma50:

            score += 5
            reasons.append("Trading below 50 DMA")

        if current < dma200:

            score += 10
            reasons.append("Trading below 200 DMA")

        return MovingAverageResult(
            score=score,
            reasons=reasons,
        )