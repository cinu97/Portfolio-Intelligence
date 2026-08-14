from __future__ import annotations

import sys

import yfinance as yf

from backtest.engine import BacktestEngine
from backtest.metrics import (
    calculate_buy_and_hold_metrics,
    calculate_metrics,
)


def yahoo_symbol(symbol: str) -> str:
    """Convert portfolio symbols into Yahoo Finance symbols."""

    base = symbol.removesuffix("-RR")

    return f"{base}.NS"


def print_metrics(
    title: str,
    metrics: dict[str, float],
) -> None:

    print()
    print(title)
    print("-" * 70)

    for name, value in metrics.items():

        if isinstance(value, float):
            print(
                f"{name:<30}: {value:,.2f}"
            )
        else:
            print(
                f"{name:<30}: {value}"
            )


def run(symbol: str) -> None:

    print()
    print("=" * 70)
    print(f"BACKTEST: {symbol}")
    print("=" * 70)

    ticker = yahoo_symbol(symbol)

    print(f"Yahoo symbol : {ticker}")
    print("Downloading 5 years of historical data...")

    history = yf.Ticker(ticker).history(
        period="5y"
    )

    if history.empty:
        raise RuntimeError(
            f"No historical data returned for {ticker}"
        )

    print(
        f"Downloaded {len(history)} trading sessions"
    )

    engine = BacktestEngine(
        initial_capital=100_000,
        buy_threshold=45,
    )

    result = engine.run(
        symbol=symbol,
        history=history,
    )

    strategy_metrics = calculate_metrics(
        result.equity_curve,
        result.initial_capital,
    )

    buy_hold_metrics = calculate_buy_and_hold_metrics(
        history,
        result.initial_capital,
    )

    print_metrics(
        "STRATEGY PERFORMANCE",
        strategy_metrics,
    )

    print_metrics(
        "BUY & HOLD PERFORMANCE",
        buy_hold_metrics,
    )

    print()
    print("=" * 70)
    print("COMPARISON")
    print("=" * 70)

    strategy_cagr = strategy_metrics.get(
        "CAGR %",
        0,
    )

    buy_hold_cagr = buy_hold_metrics.get(
        "CAGR %",
        0,
    )

    strategy_return = strategy_metrics.get(
        "Total Return %",
        0,
    )

    buy_hold_return = buy_hold_metrics.get(
        "Total Return %",
        0,
    )

    print(
        f"{'Metric':<30}"
        f"{'Strategy':>15}"
        f"{'Buy & Hold':>15}"
    )

    print("-" * 60)

    print(
        f"{'Total Return %':<30}"
        f"{strategy_return:>15.2f}"
        f"{buy_hold_return:>15.2f}"
    )

    print(
        f"{'CAGR %':<30}"
        f"{strategy_cagr:>15.2f}"
        f"{buy_hold_cagr:>15.2f}"
    )

    print(
        f"{'Max Drawdown %':<30}"
        f"{strategy_metrics.get('Max Drawdown %', 0):>15.2f}"
        f"{buy_hold_metrics.get('Max Drawdown %', 0):>15.2f}"
    )

    print(
        f"{'Sharpe Ratio':<30}"
        f"{strategy_metrics.get('Sharpe Ratio', 0):>15.2f}"
        f"{buy_hold_metrics.get('Sharpe Ratio', 0):>15.2f}"
    )

    print()

    if strategy_cagr > buy_hold_cagr:
        print("RESULT: Strategy CAGR beats Buy & Hold.")
    else:
        print("RESULT: Strategy CAGR does NOT beat Buy & Hold.")

    print()
    print("TRADES")
    print("-" * 70)

    for trade in result.trades:

        print(
            f"{trade.date.date()} | "
            f"{trade.action:<4} | "
            f"Price ₹{trade.price:,.2f} | "
            f"Score {trade.score:<3} | "
            f"Portfolio ₹{trade.portfolio_value:,.2f}"
        )

    print()
    print("=" * 70)


if __name__ == "__main__":

    symbol = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "NIFTYBEES"
    )

    run(symbol)