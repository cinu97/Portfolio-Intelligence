# Roadmap

## Current baseline

- V2 `PortfolioContext` and rule-based recommendations are active.
- The rule engine uses independent, registered plugins.
- SQLite, Google Sheets, and console reporting are operational.
- Unit tests cover rule registration, weighting, and default scoring compatibility.

## Near-term priorities

1. Add tests for CSV schema mapping, context building, SQLite persistence, and Google Sheets serialization.
2. Establish explicit historical-snapshot behavior for the database and the Market History worksheet.
3. Validate the market-history lookback used for 52-week range and moving-average labels.
4. Make policy configuration single-sourced and document any retired configuration keys.

## Future architecture work

- Move domain models such as `Holding` into a neutral domain/models module.
- Separate provider retrieval from market-data transformation.
- Add a formal migration strategy before any SQLite schema evolution.
- Consider batched market retrieval and SQLite writes if the portfolio size grows.
- Add structured application configuration through environment variables where deployment needs require it.

## Guardrails

Future work should preserve the established `PortfolioContext` boundary, add investment logic as registered rules, and include regression tests for score/action compatibility before changing policy.
