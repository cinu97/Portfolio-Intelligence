# Architecture and Code Quality Review

## Scope and method

This is a read-only review of the repository's Python source, configuration, sample CSV inputs, dependency manifest, and entry point. The active execution path is:

`main.py -> PortfolioEngine -> PortfolioLoader / MarketDataService -> ContextBuilder -> RecommendationEngine -> ScoringEngine -> rules`, followed by SQLite, Google Sheets, and console publishing.

No application code was modified as part of this review.

## Executive summary

The V2 recommendation path has a sensible core: typed `Holding`, `MarketData`, `PortfolioContext`, rule results, and `PortfolioResult` make the calculation pipeline understandable. The primary risks are data correctness rather than application startup: the market history request provides only 15 days while being used to calculate values labelled as 52-week and 200-DMA indicators; the scoring YAML is not applied; and output called "Market History" is not history.

The repository has no current circular imports. Its largest maintainability issue is residual V1/scaffolding code that is importable but unused, coupled with hard-coded policy values duplicated in YAML and Python.

## 1. Dead code

| Item | Evidence | Recommendation |
| --- | --- | --- |
| `market/analytics.py` (`AnalyticsService`) | No active caller imports it; the V2 path scores through `ScoringEngine`. | Remove after confirming no external consumer needs V1, or move it to an explicit `legacy/` compatibility package with a deprecation note. |
| `market/ranking.py` and `market/signals.py` | Neither helper is imported by project code. | Remove or integrate one canonical ranking/signal abstraction; do not retain both alongside recommendation actions. |
| `portfolio/allocation.py` | `calculate_allocations()` has no caller; allocation is calculated in `ContextBuilder`. | Remove or make `ContextBuilder` use it if a shared allocation utility is desired. |
| `portfolio/holdings.py` | `add_holding()` has no caller and uses an untyped dictionary that competes with `Holding`. | Remove; `Holding` should be the sole portfolio-holding model. |
| `utils/helpers.py` | `ensure_list()` has no caller. | Remove unless a near-term caller is introduced. |
| `analytics/rules/confidence.py`, `investment.py`, and `technical.py` | Empty modules, not imports or extension points. | Remove them until a concrete rule is implemented. |
| `MarketData.buy_score` and `MarketData.recommendation` | The V2 path stores these on `Recommendation`; the V1 `AnalyticsResult` also carries them. | Remove these fields from `MarketData` once V1 compatibility is retired. |
| `config.settings.CONFIG` and much of `config/scoring.yaml` | YAML is read at import time but no runtime code consumes it. | Either wire it into the engines or remove it; unused configuration falsely suggests tunability. |
| Several declared packages | `sqlalchemy`, `gspread-dataframe`, `python-dotenv`, `requests`, `streamlit`, `plotly`, and `openpyxl` have no source imports. | Split current runtime requirements from optional/future tooling, or remove unused entries. |

## 2. Duplicate logic

1. Recommendation policy is duplicated between `config/scoring.yaml` and `analytics/recommendation.py` / rule modules. Thresholds, suggested amounts, target allocation, and score weights are configured in YAML but hard-coded in code. The two already disagree: YAML gives momentum a weight of 10, while `MomentumRule.MAX_SCORE` is 30.
2. The V1 `AnalyticsService.calculate_score()` and the V2 rules both convert short-term momentum into a score/action. They can produce conflicting recommendations for the same market data.
3. Percent-change calculation exists in `MarketDataService._pct()` and `AnalyticsService.percentage()`. There should be one shared calculation with one rounding policy.
4. Symbol-column discovery is performed in both `PortfolioLoader.load_holding_records()` and `PortfolioLoader.get_symbols()`. Define the input schema once, then use it for both typed records and symbols.
5. Holdings CSV is read once to build records, again to get symbols, and a third time in `main.py` for Sheets output. Load once per run and pass a snapshot to the consumers that need it.

## 3. Circular dependencies

No circular imports are present in the current source graph.

The graph is layered enough for the active path, but `analytics.context_builder` and `analytics.portfolio_result` import `Holding` from `portfolio.loader`. This is a coupling risk: a loader is an infrastructure adapter, while `Holding` is a domain model. Moving models to a neutral `domain/` or `models/` package would prevent a future cycle when the loader needs V2 context or result types.

