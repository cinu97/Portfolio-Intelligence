"""Unit tests for plugin registration and V2 scoring compatibility."""

from __future__ import annotations

import unittest

from analytics.portfolio_context import PortfolioContext
from analytics.recommendation import RecommendationEngine
from analytics.rules.base import InvestmentRule, RuleResult
from analytics.rules.registry import RuleRegistry, create_default_registry
from analytics.scoring import ScoringEngine


class FixedRule(InvestmentRule):
    """Minimal rule used to test registry behavior without market dependencies."""

    key = "fixed"

    def __init__(self, score: int, reason: str) -> None:
        self.score = score
        self.reason = reason

    def evaluate(self, context: PortfolioContext) -> RuleResult:
        return RuleResult(self.score, [self.reason])


def sample_context() -> PortfolioContext:
    """Build inputs that exercise every existing V2 rule."""
    return PortfolioContext(
        symbol="TEST",
        quantity=1,
        average_price=100,
        invested_value=100,
        current_value=80,
        current_price=80,
        previous_close=83,
        pnl=-20,
        pnl_percent=-20,
        allocation_percent=1,
        discount_from_average=-20,
        day_percent=-3,
        t5_percent=-5,
        t7_percent=-7,
        week52_high=120,
        week52_low=60,
        range_percent=10,
        dma50=90,
        dma200=100,
    )


class RuleRegistryTests(unittest.TestCase):
    """Verify plugin registration, removal, and weighted evaluation."""

    def test_register_and_unregister_rules(self) -> None:
        registry = RuleRegistry()
        rule = FixedRule(10, "Fixed score")

        registry.register(rule)

        self.assertEqual(registry.rules, (rule,))
        self.assertIs(registry.unregister("fixed"), rule)
        self.assertEqual(registry.rules, ())

    def test_duplicate_keys_are_rejected(self) -> None:
        registry = RuleRegistry((FixedRule(10, "First"),))

        with self.assertRaises(ValueError):
            registry.register(FixedRule(20, "Second"))

    def test_rule_weights_scale_only_the_selected_rule(self) -> None:
        registry = RuleRegistry((FixedRule(10, "Fixed score"),))

        score, reasons = ScoringEngine.calculate(
            sample_context(),
            registry=registry,
            rule_weights={"fixed": 0.5},
        )

        self.assertEqual(score, 5)
        self.assertEqual(reasons, ["Fixed score"])

    def test_weighted_trace_rows_match_the_rule_total(self) -> None:
        score_result = ScoringEngine.evaluate(
            sample_context(),
            registry=create_default_registry(),
            rule_weights={"momentum": 0.25},
        )

        momentum_rows = [
            contribution
            for contribution in score_result.rule_breakdown
            if contribution.rule_key == "momentum"
        ]
        self.assertEqual(sum(row.score for row in momentum_rows), 8)
        self.assertEqual(sum(row.max_score for row in momentum_rows), 8)


class DefaultRuleCompatibilityTests(unittest.TestCase):
    """Verify that the default plugin registry preserves current V2 scoring."""

    def test_default_registry_has_the_legacy_rule_order(self) -> None:
        registry = create_default_registry()

        self.assertEqual(
            [rule.key for rule in registry.rules],
            [
                "average_buy",
                "allocation",
                "momentum",
                "fifty_two_week",
                "moving_average",
            ],
        )

    def test_default_rules_preserve_score_and_reasons(self) -> None:
        score, reasons = ScoringEngine.calculate(sample_context())

        self.assertEqual(score, 100)
        self.assertEqual(
            reasons,
            [
                "Trading >15% below average buy",
                "Significantly underweight",
                "Strong correction today",
                "Weak 5-day momentum",
                "Strong weekly correction",
                "Trading near 52-week low",
                "Trading below 50 DMA",
                "Trading below 200 DMA",
            ],
        )

    def test_score_result_exposes_individual_rule_contributions(self) -> None:
        score_result = ScoringEngine.evaluate(sample_context())

        self.assertEqual(score_result.total_score, 100)
        self.assertEqual(score_result.raw_score, 115)
        self.assertEqual(
            [contribution.label for contribution in score_result.rule_breakdown],
            [
                "Average Buy",
                "Allocation",
                "Momentum (Day)",
                "Momentum (5D)",
                "Momentum (7D)",
                "52 Week",
                "Moving Average (50 DMA)",
                "Moving Average (200 DMA)",
            ],
        )
        self.assertEqual(
            [contribution.max_score for contribution in score_result.rule_breakdown],
            [30, 20, 10, 10, 10, 20, 5, 10],
        )

    def test_recommendation_retains_the_rule_breakdown(self) -> None:
        recommendation = RecommendationEngine().generate(sample_context())

        self.assertEqual(recommendation.buy_score, 100)
        self.assertEqual(recommendation.action, "STRONG BUY")
        self.assertEqual(len(recommendation.rule_breakdown), 8)


if __name__ == "__main__":
    unittest.main()
