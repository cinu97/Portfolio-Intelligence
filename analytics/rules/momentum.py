from dataclasses import dataclass

from analytics.portfolio_context import PortfolioContext
from analytics.rules.base import InvestmentRule, RuleContribution, RuleResult


@dataclass(slots=True)
class MomentumResult:
    score: int
    reasons: list[str]


class MomentumRule(InvestmentRule):
    """Score the existing daily, five-day, and seven-day pullback bands."""

    MAX_SCORE = 30
    key = "momentum"

    def evaluate(self, context: PortfolioContext) -> RuleResult:
        """Adapt the existing momentum calculation to the rule interface."""
        result = self.calculate(context.day_percent, context.t5_percent, context.t7_percent)
        day_score, day_reason = self._day_contribution(context.day_percent)
        five_day_score, five_day_reason = self._five_day_contribution(
            context.t5_percent,
        )
        seven_day_score, seven_day_reason = self._seven_day_contribution(
            context.t7_percent,
        )
        return RuleResult(
            score=result.score,
            reasons=result.reasons,
            max_score=self.MAX_SCORE,
            contributions=[
                RuleContribution(
                    rule_key=self.key,
                    label="Momentum (Day)",
                    score=day_score,
                    max_score=10,
                    reason=day_reason or "No material daily correction",
                ),
                RuleContribution(
                    rule_key=self.key,
                    label="Momentum (5D)",
                    score=five_day_score,
                    max_score=10,
                    reason=five_day_reason or "No material 5-day pullback",
                ),
                RuleContribution(
                    rule_key=self.key,
                    label="Momentum (7D)",
                    score=seven_day_score,
                    max_score=10,
                    reason=seven_day_reason or "No material 7-day pullback",
                ),
            ],
        )

    @classmethod
    def calculate(
        cls,
        day_percent: float,
        t5_percent: float,
        t7_percent: float,
    ) -> MomentumResult:

        day_score, day_reason = cls._day_contribution(day_percent)
        five_day_score, five_day_reason = cls._five_day_contribution(t5_percent)
        seven_day_score, seven_day_reason = cls._seven_day_contribution(t7_percent)

        score = day_score + five_day_score + seven_day_score
        reasons = [
            reason
            for reason in (day_reason, five_day_reason, seven_day_reason)
            if reason is not None
        ]

        return MomentumResult(
            score=score,
            reasons=reasons,
        )

    @staticmethod
    def _day_contribution(day_percent: float) -> tuple[int, str | None]:
        if day_percent <= -3:
            return 10, "Strong correction today"
        if day_percent <= -1:
            return 5, "Minor correction today"
        return 0, None

    @staticmethod
    def _five_day_contribution(t5_percent: float) -> tuple[int, str | None]:
        if t5_percent <= -5:
            return 10, "Weak 5-day momentum"
        if t5_percent <= -2:
            return 5, "Moderate 5-day pullback"
        return 0, None

    @staticmethod
    def _seven_day_contribution(t7_percent: float) -> tuple[int, str | None]:
        if t7_percent <= -7:
            return 10, "Strong weekly correction"
        if t7_percent <= -3:
            return 5, "Weekly pullback"
        return 0, None
