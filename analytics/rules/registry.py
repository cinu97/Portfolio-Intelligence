"""Registration and evaluation of pluggable portfolio scoring rules."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import replace

from analytics.portfolio_context import PortfolioContext
from analytics.rules.base import (
    InvestmentRule,
    RuleContribution,
    RuleResult,
    RuleSetResult,
)


class RuleRegistry:
    """An ordered collection of independently evaluable investment rules."""

    def __init__(self, rules: Iterable[InvestmentRule] = ()) -> None:
        self._rules: dict[str, InvestmentRule] = {}
        for rule in rules:
            self.register(rule)

    @property
    def rules(self) -> tuple[InvestmentRule, ...]:
        """Return registered rules in their deterministic evaluation order."""
        return tuple(self._rules.values())

    def register(self, rule: InvestmentRule) -> None:
        """Add a rule, rejecting duplicate keys to avoid accidental overrides."""
        if rule.key in self._rules:
            raise ValueError(f"A rule is already registered for key '{rule.key}'.")

        self._rules[rule.key] = rule

    def unregister(self, key: str) -> InvestmentRule:
        """Remove and return a registered rule by key."""
        return self._rules.pop(key)

    def evaluate(
        self,
        context: PortfolioContext,
        rule_weights: Mapping[str, float],
    ) -> RuleSetResult:
        """Evaluate all rules using configurable score multipliers."""
        score = 0
        reasons: list[str] = []
        rule_breakdown: list[RuleContribution] = []

        for rule in self.rules:
            result = rule.evaluate(context)
            weight = rule_weights.get(rule.key, 1.0)
            score += int(round(result.score * weight))
            reasons.extend(result.reasons)
            rule_breakdown.extend(
                self._weighted_contributions(rule, result, weight)
            )

        return RuleSetResult(score, reasons, rule_breakdown)

    @staticmethod
    def _weighted_contributions(
        rule: InvestmentRule,
        result: RuleResult,
        weight: float,
    ) -> list[RuleContribution]:
        """Apply a rule's multiplier to its trace contributions."""
        contributions = result.contributions or [
            RuleContribution(
                rule_key=rule.key,
                label=rule.key.replace("_", " ").title(),
                score=result.score,
                max_score=result.max_score,
                reason="; ".join(result.reasons),
            )
        ]
        weighted_contributions = [
            RuleContribution(
                rule_key=contribution.rule_key,
                label=contribution.label,
                score=int(round(contribution.score * weight)),
                max_score=int(round(contribution.max_score * weight)),
                reason=contribution.reason,
            )
            for contribution in contributions
        ]
        return RuleRegistry._align_weighted_total(
            weighted_contributions,
            target_score=int(round(result.score * weight)),
            target_max_score=int(round(result.max_score * weight)),
        )

    @staticmethod
    def _align_weighted_total(
        contributions: list[RuleContribution],
        target_score: int,
        target_max_score: int,
    ) -> list[RuleContribution]:
        """Keep rounded detailed rows aligned with the rounded rule total."""
        if not contributions:
            return contributions

        score_adjustment = target_score - sum(
            contribution.score for contribution in contributions
        )
        max_score_adjustment = target_max_score - sum(
            contribution.max_score for contribution in contributions
        )
        if score_adjustment == 0 and max_score_adjustment == 0:
            return contributions

        last = contributions[-1]
        contributions[-1] = replace(
            last,
            score=last.score + score_adjustment,
            max_score=last.max_score + max_score_adjustment,
        )
        return contributions


def create_default_registry() -> RuleRegistry:
    """Create the existing V2 rule set in its established evaluation order."""
    from analytics.rules.allocation import AllocationRule
    from analytics.rules.average_buy import AverageBuyRule
    from analytics.rules.fifty_two_week import FiftyTwoWeekRule
    from analytics.rules.momentum import MomentumRule
    from analytics.rules.moving_average import MovingAverageRule

    return RuleRegistry(
        (
            AverageBuyRule(),
            AllocationRule(),
            MomentumRule(),
            FiftyTwoWeekRule(),
            MovingAverageRule(),
        )
    )
