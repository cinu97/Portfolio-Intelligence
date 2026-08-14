from __future__ import annotations

import math

import pandas as pd


def _performance_metrics(
    values: pd.Series,
    initial_capital: float,
    dates: pd.Series,
) -> dict[str, float]:

    values = values.astype(float)

    final_value = float(values.iloc[-1])

    total_return = (
        final_value / initial_capital
    ) - 1

    days = (
        dates.iloc[-1] - dates.iloc[0]
    ).days

    years = max(days / 365.25, 1 / 365.25)

    cagr = (
        (final_value / initial_capital)
        ** (1 / years)
    ) - 1

    daily_returns = values.pct_change().dropna()

    volatility = 0.0
    sharpe = 0.0

    if len(daily_returns) > 1:

        daily_std = daily_returns.std()

        volatility = (
            daily_std * math.sqrt(252)
        )

        if daily_std > 0:
            sharpe = (
                daily_returns.mean()
                / daily_std
            ) * math.sqrt(252)

    running_max = values.cummax()

    drawdown = (
        values / running_max
    ) - 1

    max_drawdown = float(
        drawdown.min()
    )

    return {
        "Final Value": round(final_value, 2),
        "Total Return %": round(
            total_return * 100,
            2,
        ),
        "CAGR %": round(
            cagr * 100,
            2,
        ),
        "Annualized Volatility %": round(
            volatility * 100,
            2,
        ),
        "Sharpe Ratio": round(
            sharpe,
            2,
        ),
        "Max Drawdown %": round(
            max_drawdown * 100,
            2,
        ),
    }


def calculate_metrics(
    equity_curve: pd.DataFrame,
    initial_capital: float,
) -> dict[str, float]:

    if equity_curve.empty:
        return {}

    metrics = _performance_metrics(
        equity_curve["Portfolio Value"],
        initial_capital,
        equity_curve["Date"],
    )

    invested = equity_curve["Shares"] > 0

    metrics["Time Invested %"] = round(
        invested.mean() * 100,
        2,
    )

    metrics["Time In Cash %"] = round(
        (~invested).mean() * 100,
        2,
    )

    metrics["Trade Count"] = int(
        equity_curve["Action"]
        .isin(["BUY", "SELL"])
        .sum()
    )

    return metrics


def calculate_buy_and_hold_metrics(
    history: pd.DataFrame,
    initial_capital: float,
) -> dict[str, float]:

    if history.empty:
        return {}

    prices = (
        history["Close"]
        .dropna()
        .astype(float)
    )

    initial_price = float(prices.iloc[0])

    buy_and_hold_values = (
        prices / initial_price
    ) * initial_capital

    return _performance_metrics(
        buy_and_hold_values,
        initial_capital,
        prices.index.to_series().reset_index(drop=True),
    )