## 4. Incorrect module responsibilities

| Module | Responsibility concern | Suggested boundary |
| --- | --- | --- |
| `portfolio/loader.py` | Combines CSV I/O, input-schema discovery, conversion/validation, symbol aggregation, and the `Holding` domain model. | Put `Holding` in `domain/models.py`; keep CSV parsing in a repository/adapter; put schema mapping in a dedicated mapper. |
| `market/fetch_prices.py` | Fetches remote data, chooses lookback windows, computes returns, and builds domain data. | Separate provider access from market-data transformation/calculation. |
| `database/sqlite.py` | Owns connection management, schema creation/migration, and snapshot persistence. | Keep a repository focused on persistence and isolate DDL/migrations from runtime writes. |
| `main.py` | Coordinates the use case, persists each record, maps view rows, publishes four Sheets tabs, and renders a wide console table. | Retain only application composition; extract `DashboardPresenter`, `ConsoleReporter`, and `RunPersistenceService` functions/classes. |
| `config/settings.py` | Defines settings and performs YAML file I/O at module import time. | Keep settings/environment parsing separate from typed scoring-policy loading. |
| `GoogleSheetsService.history()` | Writes the current dashboard DataFrame into a worksheet named "Market History". | Either append actual dated history or rename the method/tab to reflect a snapshot export. |

## 5. Functions and methods that should be split

No individual function is excessively long, but several have multiple change reasons and should be decomposed before more rules or outputs are added.

1. `main.main()` should split into `run_analysis()`, `persist_results()`, `build_dashboard_dataframe()`, `publish_reports()`, and `print_console_report()`. This enables tests without monkey-patching global imports and permits a single output failure to be handled independently.
2. `PortfolioLoader.load_holding_records()` should delegate column selection, numeric validation, and `Holding` construction to helpers. This will make source-schema changes auditable and testable.
3. `PortfolioLoader.get_symbols()` should use a normalized holdings snapshot and a dedicated `enabled_watchlist_symbols()` helper rather than repeat CSV and column handling.
4. `MarketDataService.fetch()` should separate history retrieval, minimum-history validation, return calculation, technical calculation, and `MarketData` construction. Each step has distinct error and testing concerns.
5. `DatabaseManager.initialize()` should move each table definition into a migration or schema module. `save_market_snapshot()` should be a repository operation accepting typed inputs.

## 6. Naming improvements

| Current name | Suggested name | Reason |
| --- | --- | --- |
| `AnalyticsService.analyse` | `analyze` | Align with the rest of the repository's US-English naming. |
| `RecommendationEngine.generate(portfolio)` | `generate(context: PortfolioContext)` | The argument is a context, not a portfolio. |
| `MarketDataService.fetch` | `fetch_market_data` | Makes the returned object type clear at call sites. |
| `MarketData.live_price` | `latest_close` (unless a live quote is actually fetched) | The value is the final close from `yfinance.history()`, not necessarily an intraday/live price. |
| `t2_close`, `t5_percent`, etc. | `close_2_trading_days_ago`, `return_5_trading_days` or documented equivalents | The compact names are easy to misinterpret and do not state the return direction. |
| `day_percent` | `day_change_percent` | Matches the market model and avoids two names for one datum. |
| `FiftyTwoWeekRule` | `RangePositionRule` | It scores position within the range, not the 52-week high/low itself. |
| `GoogleSheetsService.history` | `write_market_snapshot` | Current behavior replaces a sheet with current output rather than recording history. |
| `Holding.current_value`, `pnl`, `pnl_percent` | `source_current_value`, etc., or remove from typed model | These fields come from CSV but V2 recomputes live values, creating ambiguous provenance. |

## 7. Data-flow issues

