# Contributing

## Setup

Use Python and the local virtual environment:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Required local inputs:

- `data/holdings.csv`
- optionally `data/watchlist.csv`
- `config/credentials.json` for Google Sheets publishing

Do not commit credentials, `.env` files, SQLite databases, logs, or virtual environments. They are ignored by `.gitignore`.

## Run the application

```powershell
.\.venv\Scripts\python.exe main.py
```

This command fetches market data and writes SQLite and Google Sheets outputs when credentials are configured.

## Test and validate changes

Run unit tests:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Compile the source before handoff:

```powershell
.\.venv\Scripts\python.exe -m compileall -q analytics config database gsheets market portfolio utils tests main.py
```

For changes to recommendations, add regression tests that assert score, action, amount, and reason order for representative `PortfolioContext` values.

## Contribution guidelines

1. Keep market retrieval, persistence, reporting, and scoring concerns separate.
2. Use `PortfolioContext` as the input to all new recommendation rules.
3. Implement new rules through `InvestmentRule` and register them deliberately.
4. Preserve rule keys and ordering unless the policy change is explicit and tested.
5. Add type hints and docstrings to public classes and methods.
6. Avoid broad exception handling unless it is an output/integration boundary with logging.
7. Do not change the SQLite schema without a migration and data-compatibility plan.
8. Keep pull requests focused; do not combine feature, cleanup, and policy changes unnecessarily.

## Pull request checklist

- [ ] Relevant tests added or updated.
- [ ] Unit tests and compilation pass.
- [ ] No secrets or runtime artifacts added.
- [ ] Recommendation behavior is unchanged, or the policy change is documented and approved.
- [ ] Documentation is updated when architecture, data flow, configuration, or contributor workflow changes.
