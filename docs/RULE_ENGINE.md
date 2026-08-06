# Rule Engine

## Purpose

The V2 rule engine converts a `PortfolioContext` into a score and ordered explanation list. `RecommendationEngine` then maps the score to the existing action and suggested amount policy.

## Plugin contract

Every rule implements `InvestmentRule` from `analytics.rules.base`:

```python
class InvestmentRule(ABC):
    key: str

    def evaluate(self, context: PortfolioContext) -> RuleResult:
        ...
```

`RuleResult` contains an integer score contribution, maximum possible score,
existing recommendation reasons, and detailed `RuleContribution` rows. Each
trace row records a label, score contribution, maximum score, and one reason.

Existing rule classes retain their `calculate()` APIs and provide `evaluate()` adapters so the calculation logic and reason text are unchanged.

## Default registry

`create_default_registry()` creates rules in this fixed order:

1. `AverageBuyRule` (`average_buy`)
2. `AllocationRule` (`allocation`)
3. `MomentumRule` (`momentum`)
4. `FiftyTwoWeekRule` (`fifty_two_week`)
5. `MovingAverageRule` (`moving_average`)

Order matters because reasons are presented in evaluation order. The final score is capped at 100, matching the pre-plugin behavior.

## Decision trace

`ScoringEngine.evaluate()` returns a `ScoreResult` containing the capped final
score, the uncapped aggregate score, existing recommendation reasons, and the
rule breakdown. `RecommendationEngine` carries that breakdown on the resulting
`Recommendation`; `PortfolioResult` exposes it through `rule_breakdown`.

The default trace contains Average Buy, Allocation, Momentum (Day), Momentum
(5D), Momentum (7D), 52 Week, Moving Average (50 DMA), and Moving Average
(200 DMA). The existing summary reasons remain unchanged; neutral trace rows
use explanatory text only in the detailed trace.

Run the application with the optional console trace:

```powershell
.\.venv\Scripts\python.exe main.py --detailed
```

Every normal application run also writes a `Decision Trace` Google Sheets
worksheet with one row per symbol. It contains the final score, action, amount,
individual rule score columns, and combined recommendation reasons.

## Configurable weights

`config/scoring.yaml` contains `rule_weights`. A weight is a score multiplier for the matching rule key:

```yaml
rule_weights:
  average_buy: 1.0
  allocation: 1.0
  momentum: 1.0
  fifty_two_week: 1.0
  moving_average: 1.0
```

All default values are `1.0`, preserving current scores. The weighted contribution is rounded to an integer before it is added to the total.

## Adding a rule

1. Create a class implementing `InvestmentRule` with a unique `key`.
2. Keep `evaluate()` deterministic: it must use only `PortfolioContext`.
3. Add the class to `create_default_registry()` at the intended reason-order position.
4. Add a `1.0` `rule_weights` entry to preserve behavior initially.
5. Add unit tests for the rule and the expected aggregate score/reasons.

Example:

```python
class ExampleRule(InvestmentRule):
    key = "example"

    def evaluate(self, context: PortfolioContext) -> RuleResult:
        return RuleResult(score=0, reasons=[])
```

## Testing and custom registries

`ScoringEngine.calculate()` accepts optional `registry` and `rule_weights` arguments. Tests can provide a minimal registry without CSV, SQLite, Google Sheets, or market-data dependencies.

```python
registry = RuleRegistry((ExampleRule(),))
score, reasons = ScoringEngine.calculate(
    context,
    registry=registry,
    rule_weights={"example": 1.0},
)
```

`RuleRegistry.register()` rejects duplicate keys. `RuleRegistry.unregister()` cleanly removes a rule for a custom registry.
