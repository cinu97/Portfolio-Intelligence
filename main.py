from portfolio.loader import PortfolioLoader
from market.fetch_prices import MarketDataService
from analytics.recommendation import RecommendationEngine


def main():

    loader = PortfolioLoader()

    symbols = loader.get_symbols()

    market = MarketDataService()

    prices = market.fetch(symbols)

    engine = RecommendationEngine()

    recommendations = []

    for price in prices:

        recommendations.append(
            (
                price,
                engine.generate(price),
            )
        )

    recommendations.sort(
        key=lambda x: x[1].buy_score,
        reverse=True,
    )

    print()

    print("=" * 220)

    print(
        f"{'Rank':<5}"
        f"{'Symbol':<15}"
        f"{'Live':>10}"
        f"{'Prev':>20}"
        f"{'T5':>20}"
        f"{'T7':>20}"
        f"{'Score':>10}"
        f"{'Action':>15}"
        f"{'Amount':>12}"
    )

    print("=" * 220)

    for index, (market_data, recommendation) in enumerate(
        recommendations,
        start=1,
    ):

        print(
            f"{index:<5}"
            f"{market_data.symbol:<15}"
            f"{market_data.live_price:>10.2f}"

            f"{market_data.previous_close:>10.2f}"
            f" ({market_data.day_change_percent:+6.2f}%)"

            f"{market_data.t5_close:>10.2f}"
            f" ({market_data.t5_percent:+6.2f}%)"

            f"{market_data.t7_close:>10.2f}"
            f" ({market_data.t7_percent:+6.2f}%)"

            f"{recommendation.buy_score:>10}"

            f"{recommendation.action:>15}"

            f"{recommendation.suggested_amount:>12}"
        )

    print()
    print("=" * 220)


if __name__ == "__main__":
    main()