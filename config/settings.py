from pathlib import Path
import os
import yaml


class Settings:

    def __init__(self):

        self.PROJECT_ROOT = Path(__file__).resolve().parent.parent

        self.CONFIG_DIR = self.PROJECT_ROOT / "config"

        self.DATA_DIR = self.PROJECT_ROOT / "data"

        self.DATABASE_PATH = self.DATA_DIR / "portfolio.db"

        self.GOOGLE_CREDENTIALS = (
            self.CONFIG_DIR / "credentials.json"
        )

        self.GOOGLE_OAUTH_CLIENT = (
            self.CONFIG_DIR / "oauth_client.json"
        )

        self.GOOGLE_OAUTH_TOKEN = (
            self.CONFIG_DIR / "oauth_token.json"
        )

        self.GOOGLE_SHEET_ID = os.getenv(
            "GOOGLE_SHEET_ID",
            "1WfXiXFvcL1tHin6Ar9x3dC7VUhn2DT7JA7vhAxAcOXc",
        )

        self.LOG_LEVEL = os.getenv(
            "LOG_LEVEL",
            "INFO",
        )


settings = Settings()


SCORING_FILE = settings.CONFIG_DIR / "scoring.yaml"

if SCORING_FILE.exists():

    with open(
        SCORING_FILE,
        "r",
        encoding="utf-8",
    ) as f:

        CONFIG = yaml.safe_load(f)

else:

    CONFIG = {}