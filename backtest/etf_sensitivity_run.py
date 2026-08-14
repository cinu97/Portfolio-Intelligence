from __future__ import annotations

import sys

import yfinance as yf

from backtest.etf_sensitivity import run_etf_sensitivity


def yahoo_symbol(symbol: str) -> str:
    return f"{symbol.removesuffix('-RR')}.NS"


def run(symbol: str) -> None:

    print()
    print("=" * 100)
    print(f"ETF-FRIENDLY SENSITIVITY: {symbol}")
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

    results = run_etf_sensitivity(history)

    if results.empty:
        print("No valid sensitivity results.")
        return

    print()
    print("TOP RESULTS")
    print("=" * 100)

    print(
        results.head(20).to_string(
            index=False
        )
    )

    print()
    print("BEST RISK-ADJUSTED RESULTS")
    print("=" * 100)

    risk_results = results[
        (results["Sharpe"] >= 0.80)
        & (results["Time Invested %"] >= 40)
        & (results["Trade Count"] >= 10)
    ].copy()

    if risk_results.empty:
        print(
            "No configuration met all risk/exposure filters."
        )
    else:
        risk_results = risk_results.sort_values(
            by=["Sharpe", "CAGR %"],
            ascending=False,
        )

        print(
            risk_results.head(10).to_string(
                index=False
            )
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