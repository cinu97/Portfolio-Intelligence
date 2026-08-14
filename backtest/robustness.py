from __future__ import annotations

import pandas as pd

from backtest.model_comparison import (
    model_bullish_score,
    prepare_history,
    run_model,
)


ENTRY_THRESHOLDS = [45, 50, 55, 60, 65]
EXIT_THRESHOLDS = [20, 25, 30, 35, 40]


def test_parameters(
    history: pd.DataFrame,
    entry: int,
    exit_threshold: int,
    prepared: bool = False,
) -> dict:

    _, metrics = run_model(
        history=history,
        model_name="ETF-Friendly",
        score_function=model_bullish_score,
        entry_threshold=entry,
        exit_threshold=exit_threshold,
        prepared=prepared,
    )

    return metrics


def calculate_robustness_score(
    train_cagr: float,
    train_sharpe: float,
    test_cagr: float,
    test_sharpe: float,
    test_drawdown: float,
    test_exposure: float,
    test_trades: int,
) -> float:

    score = 0.0

    # Reward positive out-of-sample CAGR.
    score += max(test_cagr, 0) * 2.0

    # Reward positive out-of-sample Sharpe.
    score += max(test_sharpe, 0) * 10.0

    # Penalize large drawdowns.
    score += test_drawdown * 0.5

    # Prefer meaningful but not excessive exposure.
    if 40 <= test_exposure <= 80:
        score += 5.0

    elif 25 <= test_exposure < 40:
        score += 2.0

    # Require enough trades for statistical usefulness.
    if test_trades >= 10:
        score += 3.0

    elif test_trades >= 5:
        score += 1.0

    # Penalize severe train/test deterioration.
    if train_cagr > 0:

        deterioration = (
            train_cagr - test_cagr
        ) / train_cagr

        if deterioration > 0.75:
            score -= 10.0

        elif deterioration > 0.50:
            score -= 5.0

    # Penalize negative test performance strongly.
    if test_cagr < 0:
        score -= 20.0

    if test_sharpe < 0:
        score -= 15.0

    return score


