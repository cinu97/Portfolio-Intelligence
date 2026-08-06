from dataclasses import dataclass

from analytics.portfolio_context import PortfolioContext
from analytics.recommendation import Recommendation
from analytics.rules.base import RuleContribution
from market.models import MarketData
from portfolio.loader import Holding


@dataclass(slots=True)
class PortfolioResult:
    """The holding, market data, context, and recommendation for one symbol."""

    holding: Holding

    market: MarketData

    context: PortfolioContext

    recommendation: Recommendation

    @property
    def total_score(self) -> int:
        """Expose the final capped recommendation score."""
        return self.recommendation.buy_score

    @property
    def action(self) -> str:
        """Expose the recommendation action."""
        return self.recommendation.action

    @property
    def amount(self) -> int:
        """Expose the suggested investment amount."""
        return self.recommendation.suggested_amount

    @property
    def rule_breakdown(self) -> list[RuleContribution]:
        """Expose the score contributions that produced the recommendation."""
        return self.recommendation.rule_breakdown
