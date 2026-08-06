"""Tests for the one-row-per-symbol Decision Trace worksheet model."""

from __future__ import annotations

import unittest

from analytics.recommendation import Recommendation
from analytics.rules.base import RuleContribution
from main import build_decision_trace_dataframe


def contribution(label: str, score: int) -> RuleContribution:
    """Create a trace contribution with an irrelevant maximum for this mapping test."""
    return RuleContribution("test", label, score, 10, "reason")


class DecisionTraceDataFrameTests(unittest.TestCase):
    """Verify the Decision Trace worksheet remains one row per symbol."""

    def test_builds_one_aggregated_row_for_each_recommendation(self) -> None:
        recommendation = Recommendation(
            symbol="TEST",
            buy_score=75,
            action="BUY",
            suggested_amount=3000,
            reasons=["First reason", "Second reason"],
            rule_breakdown=[
                contribution("Average Buy", 20),
                contribution("Allocation", 10),
                contribution("Momentum (Day)", 5),
                contribution("Momentum (5D)", 5),
                contribution("Momentum (7D)", 0),
                contribution("52 Week", 20),
                contribution("Moving Average (50 DMA)", 5),
                contribution("Moving Average (200 DMA)", 10),
            ],
        )

        dataframe = build_decision_trace_dataframe([(None, recommendation)])

        self.assertEqual(len(dataframe), 1)
        self.assertEqual(
            dataframe.columns.tolist(),
            [
                "Symbol", "Final Score", "Action", "Suggested Amount",
                "Average Buy Score", "Allocation Score", "Day Momentum",
                "5D Momentum", "7D Momentum", "52 Week Score",
                "50 DMA Score", "200 DMA Score", "Combined Reasons",
            ],
        )
        self.assertEqual(dataframe.iloc[0].to_dict(), {
            "Symbol": "TEST",
            "Final Score": 75,
            "Action": "BUY",
            "Suggested Amount": 3000,
            "Average Buy Score": 20,
            "Allocation Score": 10,
            "Day Momentum": 5,
            "5D Momentum": 5,
            "7D Momentum": 0,
            "52 Week Score": 20,
            "50 DMA Score": 5,
            "200 DMA Score": 10,
            "Combined Reasons": "First reason; Second reason",
        })