def run_robustness(
    history: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:

    raw = history.copy().sort_index()

    total_rows = len(raw)

    if total_rows < 800:
        raise ValueError(
            "At least 800 historical sessions are required."
        )

    # Three chronological periods.
    #
    # No future information is used to select parameters.
    folds = [
        (
            "Period-1",
            0.00,
            0.40,
            0.40,
            0.60,
        ),
        (
            "Period-2",
            0.00,
            0.60,
            0.60,
            0.80,
        ),
        (
            "Period-3",
            0.00,
            0.80,
            0.80,
            1.00,
        ),
    ]

    results = []

    for (
        period,
        train_start_pct,
        train_end_pct,
        test_start_pct,
        test_end_pct,
    ) in folds:

        train_raw = raw.iloc[
            int(total_rows * train_start_pct):
            int(total_rows * train_end_pct)
        ].copy()

        test_raw = raw.iloc[
            int(total_rows * test_start_pct):
            int(total_rows * test_end_pct)
        ].copy()

        train = prepare_history(
            train_raw
        )

        if train.empty or test_raw.empty:
            continue

        candidates = []

        for entry in ENTRY_THRESHOLDS:

            for exit_threshold in EXIT_THRESHOLDS:

                if exit_threshold >= entry:
                    continue

                train_metrics = test_parameters(
                    train,
                    entry,
                    exit_threshold,
                    prepared=True,
                )

                if train_metrics.get(
                    "CAGR %"
                ) is None:
                    continue

                candidates.append(
                    {
                        "Entry": entry,
                        "Exit": exit_threshold,
                        "Train CAGR %": train_metrics.get(
                            "CAGR %",
                            0,
                        ),
                        "Train Sharpe": train_metrics.get(
                            "Sharpe Ratio",
                            0,
                        ),
                        "Train Max DD %": train_metrics.get(
                            "Max Drawdown %",
                            0,
                        ),
                        "Train Exposure %": train_metrics.get(
                            "Time Invested %",
                            0,
                        ),
                        "Train Trades": train_metrics.get(
                            "Trade Count",
                            0,
                        ),
                    }
                )

        if not candidates:
            continue

        candidates_df = pd.DataFrame(
            candidates
        )

        # Select based ONLY on training performance.
        candidates_df = candidates_df.sort_values(
            by=[
                "Train Sharpe",
                "Train CAGR %",
            ],
            ascending=False,
        )

        selected = candidates_df.iloc[0]

        entry = int(
            selected["Entry"]
        )

        exit_threshold = int(
            selected["Exit"]
        )

        # Give the test period the complete training
        # history as indicator warm-up.
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

        test_start = test_raw.index[0]
        test_end = test_raw.index[-1]

        test = combined.loc[
            (combined.index >= test_start)
            & (combined.index <= test_end)
        ].copy()

        if test.empty:
            continue

        # IMPORTANT:
        # test already contains indicators calculated from
        # the combined train + test history.
        #
        # Do NOT call prepare_history() again inside run_model().
        test_metrics = test_parameters(
            test,
            entry,
            exit_threshold,
            prepared=True,
        )

        train_cagr = float(
            selected["Train CAGR %"]
        )

        train_sharpe = float(
            selected["Train Sharpe"]
        )

        test_cagr = float(
            test_metrics.get(
                "CAGR %",
                0,
            )
        )

        test_sharpe = float(
            test_metrics.get(
                "Sharpe Ratio",
                0,
            )
        )

        test_drawdown = float(
            test_metrics.get(
                "Max Drawdown %",
                0,
            )
        )

        test_exposure = float(
            test_metrics.get(
                "Time Invested %",
                0,
            )
        )

        test_trades = int(
            test_metrics.get(
                "Trade Count",
                0,
            )
        )

        robustness_score = calculate_robustness_score(
            train_cagr=train_cagr,
            train_sharpe=train_sharpe,
            test_cagr=test_cagr,
            test_sharpe=test_sharpe,
            test_drawdown=test_drawdown,
            test_exposure=test_exposure,
            test_trades=test_trades,
        )

        results.append(
            {
                "Period": period,
                "Train Start": train.index[0],
                "Train End": train.index[-1],
                "Test Start": test.index[0],
                "Test End": test.index[-1],
                "Entry": entry,
                "Exit": exit_threshold,
                "Train CAGR %": train_cagr,
                "Train Sharpe": train_sharpe,
                "Test CAGR %": test_cagr,
                "Test Return %": test_metrics.get(
                    "Total Return %",
                    0,
                ),
                "Test Max DD %": test_drawdown,
                "Test Sharpe": test_sharpe,
                "Test Exposure %": test_exposure,
                "Test Trades": test_trades,
                "Robustness Score": robustness_score,
            }
        )

    results_df = pd.DataFrame(
        results
    )

    if results_df.empty:
        return (
            results_df,
            pd.DataFrame(),
        )

    results_df = results_df.sort_values(
        "Period"
    ).reset_index(
        drop=True
    )

    summary = pd.DataFrame(
        [
            {
                "Periods Tested": len(
                    results_df
                ),
                "Average Test CAGR %": results_df[
                    "Test CAGR %"
                ].mean(),
                "Average Test Sharpe": results_df[
                    "Test Sharpe"
                ].mean(),
                "Average Test Max DD %": results_df[
                    "Test Max DD %"
                ].mean(),
                "Average Test Exposure %": results_df[
                    "Test Exposure %"
                ].mean(),
                "Positive Test Periods": int(
                    (
                        results_df[
                            "Test CAGR %"
                        ] > 0
                    ).sum()
                ),
                "Negative Test Periods": int(
                    (
                        results_df[
                            "Test CAGR %"
                        ] < 0
                    ).sum()
                ),
                "Average Robustness Score": results_df[
                    "Robustness Score"
                ].mean(),
            }
        ]
    )

    return (
        results_df,
        summary,
    )