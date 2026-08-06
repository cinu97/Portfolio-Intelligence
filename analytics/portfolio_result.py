from dataclasses import dataclass

from analytics.portfolio_context import PortfolioContext
from analytics.recommendation import Recommendation
from market.models import MarketData
from portfolio.loader import Holding


@dataclass(slots=True)
class PortfolioResult:

    holding: Holding

    market: MarketData

    context: PortfolioContext

    recommendation: Recommendation
