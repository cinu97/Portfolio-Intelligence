"""Pluggable scoring rules and their registry."""

from analytics.rules.base import InvestmentRule, RuleResult
from analytics.rules.registry import RuleRegistry, create_default_registry

__all__ = [
    "InvestmentRule",
    "RuleRegistry",
    "RuleResult",
    "create_default_registry",
]
