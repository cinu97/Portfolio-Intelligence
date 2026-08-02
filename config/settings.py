"""
Application settings.

Loads configuration from the .env file and exposes strongly typed settings.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
import os

# Project root
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env
load_dotenv(BASE_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    """Application configuration."""

    APP_NAME: str = "Portfolio Intelligence"
    APP_VERSION: str = "1.0.0"

    DATA_DIR: Path = BASE_DIR / "data"
    DATABASE_PATH: Path = BASE_DIR / "data" / "portfolio.db"

    GOOGLE_SHEET_ID: str = os.getenv("GOOGLE_SHEET_ID", "")

    GOOGLE_CREDENTIALS: Path = Path(
        os.getenv(
            "GOOGLE_CREDENTIALS",
            str(BASE_DIR / "config" / "credentials.json"),
        )
    )

    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    WATCHLIST_FILE: Path = BASE_DIR / "data" / "watchlist.csv"


settings = Settings()