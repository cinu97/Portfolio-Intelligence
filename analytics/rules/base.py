"""Common contracts for pluggable portfolio scoring rules."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from analytics.portfolio_context import PortfolioContext


@dataclass(slots=True)
class RuleContribution:
    """One visible score contribution within an investment rule."""

    rule_key: str
    label: str
    score: int
    max_score: int
    reason: str


@dataclass(slots=True)
class RuleResult:
    """The score, maximum, reasons, and detailed trace produced by one rule."""

    score: int
    reasons: list[str]
    max_score: int = 0
    contributions: list[RuleContribution] = field(default_factory=list)


@dataclass(slots=True)
class RuleSetResult:
    """The combined result of evaluating a registry of investment rules."""

    score: int
    reasons: list[str]
    rule_breakdown: list[RuleContribution]


class InvestmentRule(ABC):
    """Interface implemented by every rule available to the scoring registry."""

    key: str

    @abstractmethod
    def evaluate(self, context: PortfolioContext) -> RuleResult:
        """Evaluate this rule against one normalized portfolio context."""
