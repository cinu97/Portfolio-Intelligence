"""Application entry point for the portfolio intelligence batch run."""

from __future__ import annotations

import argparse
import logging

import pandas as pd

from analytics.portfolio_health import PortfolioHealthEngine
from analytics.portfolio_engine import PortfolioEngine
from analytics.portfolio_result import PortfolioResult
from analytics.recommendation import Recommendation
from database.sqlite import DatabaseManager
from gsheets.sheets import GoogleSheetsService
from market.models import MarketData
from portfolio.loader import PortfolioLoader
from utils.logger import setup_logger



LOGGER = logging.getLogger(__name__)

RecommendationPair = tuple[MarketData, Recommendation]


def persist_market_snapshots(
    results: list[PortfolioResult],
    database: DatabaseManager,
) -> list[RecommendationPair]:
    """Persist each result and return its market/recommendation pair."""
    recommendations: list[RecommendationPair] = []

    for result in results:
        database.save_market_snapshot(result.market, result.recommendation)
        recommendations.append((result.market, result.recommendation))

    return recommendations


def build_dashboard_dataframe(
    recommendations: list[RecommendationPair],
) -> pd.DataFrame:
    """Convert ranked recommendations to the existing dashboard schema plus 52W metrics."""

    dashboard_rows = []

    for market_data, recommendation in recommendations:

        week52_low = (
            market_data.week52_low
            if market_data.week52_low > 0
            else None
        )

        week52_high = (
            market_data.week52_high
            if market_data.week52_high > 0
            else None
        )

        percent_from_52w_high = None

        if week52_high is not None:
            percent_from_52w_high = round(
                (
                    (market_data.live_price - week52_high)
                    / week52_high
                ) * 100,
                2,
            )
            
        week52_low = (
            market_data.week52_low
            if market_data.week52_low > 0
            else None
        )

        week52_high = (
            market_data.week52_high
            if market_data.week52_high > 0
            else None
        )

        percent_from_52w_low = None
        percent_from_52w_high = None

        if week52_low is not None:
            percent_from_52w_low = round(
                (
                    (market_data.live_price - week52_low)
                    / week52_low
                ) * 100,
                2,
            )

        if week52_high is not None:
            percent_from_52w_high = round(
                (
                    (market_data.live_price - week52_high)
                    / week52_high
                ) * 100,
                2,
            )

        dashboard_rows.append(
            {
                # Existing columns — unchanged
                "Symbol": market_data.symbol,
                "Live": market_data.live_price,
                "Prev Close": market_data.previous_close,
                "Day %": market_data.day_change_percent,
                "T5 Close": market_data.t5_close,
                "T5 %": market_data.t5_percent,
                "T7 Close": market_data.t7_close,
                "T7 %": market_data.t7_percent,
                
                                # New columns
                "52W Low": week52_low,
                "52W High": week52_high,
                "% From 52W Low": percent_from_52w_low,
                "% From 52W High": percent_from_52w_high,
                
                #Old
                "Score": recommendation.buy_score,
                "Action": recommendation.action,
                "Amount": recommendation.suggested_amount,


            }
        )

    return pd.DataFrame(dashboard_rows)


def build_decision_trace_dataframe(
    recommendations: list[RecommendationPair],
) -> pd.DataFrame:
    """Convert each recommendation trace to one Sheets-ready summary row."""
    columns = [
        "Symbol",
        "Final Score",
        "Action",
        "Suggested Amount",
        "Average Buy Score",
        "Allocation Score",
        "Day Momentum",
        "5D Momentum",
        "7D Momentum",
        "52 Week Score",
        "50 DMA Score",
        "200 DMA Score",
        "Combined Reasons",
    ]
    trace_rows = []
    for _, recommendation in recommendations:
        scores_by_label = {
            contribution.label: contribution.score
            for contribution in recommendation.rule_breakdown
        }
        trace_rows.append(
            {
            "Symbol": recommendation.symbol,
            "Final Score": recommendation.buy_score,
            "Action": recommendation.action,
            "Suggested Amount": recommendation.suggested_amount,
            "Average Buy Score": scores_by_label.get("Average Buy", 0),
            "Allocation Score": scores_by_label.get("Allocation", 0),
            "Day Momentum": scores_by_label.get("Momentum (Day)", 0),
            "5D Momentum": scores_by_label.get("Momentum (5D)", 0),
            "7D Momentum": scores_by_label.get("Momentum (7D)", 0),
            "52 Week Score": scores_by_label.get("52 Week", 0),
            "50 DMA Score": scores_by_label.get("Moving Average (50 DMA)", 0),
            "200 DMA Score": scores_by_label.get("Moving Average (200 DMA)", 0),
            "Combined Reasons": "; ".join(recommendation.reasons),
            }
        )
    return pd.DataFrame(trace_rows, columns=columns)


