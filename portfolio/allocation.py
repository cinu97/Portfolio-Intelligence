"""Portfolio allocation helpers."""

from typing import Iterable


def calculate_allocations(values: Iterable[float]) -> list[float]:
    """Return proportional allocations based on provided values."""
    values = list(values)
    total = sum(values)
    if total == 0:
        return [0.0 for _ in values]
    return [value / total for value in values]
