from __future__ import annotations

import sys

import yfinance as yf

from backtest.score_diagnostics import (
    calculate_score_components,
    summarize_scores,
)


def yahoo_symbol(symbol: str) -> str:
    """Convert portfolio symbol into Yahoo Finance symbol."""

    base = symbol.removesuffix("-RR")

    return f"{base}.NS"


def run(symbol: str) -> None:

    print()
    print("=" * 90)
    print(f"SCORE DIAGNOSTICS: {symbol}")
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

    dataframe = calculate_score_components(
        history
    )

    if dataframe.empty:
        print("No valid score data.")
        return

    summary = summarize_scores(
        dataframe
    )

    print()
    print("SCORE DISTRIBUTION")
    print("=" * 90)

    for name, value in summary.items():

        print(
            f"{name:<30}: {value:>8.2f}"
        )

    print()
    print("AVERAGE SCORE COMPONENTS")
    print()
    print("COMPONENT SCORE FREQUENCY")
    print("=" * 90)

    for component in [
        "Momentum Score",
        "52W Score",
        "DMA Score",
    ]:

        print()
        print(component)
        print("-" * 50)

        frequencies = (
            dataframe[component]
            .value_counts()
            .sort_index()
        )

        for score, count in frequencies.items():

            percentage = (
                count / len(dataframe)
            ) * 100

            print(
                f"Score {int(score):>3}: "
                f"{int(count):>5} days "
                f"({percentage:>5.2f}%)"
            )
    print("=" * 90)

    print(
        f"{'Momentum':<30}: "
        f"{dataframe['Momentum Score'].mean():.2f}"
    )

    print(
        f"{'52 Week':<30}: "
        f"{dataframe['52W Score'].mean():.2f}"
    )

    print(
        f"{'DMA':<30}: "
        f"{dataframe['DMA Score'].mean():.2f}"
    )

    print(
        f"{'Total':<30}: "
        f"{dataframe['Total Score'].mean():.2f}"
    )

    print()
    print("SCORE FREQUENCY")
    print("=" * 90)

    score_frequency = (
        dataframe["Total Score"]
        .value_counts()
        .sort_index()
    )

    for score, count in score_frequency.items():

        print(
            f"Score {int(score):>3}: "
            f"{int(count):>5} days "
            f"({count / len(dataframe) * 100:>5.2f}%)"
        )

    print()
    print("HIGHEST SCORE DAYS")
    print("=" * 90)

    columns = [
        "Date",
        "Close",
        "Momentum Score",
        "52W Score",
        "DMA Score",
        "Total Score",
    ]

    print(
        dataframe
        .sort_values(
            "Total Score",
            ascending=False,
        )
        .head(20)[columns]
        .to_string(index=False)
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