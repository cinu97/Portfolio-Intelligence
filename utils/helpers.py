"""General helper utilities."""

from typing import Any


def ensure_list(value: Any) -> list[Any]:
    """Wrap a value in a list if it is not already a list or tuple."""
    if isinstance(value, (list, tuple)):
        return list(value)
    return [value]
