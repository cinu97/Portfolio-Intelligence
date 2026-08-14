from __future__ import annotations

import pandas as pd

from backtest.model_comparison import (
    model_bullish_score,
    prepare_history,
    run_model,
)


ENTRY_THRESHOLDS = [45, 50, 55, 60, 65]
EXIT_THRESHOLDS = [20, 25, 30, 35, 40]


def evaluate_period(
    history: pd.DataFrame,
    entry: int,
    exit_threshold: int,
) -> dict:

    _, metrics = run_model(
        history=history,
        model_name="ETF-Friendly",
        score_function=model_bullish_score,
        entry_threshold=entry,
        exit_threshold=exit_threshold,
    )

    return metrics


def select_parameters(
    train: pd.DataFrame,
) -> dict | None:

    candidates = []

    for entry in ENTRY_THRESHOLDS:

        for exit_threshold in EXIT_THRESHOLDS:

            if exit_threshold >= entry:
                continue

            metrics = evaluate_period(
                train,
                entry,
                exit_threshold,
            )

            cagr = metrics.get("CAGR %")
            sharpe = metrics.get("Sharpe Ratio")
            drawdown = metrics.get("Max Drawdown %")
            exposure = metrics.get("Time Invested %")
            trades = metrics.get("Trade Count")

            if any(
                value is None
                for value in [
                    cagr,
                    sharpe,
                    drawdown,
                    exposure,
                    trades,
                ]
            ):
                continue

            if (
                sharpe >= 0.80
                and exposure >= 30
                and trades >= 5
                and drawdown >= -15
            ):
                candidates.append(
                    {
                        "Entry": entry,
                        "Exit": exit_threshold,
                        "CAGR %": cagr,
                        "Sharpe": sharpe,
                        "Max Drawdown %": drawdown,
                        "Time Invested %": exposure,
                        "Trade Count": trades,
                    }
                )

    if not candidates:
        return None

    candidates_df = pd.DataFrame(candidates)

    candidates_df = candidates_df.sort_values(
        by=["CAGR %", "Sharpe"],
        ascending=False,
    )

    return candidates_df.iloc[0].to_dict()


def run_walk_forward(
    history: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:

    # IMPORTANT:
    # Do not call prepare_history() before splitting.
    #
    # We need the original history because the test period
    # requires the preceding training data as indicator warm-up.

    raw = history.copy()

    raw = raw.sort_index()

    total_rows = len(raw)

    if total_rows < 800:
        raise ValueError(
            "Walk-forward validation requires at least "
            "800 historical trading sessions."
        )

    # Expanding-window walk-forward.
    folds = [
        ("WF-1", 0.00, 0.50, 0.50, 0.75),
        ("WF-2", 0.00, 0.75, 0.75, 1.00),
    ]

    fold_results = []
    parameter_results = []

    for (
        fold_name,
        train_start_pct,
        train_end_pct,
        test_start_pct,
        test_end_pct,
    ) in folds:

        train_start_idx = int(
            total_rows * train_start_pct
        )

        train_end_idx = int(
            total_rows * train_end_pct
        )

        test_start_idx = int(
            total_rows * test_start_pct
        )

        test_end_idx = int(
            total_rows * test_end_pct
        )

        train_raw = raw.iloc[
            train_start_idx:train_end_idx
        ].copy()

        test_raw = raw.iloc[
            test_start_idx:test_end_idx
        ].copy()

        # -----------------------------------------
        # TRAIN
        # -----------------------------------------

        train = prepare_history(
            train_raw
        )

        if train.empty:
            continue

        selected = select_parameters(
            train
        )

        if selected is None:
            continue

        entry = int(
            selected["Entry"]
        )

        exit_threshold = int(
            selected["Exit"]
        )

        # -----------------------------------------
        # TEST WITH TRAINING WARM-UP
        # -----------------------------------------
        #
        # The test needs the historical context required
        # for:
        #
        # 50 DMA
        # 200 DMA
        # 252-day 52W high/low
        #
        # Therefore we combine train + test before calling
        # prepare_history().
        #
        # We DO NOT use test results during parameter selection.

        combined_raw = pd.concat(
            [
                train_raw,
                test_raw,
            ]
        )

        combined_raw = (
            combined_raw[
                ~combined_raw.index.duplicated(
                    keep="first"
                )
            ]
            .sort_index()
        )

        combined = prepare_history(
            combined_raw
        )

        if combined.empty:
            continue

        # Only retain dates belonging to the
        # previously unseen test period.
        test_start_date = test_raw.index[0]
        test_end_date = test_raw.index[-1]

        test = combined.loc[
            (combined.index >= test_start_date)
            & (combined.index <= test_end_date)
        ].copy()

        if test.empty:
            continue

        # -----------------------------------------
        # OUT-OF-SAMPLE TEST
        # -----------------------------------------

        test_metrics = evaluate_period(
            test,
            entry,
            exit_threshold,
        )

        fold_results.append(
            {
                "Fold": fold_name,

                "Train Start": train.index[0],
                "Train End": train.index[-1],

                "Test Start": test.index[0],
                "Test End": test.index[-1],

                "Entry": entry,
                "Exit": exit_threshold,

                "Train CAGR %": selected[
                    "CAGR %"
                ],

                "Train Sharpe": selected[
                    "Sharpe"
                ],

                "Test CAGR %": test_metrics.get(
                    "CAGR %",
                    0,
                ),

                "Test Return %": test_metrics.get(
                    "Total Return %",
                    0,
                ),

                "Test Max DD %": test_metrics.get(
                    "Max Drawdown %",
                    0,
                ),

                "Test Sharpe": test_metrics.get(
                    "Sharpe Ratio",
                    0,
                ),

                "Test Exposure %": test_metrics.get(
                    "Time Invested %",
                    0,
                ),

                "Test Trades": test_metrics.get(
                    "Trade Count",
                    0,
                ),
            }
        )

        parameter_results.append(
            {
                "Fold": fold_name,
                "Entry": entry,
                "Exit": exit_threshold,
            }
        )

    return (
        pd.DataFrame(fold_results),
        pd.DataFrame(parameter_results),
    )