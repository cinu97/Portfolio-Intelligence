"""
SQLite database manager for Portfolio Intelligence.
"""

from __future__ import annotations

import logging
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import TYPE_CHECKING

from config.settings import settings

if TYPE_CHECKING:
    from analytics.recommendation import Recommendation
    from market.models import MarketData

LOGGER = logging.getLogger(__name__)


class DatabaseManager:
    """Handles SQLite database initialization and connections."""

    def __init__(self) -> None:
        self.db_path: Path = settings.DATABASE_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        """Create a SQLite connection."""
        return sqlite3.connect(self.db_path)

    def initialize(self) -> None:
        """Create all required database tables."""

        with closing(self.connect()) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schema_version (
                    version TEXT PRIMARY KEY,
                    created_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS watchlist (
                    symbol TEXT PRIMARY KEY,
                    exchange TEXT,
                    instrument_type TEXT
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS market_prices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT,
                    trade_date TEXT,
                    live_price REAL,
                    previous_close REAL,
                    day_change REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS portfolio (
                    symbol TEXT PRIMARY KEY,
                    quantity REAL,
                    average_price REAL
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS recommendations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trade_date TEXT,
                    symbol TEXT,
                    buy_score INTEGER,
                    recommendation TEXT
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS market_summary (
                    trade_date TEXT PRIMARY KEY,
                    market_status TEXT,
                    top_opportunity TEXT,
                    comments TEXT
                )
            """)

            cursor.execute("""
                INSERT OR IGNORE INTO schema_version(version)
                VALUES('1.0.0')
            """)

            conn.commit()

        LOGGER.info("SQLite database initialized successfully.")
    def save_market_snapshot(
        self,
        market_data: MarketData,
        recommendation: Recommendation,
    ) -> None:
        """Store the existing daily price and recommendation snapshot rows."""

        with closing(self.connect()) as conn:

            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO market_prices
                (
                    symbol,
                    trade_date,
                    live_price,
                    previous_close,
                    day_change
                )
                VALUES
                (
                    ?,
                    DATE('now'),
                    ?,
                    ?,
                    ?
                )
                """,
                (
                    market_data.symbol,
                    market_data.live_price,
                    market_data.previous_close,
                    market_data.day_change_percent,
                ),
            )

            cursor.execute(
                """
                INSERT INTO recommendations
                (
                    trade_date,
                    symbol,
                    buy_score,
                    recommendation
                )
                VALUES
                (
                    DATE('now'),
                    ?,
                    ?,
                    ?
                )
                """,
                (
                    recommendation.symbol,
                    recommendation.buy_score,
                    recommendation.action,
                ),
            )

            conn.commit()
