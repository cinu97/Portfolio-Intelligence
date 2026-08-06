"""V2 score aggregation using the pluggable investment-rule registry."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from analytics.portfolio_context import PortfolioContext
from analytics.rules.base import RuleContribution
from analytics.rules.registry import RuleRegistry, create_default_registry
from config.settings import CONFIG


def configured_rule_weights() -> dict[str, float]:
    """Load score multipliers while preserving 1.0 for omitted rule keys."""
    configured_weights = CONFIG.get("rule_weights", {})
    return {
        key: float(weight)
        for key, weight in configured_weights.items()
    }


@dataclass(slots=True)
class ScoreResult:
    """The final capped score together with its rule-level decision trace."""

    total_score: int
    raw_score: int
    reasons: list[str]
    rule_breakdown: list[RuleContribution]


class ScoringEngine:
    """Aggregate registered V2 rule scores and explanation strings."""

    @staticmethod
    def evaluate(
        context: PortfolioContext,
        registry: RuleRegistry | None = None,
        rule_weights: Mapping[str, float] | None = None,
    ) -> ScoreResult:
        """Evaluate registered rules and return the final score with its trace.

        Callers may inject a registry and weights to test or customize the rule set.
        The default registry and 1.0 multipliers preserve current behavior.
        """
        active_registry = registry or create_default_registry()
        active_weights = (
            configured_rule_weights()
            if rule_weights is None
            else rule_weights
        )
        result = active_registry.evaluate(context, active_weights)
        return ScoreResult(
            total_score=min(result.score, 100),
            raw_score=result.score,
            reasons=result.reasons,
            rule_breakdown=result.rule_breakdown,
        )

    @staticmethod
    def calculate(
        context: PortfolioContext,
        registry: RuleRegistry | None = None,
        rule_weights: Mapping[str, float] | None = None,
    ) -> tuple[int, list[str]]:
        """Return the legacy score/reasons tuple for existing callers."""
        result = ScoringEngine.evaluate(context, registry, rule_weights)
        return result.total_score, result.reasons
