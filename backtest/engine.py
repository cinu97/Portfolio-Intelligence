from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from analytics.portfolio_context import PortfolioContext
from analytics.rules.momentum import MomentumRule
from analytics.rules.fifty_two_week import FiftyTwoWeekRule
from analytics.rules.moving_average import MovingAverageRule


@dataclass(slots=True)
class BacktestTrade:
    date: pd.Timestamp
    price: float
    score: int
    action: str
    shares: float
    cash_after: float
    portfolio_value: float


@dataclass(slots=True)
class BacktestResult:
    symbol: str
    initial_capital: float
    final_value: float
    total_return_percent: float
    trades: list[BacktestTrade]
    equity_curve: pd.DataFrame


class BacktestEngine:
    """
    Historical backtesting engine for the technical component
    of the Portfolio Intelligence strategy.

    Important:
    - Uses only information available up to each historical date.
    - Does not use today's portfolio allocation or average buy price.
    - Does not modify the live recommendation engine.
    """

    INITIAL_CAPITAL = 100_000.0

    # Technical score maximum:
    # Momentum       = 30
    # 52 Week        = 20
    # Moving Average = 15
    TECHNICAL_MAX_SCORE = 65

    def __init__(
        self,
        initial_capital: float = INITIAL_CAPITAL,
        buy_threshold: int = 45,
        exit_threshold: int = 35,
    ) -> None:
        self.initial_capital = initial_capital
        self.buy_threshold = buy_threshold
        self.exit_threshold = exit_threshold

    def run(
        self,
        symbol: str,
        history: pd.DataFrame,
    ) -> BacktestResult:
        """
        Run a long-only technical strategy over historical OHLC data.

        Entry:
            Technical score >= buy_threshold

        Exit:
            Technical score < buy_threshold

        Position:
            Fully invested when signal is active.

        This first version deliberately avoids portfolio allocation
        and average-buy rules because those require a simulated
        portfolio state.
        """

        if history.empty:
            raise ValueError(f"No historical data available for {symbol}")

        df = history.copy()

        if "Close" not in df.columns:
            raise ValueError(
                f"Historical data for {symbol} does not contain Close prices"
            )

        df = df.dropna(subset=["Close"]).copy()

        if len(df) < 220:
            raise ValueError(
                f"{symbol}: need at least 220 trading days, got {len(df)}"
            )

        df["Close"] = df["Close"].astype(float)

        # Calculate indicators using only data available at each date.
        df["DMA50"] = df["Close"].rolling(50).mean()
        df["DMA200"] = df["Close"].rolling(200).mean()

        # 52-week window = approximately 252 trading sessions.
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

        # Don't generate signals until all required indicators exist.
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
        )

        cash = self.initial_capital
        shares = 0.0
        in_position = False

        trades: list[BacktestTrade] = []
        equity_rows = []

        for date, row in df.iterrows():

            price = float(row["Close"])

            range_percent = 0.0

            if row["52W_High"] != row["52W_Low"]:
                range_percent = (
                    (price - row["52W_Low"])
                    / (row["52W_High"] - row["52W_Low"])
                ) * 100

            # Reuse the exact existing rule implementations.
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

            technical_score = (
                momentum.score
                + fifty_two_week.score
                + moving_average.score
            )

            action = "HOLD"

                       # Entry
            if (
                technical_score >= self.buy_threshold
                and not in_position
            ):
                shares = cash / price
                cash = 0.0
                in_position = True
                action = "BUY"

            # Exit
            elif (
                technical_score <= self.exit_threshold
                and in_position
            ):
                cash = shares * price
                shares = 0.0
                in_position = False
                action = "SELL"

            portfolio_value = (
                cash
                + shares * price
            )

            if action in {"BUY", "SELL"}:
                trades.append(
                    BacktestTrade(
                        date=date,
                        price=price,
                        score=technical_score,
                        action=action,
                        shares=shares,
                        cash_after=cash,
                        portfolio_value=portfolio_value,
                    )
                )

            equity_rows.append(
                {
                    "Date": date,
                    "Close": price,
                    "Score": technical_score,
                    "Action": action,
                    "Shares": shares,
                    "Cash": cash,
                    "Portfolio Value": portfolio_value,
                }
            )

        equity_curve = pd.DataFrame(equity_rows)

        if equity_curve.empty:
            raise ValueError(
                f"{symbol}: no valid backtest periods"
            )

        final_value = float(
            equity_curve.iloc[-1]["Portfolio Value"]
        )

        total_return_percent = (
            (final_value - self.initial_capital)
            / self.initial_capital
        ) * 100

        return BacktestResult(
            symbol=symbol,
            initial_capital=self.initial_capital,
            final_value=final_value,
            total_return_percent=total_return_percent,
            trades=trades,
            equity_curve=equity_curve,
        )