from __future__ import annotations

import sys
import pandas as pd

import yfinance as yf

from backtest.walk_forward import run_walk_forward


def yahoo_symbol(symbol: str) -> str:
    return f"{symbol.removesuffix('-RR')}.NS"


def run(symbol: str) -> None:

    print()
    print("=" * 100)
    print(f"WALK-FORWARD VALIDATION: {symbol}")
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

    results, parameters = run_walk_forward(
        history
    )

    if results.empty:
        print("No walk-forward results.")
        return

    print()
    print("SELECTED PARAMETERS")
    print("=" * 100)

    print(
        parameters.to_string(
            index=False
        )
    )

    print()
    print("OUT-OF-SAMPLE RESULTS")
    print("=" * 100)

    display_results = results.copy()

    for column in [
        "Train Start",
        "Train End",
        "Test Start",
        "Test End",
    ]:
        display_results[column] = pd.to_datetime(
            display_results[column]
        ).dt.strftime("%Y-%m-%d")

    print(
        display_results.to_string(
            index=False
        )
    )

    print()
    print("SUMMARY")
    print("=" * 100)

    print(
        f"Average Test CAGR       : "
        f"{results['Test CAGR %'].mean():.2f}%"
    )

    print(
        f"Average Test Sharpe     : "
        f"{results['Test Sharpe'].mean():.2f}"
    )

    print(
        f"Average Test Max DD     : "
        f"{results['Test Max DD %'].mean():.2f}%"
    )

    print(
        f"Average Test Exposure   : "
        f"{results['Test Exposure %'].mean():.2f}%"
    )

    print(
        f"Total Test Trades       : "
        f"{int(results['Test Trades'].sum())}"
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