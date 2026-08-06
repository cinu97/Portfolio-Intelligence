# Architecture

## Overview

Portfolio Intelligence is a batch Python application that reads portfolio/watchlist CSV files, fetches market history, builds a V2 `PortfolioContext` per symbol, evaluates investment rules, and publishes the resulting recommendations to SQLite, Google Sheets, and the console.

The executable entry point is `main.py`.

## Runtime layers

```text
main.py
  ├── analytics/PortfolioEngine          V2 orchestration
  ├── database/DatabaseManager           SQLite persistence
  ├── gsheets/GoogleSheetsService        Spreadsheet publishing
  └── reporting helpers in main.py       Dashboard and console presentation

PortfolioEngine
  ├── portfolio/PortfolioLoader          Holdings and watchlist input
  ├── market/MarketDataService           History, returns, and technical values
  ├── analytics/ContextBuilder           PortfolioContext construction
  └── analytics/RecommendationEngine     Score-to-action policy
        └── analytics/ScoringEngine       Registered rule aggregation
```

## Core models

| Model | Module | Purpose |
| --- | --- | --- |
| `Holding` | `portfolio.loader` | Normalized holding data from `holdings.csv`. |
| `MarketData` | `market.models` | Latest close, historical returns, and technical indicators for one symbol. |
| `PortfolioContext` | `analytics.portfolio_context` | The complete V2 input to recommendation scoring. |
| `Recommendation` | `analytics.recommendation` | Score, action, suggested amount, reasons, and rule breakdown. |
| `PortfolioResult` | `analytics.portfolio_result` | The combined holding, market data, context, and recommendation for one symbol. |

## V2 boundaries

`PortfolioContext` is the sole input to `RecommendationEngine`. `ContextBuilder` is responsible for deriving values that depend on both a holding and live market data, such as current value, P&L, allocation percentage, and discount from average buy price.

The rule engine does not read CSV files, make network requests, publish output, or access SQLite. This keeps rules deterministic and unit-testable.

`ScoringEngine.evaluate()` produces a detailed score result. Its individual
rule contributions are retained on `Recommendation` and exposed by
`PortfolioResult`, enabling console and Google Sheets decision traces without
changing the action policy.

## Configuration and adapters

- `config/settings.py` resolves project paths, the SQLite path, credentials path, Sheet ID, and logging level.
- `config/scoring.yaml` contains rule multiplier configuration. The default multipliers are all `1.0`.
- `market/history.py` is the Yahoo Finance adapter.
- `database/sqlite.py` owns the SQLite connection and persistence operations.
- `gsheets/` owns Google service-account authentication and workbook updates.

## Extension guidance

Add investment logic through the rule registry rather than branching in `ScoringEngine`. Add a new output destination as a separate adapter called from the entry-point publishing stage. Keep provider-specific data handling inside `market/`.
