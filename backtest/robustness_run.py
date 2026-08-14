from __future__ import annotations

import sys

import pandas as pd
import yfinance as yf

from backtest.robustness import run_robustness


def yahoo_symbol(symbol: str) -> str:
    return f"{symbol.removesuffix('-RR')}.NS"


def run(symbol: str) -> None:

    print()
    print("=" * 100)
    print(f"ROBUSTNESS VALIDATION: {symbol}")
    print("=" * 100)

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

    results, summary = run_robustness(
        history
    )

    if results.empty:
        print("No robustness results.")
        return

    date_columns = [
        "Train Start",
        "Train End",
        "Test Start",
        "Test End",
    ]

    display_results = results.copy()

    for column in date_columns:
        display_results[column] = pd.to_datetime(
            display_results[column]
        ).dt.strftime("%Y-%m-%d")

    print()
    print("ROBUSTNESS RESULTS")
    print("=" * 100)

    print(
        display_results.to_string(
            index=False
        )
    )

    print()
    print("SUMMARY")
    print("=" * 100)

    display_summary = summary.copy()

    print(
        display_summary.to_string(
            index=False
        )
    )

    print()
    print("DECISION")
    print("=" * 100)

    positive_periods = int(
        summary.iloc[0]["Positive Test Periods"]
    )

    negative_periods = int(
        summary.iloc[0]["Negative Test Periods"]
    )

    avg_sharpe = float(
        summary.iloc[0]["Average Test Sharpe"]
    )

    avg_cagr = float(
        summary.iloc[0]["Average Test CAGR %"]
    )

    if (
        negative_periods == 0
        and positive_periods >= 2
        and avg_sharpe > 0
        and avg_cagr > 0
    ):
        print(
            "PASS: Strategy shows positive and "
            "consistent out-of-sample behavior."
        )
    else:
        print(
            "FAIL: Strategy is not yet robust "
            "enough for production."
        )

    print()
    print("=" * 100)


if __name__ == "__main__":

    symbol = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "NIFTYBEES"
    )

    run(symbol)