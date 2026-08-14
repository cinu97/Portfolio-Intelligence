from __future__ import annotations

import pandas as pd

from analytics.rules.momentum import MomentumRule
from analytics.rules.fifty_two_week import FiftyTwoWeekRule
from analytics.rules.moving_average import MovingAverageRule


def calculate_score_components(
    history: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate historical score components for diagnostic analysis.

    This does NOT execute trades and does NOT modify the live strategy.
    """

    if history.empty:
        raise ValueError("Historical data is empty")

    df = history.copy()

    if "Close" not in df.columns:
        raise ValueError("Historical data does not contain Close")

    df["Close"] = df["Close"].astype(float)

    # Technical indicators
    df["DMA50"] = df["Close"].rolling(50).mean()
    df["DMA200"] = df["Close"].rolling(200).mean()

    df["52W_High"] = (
        df["Close"]
        .rolling(252)
        .max()
    )

    df["52W_Low"] = (
        df["Close"]
        .rolling(252)
        .min()
    )

    df["Day_%"] = (
        df["Close"]
        .pct_change()
        .mul(100)
    )

    df["T5_%"] = (
        df["Close"]
        .pct_change(5)
        .mul(100)
    )

    df["T7_%"] = (
        df["Close"]
        .pct_change(7)
        .mul(100)
    )

    # Need all indicators before scoring.
    df = df.dropna(
        subset=[
            "DMA50",
            "DMA200",
            "52W_High",
            "52W_Low",
            "Day_%",
            "T5_%",
            "T7_%",
        ]
    ).copy()

    rows = []

    for date, row in df.iterrows():

        price = float(row["Close"])

        # Position within 52-week range.
        if row["52W_High"] != row["52W_Low"]:
            range_percent = (
                (price - row["52W_Low"])
                / (
                    row["52W_High"]
                    - row["52W_Low"]
                )
            ) * 100
        else:
            range_percent = 0.0

        momentum = MomentumRule.calculate(
            float(row["Day_%"]),
            float(row["T5_%"]),
            float(row["T7_%"]),
        )

        fifty_two_week = FiftyTwoWeekRule.calculate(
            range_percent
        )

        moving_average = MovingAverageRule.calculate(
            price,
            float(row["DMA50"]),
            float(row["DMA200"]),
        )

        total_score = (
            momentum.score
            + fifty_two_week.score
            + moving_average.score
        )

        rows.append(
            {
                "Date": date,
                "Close": price,

                "Momentum Score": momentum.score,
                "52W Score": fifty_two_week.score,
                "DMA Score": moving_average.score,

                "Total Score": total_score,

                "Day %": float(row["Day_%"]),
                "T5 %": float(row["T5_%"]),
                "T7 %": float(row["T7_%"]),

                "DMA50": float(row["DMA50"]),
                "DMA200": float(row["DMA200"]),

                "52W Low": float(row["52W_Low"]),
                "52W High": float(row["52W_High"]),
                "% From 52W Low": (
                    (price - row["52W_Low"])
                    / row["52W_Low"]
                ) * 100,

                "% From 52W High": (
                    (price - row["52W_High"])
                    / row["52W_High"]
                ) * 100,
            }
        )

    return pd.DataFrame(rows)


def summarize_scores(
    dataframe: pd.DataFrame,
) -> dict[str, float]:

    if dataframe.empty:
        return {}

    total_scores = dataframe["Total Score"]

    return {
        "Average Score": round(
            total_scores.mean(),
            2,
        ),
        "Median Score": round(
            total_scores.median(),
            2,
        ),
        "% Days Score >= 20": round(
            (total_scores >= 20).mean() * 100,
            2,
        ),
        "% Days Score >= 30": round(
            (total_scores >= 30).mean() * 100,
            2,
        ),
        "% Days Score >= 40": round(
            (total_scores >= 40).mean() * 100,
            2,
        ),
        "% Days Score >= 45": round(
            (total_scores >= 45).mean() * 100,
            2,
        ),
        "% Days Score >= 50": round(
            (total_scores >= 50).mean() * 100,
            2,
        ),
        "% Days Score >= 60": round(
            (total_scores >= 60).mean() * 100,
            2,
        ),
    }