1. **High — incorrect technical lookback.** `HistoryService.get_history()` requests `period="15d"`, but `TechnicalService.calculate()` labels its maximum/minimum `week52_*` and its average `dma200`. With at most 15 observations, neither label is valid. Require approximately one year / 200 trading sessions before emitting those measures, or mark insufficient indicators explicitly.
2. **High — unused scoring policy.** `scoring.yaml` advertises configurable weights, thresholds, amounts, and allocation target, but V2 never reads it. An operator changing YAML will see no behavioral change.
3. **High — dashboard “history” is not historical.** `main.py` sends the same `dashboard_df` to `dashboard()`, `opportunities()`, and `history()`. `GoogleSheetsService.write_dataframe()` clears the target first. The “Market History” worksheet therefore contains only the latest snapshot and loses prior rows.
4. **Medium — inconsistent portfolio valuation.** `Holding.current_value` is loaded from CSV, but `PortfolioContext.current_value` and allocation are calculated from fetched market values. The Sheets portfolio tab uses the CSV version while recommendations use fetched data, so the two reports can disagree in a single run.
5. **Medium — watchlist semantics are implicit.** Watchlist symbols receive synthetic zero-quantity `Holding` records. They therefore score as 0% allocated and may be recommended for purchase. This can be correct, but it should be an explicit candidate context/type rather than a holding with fabricated fields.
6. **Medium — exchange metadata is discarded.** `watchlist.csv` contains `Exchange` and `Type`, but `HistoryService` always appends `.NS`. A non-NSE instrument cannot be fetched correctly, and the configuration data has no effect.
7. **Medium — missing/invalid source values are not validated.** CSV numeric conversion can yield `NaN`, duplicate symbols silently overwrite prior rows, and empty symbol cells may become the literal string `"NAN"`. Such data can propagate to ranking and recommendations.
8. **Medium — output has no typed view model.** `main.py` creates a dictionary/DataFrame separately from `PortfolioResult`; reasons, allocation, P&L, and timestamp are not persisted or displayed, while duplicated market fields are manually selected.

## 8. Potential bugs and resilience gaps

| Priority | Finding | Impact |
| --- | --- | --- |
| High | `TechnicalService.calculate()` returns `{}` when the `Close` series is empty, then `MarketDataService.fetch()` indexes `technical["week52_high"]`. | A malformed or partially missing market response raises `KeyError`. |
| High | The 15-day history issue causes invalid 52-week/200-DMA scores. | Recommendation decisions can be materially misleading. |
| High | `RecommendationEngine`'s `if not reasons` fallback is unreachable for normal inputs because `AverageBuyRule` and `AllocationRule` always add a reason, including zero-score cases. | "No strong signal" is never shown; reason semantics are inconsistent. |
| Medium | Rule total is 115 before clamping, while YAML totals 100 and `ScoringEngine` silently caps at 100. | Scores lose differentiation at the top and policy intent is unclear. |
| Medium | `DatabaseManager.save_market_snapshot()` inserts a new market price and recommendation on every run without a uniqueness rule. | Multiple runs on one day create duplicates; "history" cannot be queried reliably without a run timestamp or upsert policy. |
| Medium | The broad `except Exception` around all Sheets publishing makes one failed tab prevent later tabs from being attempted. | A transient Dashboard error can suppress Portfolio and Opportunities updates. |
| Medium | `GoogleSheetsService.worksheet()` treats every exception as "worksheet absent" and tries to create one. | Permission/auth/network failures are misclassified and can lead to a misleading secondary error. |
| Medium | `HistoryService` catches all errors and logs only the message, not the traceback or error category. | Provider failures are difficult to diagnose and cannot be retried selectively. |
| Low | Logger setup clears all root handlers. | It can remove handlers registered by a host process or test runner. |
| Low | `data/portfolio.db` is runtime state, while the schema version is fixed at `1.0.0` without migrations. | Future schema changes will be difficult to roll out safely. |

## 9. Performance improvements

1. Use a single holdings-data load per application run; the current active flow reads the same CSV three times.
2. Fetch history in batches or concurrently with bounded workers, caching results per run. `MarketDataService.fetch()` makes one sequential remote request per symbol.
3. Request the actual required history horizon once (for example, enough trading sessions for a 200-day average) and validate it before scoring. This is both more correct and avoids refetching after the lookback is fixed.
4. Persist all snapshots in one SQLite transaction using `executemany()` or a batch repository method, rather than opening/committing once per result.
5. Add SQLite indexes for common historical queries, at minimum `(symbol, trade_date)` for `market_prices` and `recommendations`.
6. Avoid clearing/reformatting/resizing whole Sheets tabs when only a snapshot refresh is required. Batch worksheet writes where the API permits and only resize on new/restructured sheets.
7. Replace `DataFrame.iterrows()` in `load_holding_records()` with validated vectorized preparation plus `itertuples()` if portfolio size grows. This is low priority for the current sample size.

