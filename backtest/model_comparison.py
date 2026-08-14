from __future__ import annotations

import pandas as pd

from backtest.metrics import calculate_metrics
from backtest.engine import BacktestEngine
from analytics.rules.momentum import MomentumRule
from analytics.rules.fifty_two_week import FiftyTwoWeekRule
from analytics.rules.moving_average import MovingAverageRule


def prepare_history(history: pd.DataFrame) -> pd.DataFrame:
    df = history.copy()

    df["Close"] = df["Close"].astype(float)

    df["DMA50"] = df["Close"].rolling(50).mean()
    df["DMA200"] = df["Close"].rolling(200).mean()

    df["52W_High"] = df["Close"].rolling(252).max()
    df["52W_Low"] = df["Close"].rolling(252).min()

    df["Day_%"] = df["Close"].pct_change() * 100
    df["T5_%"] = df["Close"].pct_change(5) * 100
    df["T7_%"] = df["Close"].pct_change(7) * 100

    return df.dropna(
        subset=[
            "DMA50",
            "DMA200",
            "52W_High",
            "52W_Low",
            "Day_%",
            "T5_%",
            "T7_%",
        ]
    )


def current_score(
    row: pd.Series,
) -> int:
    price = float(row["Close"])

    range_percent = (
        (price - row["52W_Low"])
        / (row["52W_High"] - row["52W_Low"])
        * 100
        if row["52W_High"] != row["52W_Low"]
        else 0
    )

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

    return (
        momentum.score
        + fifty_two_week.score
        + moving_average.score
    )


def model_bullish_score(row: pd.Series) -> int:
    """
    ETF-friendly model.

    Trend:
        +20 price > 200 DMA
        +10 price > 50 DMA

    Momentum:
        +15 positive 5D
        +10 positive 7D
        +5 positive 1D

    Position:
        +10 above 52W low by >= 20%
        +10 below 52W high by <= 15%
    """

    price = float(row["Close"])

    score = 0

    if price > float(row["DMA200"]):
        score += 20

    if price > float(row["DMA50"]):
        score += 10

    if float(row["T5_%"]) > 0:
        score += 15

    if float(row["T7_%"]) > 0:
        score += 10

    if float(row["Day_%"]) > 0:
        score += 5

    low_distance = (
        (price - float(row["52W_Low"]))
        / float(row["52W_Low"])
        * 100
    )

    high_distance = (
        (float(row["52W_High"]) - price)
        / float(row["52W_High"])
        * 100
    )

    if low_distance >= 20:
        score += 10

    if high_distance <= 15:
        score += 10

    return score


def model_trend_score(row: pd.Series) -> int:
    """
    Trend-following model.

    +40 price > 200 DMA
    +25 price > 50 DMA
    +20 positive 7D momentum
    +15 positive 5D momentum
    """

    price = float(row["Close"])

    score = 0

    if price > float(row["DMA200"]):
        score += 40

    if price > float(row["DMA50"]):
        score += 25

    if float(row["T7_%"]) > 0:
        score += 20

    if float(row["T5_%"]) > 0:
        score += 15

    return score


def run_model(
    history: pd.DataFrame,
    model_name: str,
    score_function,
    entry_threshold: int,
    exit_threshold: int,
    prepared: bool = False,
) -> tuple[pd.DataFrame, dict]:

    # When prepared=True, the caller has already calculated
    # all indicators using the required historical warm-up.
    #
    # This is required for walk-forward testing because the
    # test period must retain the training period's indicator
    # history.

    df = (
        history.copy()
        if prepared
        else prepare_history(history)
    )

    cash = 100_000.0
    shares = 0.0
    in_position = False

    rows = []

    for date, row in df.iterrows():

        score = score_function(row)

        price = float(row["Close"])

        action = "HOLD"

        if score >= entry_threshold and not in_position:
            shares = cash / price
            cash = 0.0
            in_position = True
            action = "BUY"

        elif score <= exit_threshold and in_position:
            cash = shares * price
            shares = 0.0
            in_position = False
            action = "SELL"

        portfolio_value = cash + shares * price

        rows.append(
            {
                "Date": date,
                "Close": price,
                "Score": score,
                "Action": action,
                "Shares": shares,
                "Cash": cash,
                "Portfolio Value": portfolio_value,
            }
        )

    curve = pd.DataFrame(rows)

    metrics = calculate_metrics(
        curve,
        100_000.0,
    )

    metrics["Model"] = model_name

    return curve, metrics


def compare_models(history: pd.DataFrame) -> pd.DataFrame:

    models = [
        (
            "Current",
            current_score,
            45,
            20,
        ),
        (
            "ETF-Friendly",
            model_bullish_score,
            50,
            30,
        ),
        (
            "Trend-Following",
            model_trend_score,
            60,
            35,
        ),
    ]

    results = []

    for (
        name,
        function,
        entry,
        exit_threshold,
    ) in models:

        _, metrics = run_model(
            history,
            name,
            function,
            entry,
            exit_threshold,
        )

        results.append(
            metrics
        )

    return pd.DataFrame(results)