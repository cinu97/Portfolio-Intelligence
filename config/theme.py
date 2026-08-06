"""Starter theme configuration for the portfolio intelligence app."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ThemeConfig:
    """Simple theme settings container."""

    name: str = "dark"
    primary_color: str = "#2563eb"
    accent_color: str = "#10b981"
    background_color: str = "#0f172a"
    text_color: str = "#f8fafc"


DEFAULT_THEME = ThemeConfig()
