from dataclasses import dataclass


@dataclass(slots=True)
class AllocationResult:
    score: int
    reason: str


class AllocationRule:

    MAX_SCORE = 20

    @classmethod
    def calculate(
        cls,
        allocation_percent: float,
        target_percent: float = 5.0,
    ) -> AllocationResult:

        if allocation_percent <= target_percent * 0.40:
            return AllocationResult(
                20,
                "Significantly underweight",
            )

        if allocation_percent <= target_percent * 0.60:
            return AllocationResult(
                15,
                "Underweight",
            )

        if allocation_percent <= target_percent:
            return AllocationResult(
                10,
                "Near target allocation",
            )

        if allocation_percent <= target_percent * 1.20:
            return AllocationResult(
                5,
                "Slightly overweight",
            )

        return AllocationResult(
            0,
            "Overweight",
        )