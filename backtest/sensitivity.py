from __future__ import annotations

import pandas as pd

from backtest.engine import BacktestEngine
from backtest.metrics import calculate_metrics


def run_sensitivity(
    symbol: str,
    history: pd.DataFrame,
    entry_thresholds: list[int],
    exit_thresholds: list[int],
) -> pd.DataFrame:

    results = []

    for entry in entry_thresholds:

        for exit_threshold in exit_thresholds:

            # Invalid combination.
            if exit_threshold >= entry:
                continue

            try:
                engine = BacktestEngine(
                    initial_capital=100_000,
                    buy_threshold=entry,
                    exit_threshold=exit_threshold,
                )

                result = engine.run(
                    symbol=symbol,
                    history=history,
                )

                metrics = calculate_metrics(
                    result.equity_curve,
                    result.initial_capital,
                )

                results.append(
                    {
                        "Symbol": symbol,
                        "Entry Score": entry,
                        "Exit Score": exit_threshold,
                        "CAGR %": metrics.get(
                            "CAGR %",
                            0,
                        ),
                        "Total Return %": metrics.get(
                            "Total Return %",
                            0,
                        ),
                        "Max Drawdown %": metrics.get(
                            "Max Drawdown %",
                            0,
                        ),
                        "Sharpe": metrics.get(
                            "Sharpe Ratio",
                            0,
                        ),
                        "Time Invested %": metrics.get(
                            "Time Invested %",
                            0,
                        ),
                        "Trade Count": metrics.get(
                            "Trade Count",
                            0,
                        ),
                    }
                )

            except Exception as exc:

                    print()
                    print("=" * 70)
                    print("BACKTEST ERROR")
                    print("=" * 70)
                    print(f"Symbol         : {symbol}")
                    print(f"Entry threshold: {entry}")
                    print(f"Exit threshold : {exit_threshold}")
                    print(f"Error          : {type(exc).__name__}: {exc}")
                    print("=" * 70)

                    raise

    dataframe = pd.DataFrame(results)

    if dataframe.empty:
        return dataframe

    # Rank primarily by CAGR, but keep risk visible.
    dataframe = dataframe.sort_values(
        by=[
            "CAGR %",
            "Sharpe",
        ],
        ascending=False,
        na_position="last",
    )

    return dataframe.reset_index(drop=True)