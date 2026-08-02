"""Ranking helpers for assets or portfolio candidates."""

from typing import Iterable


def rank_assets(items: Iterable[tuple[str, float]]) -> list[tuple[str, float]]:
    """Return assets sorted by descending score."""
    return sorted(items, key=lambda item: item[1], reverse=True)
