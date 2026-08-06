# Data Flow

## End-to-end run

```text
data/holdings.csv + data/watchlist.csv
                │
                ▼
        PortfolioLoader
                │ symbols + Holding records
                ▼
        MarketDataService
                │ MarketData per available symbol
                ▼
         PortfolioEngine
                │ total live portfolio value
                ▼
         ContextBuilder
                │ PortfolioContext per symbol
                ▼
    RecommendationEngine / ScoringEngine
                │ Recommendation per symbol
                ▼
             main.py
       ┌────────┼─────────┐
       ▼        ▼         ▼
    SQLite   Sheets    Console
```

## Input files

### Holdings

`PortfolioLoader.load_holding_records()` maps accepted holdings columns into `Holding` records. The current aliases are:

| Normalized field | Accepted CSV columns |
| --- | --- |
| Symbol | `Instrument`, `Symbol`, `Trading Symbol` |
| Quantity | `Qty.`, `Quantity` |
| Average price | `Avg. cost`, `Average Price` |
| Invested value | `Invested`, `Invested Value` |
| Current value | `Cur. val`, `Current Value` |
| P&L | `P&L`, `PnL` |
| P&L percentage | `Net chg.`, `PnL %` |

The original holdings DataFrame is retained for the Portfolio worksheet.

### Watchlist

Symbols from `watchlist.csv` are combined with holdings symbols. When an `Enabled` column is present, only rows with the string value `TRUE` are included. A watchlist-only symbol receives a zero-value `Holding` when its context is built.

## Market transformation

For each symbol, `HistoryService` retrieves Yahoo Finance history and `MarketDataService`:

1. Skips unavailable data or histories with fewer than eight rows.
2. Uses the latest eight closes for day, 2-day, 3-day, 5-day, and 7-day return fields.
3. Passes the full retrieved history to `TechnicalService` for range and moving-average fields.
4. Produces one `MarketData` object.

## Context construction

`PortfolioEngine` calculates total live portfolio value from available market data. `ContextBuilder` then combines one `Holding`, one `MarketData`, and that total into a `PortfolioContext`.

Derived values include:

```text
current_value          = quantity × current_price
pnl                    = current_value − invested_value
pnl_percent            = pnl / invested_value × 100
allocation_percent     = current_value / total_portfolio_value × 100
discount_from_average  = (current_price − average_price) / average_price × 100
```

Zero denominators retain the existing `0` fallback.

## Output flow

`main.py` persists every market/recommendation pair, sorts recommendations descending by buy score, creates the dashboard DataFrame, then:

- writes Dashboard, Top Opportunities, Market History, and Portfolio worksheets;
- writes a Decision Trace worksheet with one aggregated score row per symbol;
- renders the ranked fixed-width console table.

Before Sheets writes, missing DataFrame values are converted to blank cells so they can be serialized by the Google API.

Use `python main.py --detailed` to append a per-symbol decision trace to the
standard console output. The default console table remains unchanged.
