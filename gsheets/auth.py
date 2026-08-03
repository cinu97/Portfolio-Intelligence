"""
Google Authentication
"""

from __future__ import annotations

import gspread
from google.oauth2.service_account import Credentials

from config.settings import settings


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def get_google_client() -> gspread.Client:

    credentials = Credentials.from_service_account_file(
        settings.GOOGLE_CREDENTIALS,
        scopes=SCOPES,
    )

    return gspread.authorize(credentials)