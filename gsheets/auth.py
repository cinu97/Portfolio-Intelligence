"""
Google Authentication
"""

from __future__ import annotations

import json
import os

import gspread
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials as UserCredentials
from google.oauth2.service_account import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

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

    if not credentials_json and settings.GOOGLE_OAUTH_CLIENT.exists():
        credentials = None
        if settings.GOOGLE_OAUTH_TOKEN.exists():
            credentials = UserCredentials.from_authorized_user_file(
                settings.GOOGLE_OAUTH_TOKEN,
                SCOPES,
            )

        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        elif not credentials or not credentials.valid:
            flow = InstalledAppFlow.from_client_secrets_file(
                settings.GOOGLE_OAUTH_CLIENT,
                SCOPES,
            )
            credentials = flow.run_local_server(port=0)

        settings.GOOGLE_OAUTH_TOKEN.write_text(
            credentials.to_json(),
            encoding="utf-8",
        )
        return gspread.authorize(credentials)

    try:
        if credentials_json:
            credentials_info = json.loads(credentials_json)
            credentials = Credentials.from_service_account_info(
                credentials_info,
                scopes=SCOPES,
            )
        else:
            credentials_path = settings.GOOGLE_CREDENTIALS
            if not credentials_path.exists():
                raise FileNotFoundError(
                    "Missing Google credentials file. Set GOOGLE_CREDENTIALS_JSON or provide a valid config/credentials.json service-account JSON file."
                )
            with open(credentials_path, "r", encoding="utf-8") as handle:
                credentials_info = json.load(handle)
            required_fields = ("client_email", "private_key", "token_uri")
            if any(
                not credentials_info.get(field)
                or "YOUR_" in str(credentials_info[field])
                or "REPLACE_WITH" in str(credentials_info[field])
                for field in required_fields
            ):
                raise RuntimeError(
                    "config/credentials.json still contains placeholders. "
                    "Replace it with the original service-account JSON downloaded from Google Cloud."
                )
            credentials = Credentials.from_service_account_info(
                credentials_info,
                scopes=SCOPES,
            )
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        raise RuntimeError(
            "Google credentials are invalid or empty. Supply a valid service account JSON via GOOGLE_CREDENTIALS_JSON or config/credentials.json."
        ) from exc

    return gspread.authorize(credentials)