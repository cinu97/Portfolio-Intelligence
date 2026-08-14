from __future__ import annotations

import sys

import yfinance as yf

from backtest.model_comparison import compare_models


def yahoo_symbol(symbol: str) -> str:
    return f"{symbol.removesuffix('-RR')}.NS"


def run(symbol: str) -> None:

    print()
    print("=" * 90)
    print(f"MODEL COMPARISON: {symbol}")
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

    results = compare_models(history)

    columns = [
        "Model",
        "CAGR %",
        "Total Return %",
        "Max Drawdown %",
        "Sharpe Ratio",
        "Time Invested %",
        "Trade Count",
    ]

    print()
    print("MODEL COMPARISON")
    print("=" * 90)

    print(
        results[columns].to_string(
            index=False
        )
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