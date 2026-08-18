from portfolio.loader import Holding, PortfolioLoader
from market.fetch_prices import MarketDataService
from analytics.context_builder import ContextBuilder
from analytics.recommendation import RecommendationEngine
from analytics.portfolio_result import PortfolioResult


class PortfolioEngine:
    """Coordinate the V2 portfolio-context and recommendation workflow."""

    def __init__(self) -> None:

        self.loader = PortfolioLoader()

        self.market = MarketDataService()

        self.recommendation = RecommendationEngine()

    def run(self) -> list[PortfolioResult]:
        """Build V2 contexts and recommendations for holdings and watchlist items."""
        holdings = self.loader.load_holding_records()
        market_data = self.market.fetch(self.loader.get_symbols())

        total_portfolio_value = sum(
            holdings.get(item.symbol, Holding(symbol=item.symbol)).quantity * item.live_price
            for item in market_data
        )

        results: list[PortfolioResult] = []
        for item in market_data:
            holding = holdings.get(item.symbol, Holding(symbol=item.symbol))
            context = ContextBuilder.build(
                holding,
                item,
                total_portfolio_value,
            )
            recommendation = self.recommendation.generate(
                context,
                inav=item.inav,
                inav_premium_discount_pct=item.inav_premium_discount_pct,
                inav_signal=item.inav_signal,
            )
            results.append(
                PortfolioResult(
                    holding=holding,
                    market=item,
                    context=context,
                    recommendation=recommendation,
                )
            )

        return results
