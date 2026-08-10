"""
Google Authentication
"""

from __future__ import annotations

import json
import os

import gspread
from google.oauth2.service_account import Credentials

from config.settings import settings


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def get_google_client() -> gspread.Client:
    """
    Create an authenticated Google Sheets client.

    Local development:
        Uses config/credentials.json.

    GitHub Actions:
        Uses the GOOGLE_CREDENTIALS_JSON environment variable.
    """

    credentials_json = os.getenv("GOOGLE_CREDENTIALS_JSON")

    if credentials_json:
        credentials_info = json.loads(credentials_json)

        credentials = Credentials.from_service_account_info(
            credentials_info,
            scopes=SCOPES,
        )
    else:
        credentials = Credentials.from_service_account_file(
            settings.GOOGLE_CREDENTIALS,
            scopes=SCOPES,
        )

    return gspread.authorize(credentials)