def publish_reports(
    dashboard: pd.DataFrame,
    holdings: pd.DataFrame,
    decision_trace: pd.DataFrame,
    investment_plan: pd.DataFrame,

) -> None:
    """Publish existing reports and the per-rule decision trace worksheet."""
    try:
        google = GoogleSheetsService()
        google.dashboard(dashboard)
        google.opportunities(dashboard.head(10))
        google.history(dashboard)
        google.portfolio(holdings)
        google.decision_trace(decision_trace)
        google.investment_plan(investment_plan)
    except Exception:
        LOGGER.exception("Google Sheets publishing failed; results remain available locally.")


def print_recommendations(recommendations: list[RecommendationPair]) -> None:
    """Render the existing fixed-width console recommendation table."""
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

    for index, (market_data, recommendation) in enumerate(recommendations, start=1):
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


def print_decision_trace(recommendations: list[RecommendationPair]) -> None:
    """Render the optional per-rule scoring breakdown for each recommendation."""
    print()
    print("DECISION TRACE")
    print("=" * 100)

    for _, recommendation in recommendations:
        print(
            f"{recommendation.symbol} | "
            f"Score: {recommendation.buy_score} | "
            f"Action: {recommendation.action} | "
            f"Amount: {recommendation.suggested_amount}"
        )
        for contribution in recommendation.rule_breakdown:
            print(
                f"  {contribution.label:<26} "
                f"{contribution.score:>3}/{contribution.max_score:<3} "
                f"{contribution.reason}"
            )


def main(detailed: bool = False) -> None:
    """Run portfolio analysis and publish its existing outputs."""
    setup_logger()
    loader = PortfolioLoader()
    database = DatabaseManager()
    database.initialize()

    recommendations = persist_market_snapshots(PortfolioEngine().run(), database)
    recommendations.sort(key=lambda item: item[1].buy_score, reverse=True)

    from analytics.investment_planner import InvestmentPlanner
    from config.settings import CONFIG

    planner_config = CONFIG.get("investment_planner", {})

    investment_plan = InvestmentPlanner.create_plan(
        recommendations=recommendations,
        available_cash=planner_config.get("available_cash", 20000),
    )
    investment_plan_df = build_investment_plan_dataframe(
    investment_plan
    )
    dashboard = build_dashboard_dataframe(recommendations)
    decision_trace = build_decision_trace_dataframe(recommendations)
    publish_reports(
        dashboard,
        loader.load_holdings(),
        decision_trace,
        investment_plan_df,
    )
    print_recommendations(recommendations)
    print_investment_plan(investment_plan)
    if detailed:
        print_decision_trace(recommendations)

def print_investment_plan(plan):
    print()
    print("=" * 60)
    print("Investment Plan")
    print("=" * 60)

    total = 0

    for item in plan:
        print(
            f"{item.symbol:<15}"
            f"₹{item.amount:<8}"
            f"Score: {item.score:<3}"
        )
        print(f"   Reason: {item.reason}")
        total += item.amount

    print("-" * 60)
    print(f"Total Planned Investment : ₹{total}")
    
def parse_arguments() -> argparse.Namespace:
    """Parse the optional console decision-trace switch."""
    parser = argparse.ArgumentParser(
        description="Generate portfolio recommendations."
    )

    parser.add_argument(
        "--detailed",
        action="store_true",
        help="Print the rule-by-rule decision trace after the recommendation table.",
    )

    return parser.parse_args()


def build_investment_plan_dataframe(plan) -> pd.DataFrame:
    rows = []

    for item in plan:
        rows.append(
            {
                "Symbol": item.symbol,
                "Suggested Amount": item.amount,
                "Score": item.score,
                "Reason": item.reason,
            }
        )

    return pd.DataFrame(rows)


if __name__ == "__main__":
    main(detailed=parse_arguments().detailed)