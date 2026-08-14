from __future__ import annotations

import pandas as pd

from backtest.model_comparison import (
    prepare_history,
    model_bullish_score,
    run_model,
)


def run_etf_sensitivity(
    history: pd.DataFrame,
) -> pd.DataFrame:

    results = []

    entry_thresholds = [45, 50, 55, 60, 65]
    exit_thresholds = [20, 25, 30, 35, 40]

    for entry in entry_thresholds:

        for exit_threshold in exit_thresholds:

            if exit_threshold >= entry:
                continue

            try:
                _, metrics = run_model(
                    history=history,
                    model_name="ETF-Friendly",
                    score_function=model_bullish_score,
                    entry_threshold=entry,
                    exit_threshold=exit_threshold,
                )

                results.append(
                    {
                        "Entry": entry,
                        "Exit": exit_threshold,
                        "CAGR %": metrics.get("CAGR %"),
                        "Total Return %": metrics.get(
                            "Total Return %"
                        ),
                        "Max Drawdown %": metrics.get(
                            "Max Drawdown %"
                        ),
                        "Sharpe": metrics.get(
                            "Sharpe Ratio"
                        ),
                        "Time Invested %": metrics.get(
                            "Time Invested %"
                        ),
                        "Trade Count": metrics.get(
                            "Trade Count"
                        ),
                    }
                )

            except Exception as exc:
                print(
                    f"ERROR Entry={entry} "
                    f"Exit={exit_threshold}: "
                    f"{type(exc).__name__}: {exc}"
                )

    result = pd.DataFrame(results)

    if result.empty:
        return result

    result = result.dropna(
        subset=[
            "CAGR %",
            "Total Return %",
            "Max Drawdown %",
            "Sharpe",
            "Time Invested %",
            "Trade Count",
        ]
    )

    # Rank by CAGR first, but keep risk metrics visible.
    return result.sort_values(
        by=["CAGR %", "Sharpe"],
        ascending=False,
    ).reset_index(drop=True)