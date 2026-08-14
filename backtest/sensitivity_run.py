from __future__ import annotations

import sys

import yfinance as yf

from backtest.sensitivity import run_sensitivity


def yahoo_symbol(symbol: str) -> str:
    """Convert portfolio symbols into Yahoo Finance symbols."""

    base = symbol.removesuffix("-RR")

    return f"{base}.NS"


def run(symbol: str) -> None:

    print()
    print("=" * 90)
    print(f"PARAMETER SENSITIVITY: {symbol}")
    print("=" * 90)

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

    # Entry must always be higher than exit.
    entry_thresholds = [
        40,
        45,
        50,
        55,
    ]

    exit_thresholds = [
        20,
        25,
        30,
        35,
        40,
    ]

    results = run_sensitivity(
        symbol=symbol,
        history=history,
        entry_thresholds=entry_thresholds,
        exit_thresholds=exit_thresholds,
    )

    if results.empty:
        print("No sensitivity results.")
        return

    # Remove parameter combinations that did not produce
    # a valid backtest result.
    valid_results = results.dropna(
        subset=[
            "CAGR %",
            "Total Return %",
            "Max Drawdown %",
            "Sharpe",
            "Time Invested %",
            "Trade Count",
        ]
    ).copy()

    if valid_results.empty:
        print("No valid sensitivity results were produced.")
        return

    print()
    print("TOP RESULTS")
    print("=" * 90)

    print(
        valid_results.head(15).to_string(
            index=False
        )
    )

    print()
    print("=" * 90)
    print("BEST CAGR")
    print("=" * 90)

    best_cagr = valid_results.iloc[0]

    print(
        f"Entry Score     : {best_cagr['Entry Score']}"
    )

    print(
        f"Exit Score      : {best_cagr['Exit Score']}"
    )

    print(
        f"CAGR            : {best_cagr['CAGR %']:.2f}%"
    )

    print(
        f"Total Return    : {best_cagr['Total Return %']:.2f}%"
    )

    print(
        f"Max Drawdown    : {best_cagr['Max Drawdown %']:.2f}%"
    )

    print(
        f"Sharpe          : {best_cagr['Sharpe']:.2f}"
    )

    print(
        f"Time Invested   : {best_cagr['Time Invested %']:.2f}%"
    )

    print(
        f"Trade Count     : {int(best_cagr['Trade Count'])}"
    )

    print()
    print("=" * 90)


if __name__ == "__main__":

    symbol = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "NIFTYBEES"
    )

    run(symbol)