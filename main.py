from database.sqlite import DatabaseManager
from portfolio.loader import PortfolioLoader
from market.fetch_prices import MarketDataService
from analytics.recommendation import RecommendationEngine
from gsheets.sheets import GoogleSheetsService
import pandas as pd

print("=== MAIN STARTED ===")
def main():

    loader = PortfolioLoader()

    symbols = loader.get_symbols()

    market = MarketDataService()

    prices = market.fetch(symbols)

    engine = RecommendationEngine()

    database = DatabaseManager()

    database.initialize()
    
    google = GoogleSheetsService()

    recommendations = []

    for price in prices:

        recommendation = engine.generate(price)

        database.save_market_snapshot(
            price,
            recommendation,
        )

        recommendations.append(
            (
                price,
                recommendation,
            )
        )

    recommendations.sort(
        key=lambda x: x[1].buy_score,
        reverse=True,
    )
    
    dashboard_rows = []

    for market_data, recommendation in recommendations:

        dashboard_rows.append(
            {
                "Symbol": market_data.symbol,
                "Live": market_data.live_price,
                "Prev Close": market_data.previous_close,
                "Day %": market_data.day_change_percent,
                "T5 Close": market_data.t5_close,
                "T5 %": market_data.t5_percent,
                "T7 Close": market_data.t7_close,
                "T7 %": market_data.t7_percent,
                "Score": recommendation.buy_score,
                "Action": recommendation.action,
                "Amount": recommendation.suggested_amount,
            }
        )

    dashboard_df = pd.DataFrame(dashboard_rows)

    google.dashboard(dashboard_df)
    
    top_df = dashboard_df.head(10)

    google.opportunities(top_df)
    
    google.history(dashboard_df)
    
    holdings = loader.load_holdings()

    google.portfolio(holdings)

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