## 10. Missing type hints

The V2 public interfaces are partially typed, but infrastructure and rule boundaries need completion.

- `main.main()` should return `None`.
- `MarketDataService.__init__()` and `fetch()` are typed only in part; use `HistoryService` for `self.history` and a `Sequence[str]` input if mutation is not required.
- `HistoryService.get_history()` should return `pd.DataFrame | None` and accept `symbol: str`.
- `TechnicalService.calculate()` should return a typed result (`TechnicalIndicators` dataclass) or at least `dict[str, float]`; an untyped dictionary hides missing-key failures.
- `DatabaseManager.save_market_snapshot()` should accept `MarketData` and `Recommendation`, and return `None`.
- Google Sheets methods should type worksheet values and return `None`; `worksheet()` should use an appropriate gspread worksheet type.
- Every rule `calculate()` method should declare its concrete result type; `MovingAverageRule.calculate()` currently does not.
- `PortfolioLoader` methods should annotate `__init__() -> None`, and a typed CSV schema/row mapping would avoid `pandas.Series` ambiguity.
- `AnalyticsService.calculate_score()` is typed, but `analyse()` lacks a return-container type for `output` during construction; more importantly, legacy API status should be declared.

## 11. Missing docstrings

The project has module-level docstrings in some adapters, but most public classes and decision logic lack contract documentation.

Priority additions:

1. `PortfolioContext`: document units, whether percentages are signed, and the source of each field.
2. `ContextBuilder.build()`: document that it uses fetched price for live value/allocation and how zero-value watchlist candidates are handled.
3. `ScoringEngine.calculate()` and every rule: document score ranges, thresholds, maximum contribution, and whether reasons include neutral conditions.
4. `RecommendationEngine.generate()`: document threshold/action/amount policy and its relationship to YAML configuration.
5. `MarketDataService.fetch()` / `HistoryService.get_history()`: document exchange mapping, data-delay semantics, expected lookback, and missing-data behavior.
6. `GoogleSheetsService.write_dataframe()`: document destructive overwrite behavior and worksheet creation behavior.
7. `DatabaseManager.save_market_snapshot()`: document the duplicate-record policy and date/time basis.
8. `PortfolioLoader.load_holding_records()` is documented, but should also state the accepted CSV column aliases and validation/duplicate handling.

## 12. Suggested folder and module organization

Do not move files solely for aesthetics. A staged target layout would clarify boundaries while preserving the V2 domain model:

```text
src/portfolio_intelligence/
  application/
    run_portfolio_analysis.py       # use-case orchestration
    presenters.py                   # dashboard and console view models
  domain/
    models.py                       # Holding, MarketData, PortfolioContext, Recommendation
    rules/
    scoring.py
    recommendation_policy.py
  infrastructure/
    market/yfinance_provider.py
    portfolio/csv_repository.py
    persistence/sqlite_repository.py
    reporting/google_sheets.py
  config/
    settings.py
    scoring.py                      # typed YAML policy loader
  entrypoints/
    cli.py
tests/
  unit/
  integration/
docs/
```

For a minimal first step, retain the existing top-level packages but: move `Holding` out of `portfolio.loader`, delete confirmed dead modules, create `tests/`, and move `main.py` presentation helpers into an application/reporting module. Only introduce a `src/` layout when packaging or multiple entry points justify it.

## Recommended remediation order

1. Correct the market-history horizon and explicit insufficient-history behavior.
2. Make scoring policy single-sourced: either load/validate `scoring.yaml` or remove it and document code constants.
3. Decide whether the V1 analytics path is supported; remove it or isolate it as legacy code.
4. Define snapshot/history semantics for SQLite and Google Sheets, then implement an append/upsert policy consistently.
5. Move domain models out of loaders and add unit tests around context building, each rule, CSV validation, and persistence uniqueness.
6. Address batching, logging/error classification, and folder reorganization after correctness and policy are settled.
