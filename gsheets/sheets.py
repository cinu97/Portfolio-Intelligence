"""
Google Sheets Service.
"""

from __future__ import annotations

import logging
from typing import Any

import pandas as pd

from gsheets.auth import get_google_client
from config.constants import Worksheets
from config.settings import settings

LOGGER = logging.getLogger(__name__)


def dataframe_values(dataframe: pd.DataFrame) -> list[list[Any]]:
    """Return worksheet-safe values, representing missing data as blank cells."""
    sanitized = dataframe.astype(object).where(pd.notna(dataframe), None)
    return [dataframe.columns.tolist(), *sanitized.values.tolist()]


class GoogleSheetsService:
    """Write existing report DataFrames to the configured Google spreadsheet."""

    def __init__(self) -> None:

        self.client = get_google_client()

        self.spreadsheet = self.client.open_by_key(
            settings.GOOGLE_SHEET_ID
        )

    def worksheet(self, name: str) -> Any:
        """Return an existing worksheet or create it using existing dimensions."""

        try:
            return self.spreadsheet.worksheet(name)

        except Exception:

            LOGGER.info(
                "Creating worksheet %s",
                name,
            )

            return self.spreadsheet.add_worksheet(
                title=name,
                rows=1000,
                cols=30,
            )

    def clear(self, name: str) -> None:
        """Clear an existing or newly created worksheet."""

        self.worksheet(name).clear()

    def write_dataframe(
        self,
        name: str,
        dataframe: pd.DataFrame,
    ) -> None:
        """Replace a worksheet's values and apply the existing formatting."""

        worksheet = self.worksheet(name)

        worksheet.clear()

        values = dataframe_values(dataframe)

        worksheet.update(
            values=values,
            range_name="A1",
        )

        self.format_sheet(worksheet)

    def format_sheet(
        self,
        worksheet: Any,
    ) -> None:
        """Apply the existing header and frozen-row formatting."""

        worksheet.format(
            "A1:Z1",
            {
                "textFormat": {
                    "bold": True,
                    "foregroundColor": {
                        "red": 1,
                        "green": 1,
                        "blue": 1,
                    },
                },
                "backgroundColor": {
                    "red": 0.10,
                    "green": 0.25,
                    "blue": 0.60,
                },
                "horizontalAlignment": "CENTER",
            },
        )

        worksheet.freeze(rows=1)

        try:
            worksheet.columns_auto_resize(
                0,
                25,
            )

        except Exception:

            pass

    def dashboard(
        self,
        dataframe: pd.DataFrame,
    ) -> None:

        self.write_dataframe(
            Worksheets.DASHBOARD,
            dataframe,
        )
        
    def opportunities(
        self,
        dataframe: pd.DataFrame,
    ) -> None:

        self.write_dataframe(
            "Top Opportunities",
            dataframe,
        )

    def history(
        self,
        dataframe: pd.DataFrame,
    ) -> None:

        self.write_dataframe(
            "Market History",
            dataframe,
        )
        
    def portfolio(
        self,
        dataframe: pd.DataFrame,
    ) -> None:

        self.write_dataframe(
            "Portfolio",
            dataframe,
        )

    def decision_trace(
        self,
        dataframe: pd.DataFrame,
    ) -> None:
        """Write the per-rule recommendation decision trace."""
        self.write_dataframe(
            "Decision Trace",
            dataframe,
        )
