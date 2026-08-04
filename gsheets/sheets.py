"""
Google Sheets Service.
"""

from __future__ import annotations

import logging

import pandas as pd

from gsheets.auth import get_google_client
from config.constants import Worksheets
from config.settings import settings

LOGGER = logging.getLogger(__name__)


class GoogleSheetsService:

    def __init__(self):

        self.client = get_google_client()

        self.spreadsheet = self.client.open_by_key(
            settings.GOOGLE_SHEET_ID
        )

    def worksheet(self, name: str):

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

    def clear(self, name: str):

        self.worksheet(name).clear()

    def write_dataframe(
        self,
        name: str,
        dataframe: pd.DataFrame,
    ):

        worksheet = self.worksheet(name)

        worksheet.clear()

        # Replace NaN/None with empty string
        dataframe = dataframe.fillna("")
        values = [
            dataframe.columns.tolist()
        ]

        values.extend(
            dataframe.values.tolist()
        )

        worksheet.update(
            values=values,
            range_name="A1",
        )

        self.format_sheet(worksheet)

    def format_sheet(
        self,
        worksheet,
    ):

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
    ):

        self.write_dataframe(
            Worksheets.DASHBOARD,
            dataframe,
        )
        
    def opportunities(
        self,
        dataframe: pd.DataFrame,
    ):

        self.write_dataframe(
            "Top Opportunities",
            dataframe,
        )

    def history(
        self,
        dataframe: pd.DataFrame,
    ):

        self.write_dataframe(
            "Market History",
            dataframe,
        )
        
    def portfolio(
        self,
        dataframe: pd.DataFrame,
    ):

        self.write_dataframe(
            "Portfolio",
            dataframe,
        )