from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Decision(str, Enum):
    BUY = "BUY"
    ACCUMULATE = "ACCUMULATE"
    WATCH = "WATCH"
    HOLD = "HOLD"
    WAIT = "WAIT"
    PROFIT_BOOK = "PROFIT BOOK"
    REDUCE = "REDUCE"
    SELL = "SELL"


@dataclass(slots=True)
class DecisionResult:
    decision: Decision
    conviction: int
    reasons: list[str]


@dataclass(slots=True)
class PositionSizingResult:
    target_amount: int
    executable_quantity: int
    executable_amount: int
    remaining_budget: int
    reason: str