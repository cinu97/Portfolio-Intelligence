"""
Central logging configuration.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from config.settings import settings


LOG_FORMAT = (
    "%(asctime)s | "
    "%(levelname)-8s | "
    "%(name)s | "
    "%(message)s"
)


def setup_logger() -> None:
    """
    Configure application logging.
    """

    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    root = logging.getLogger()

    if root.handlers:
        root.handlers.clear()

    root.setLevel(settings.LOG_LEVEL)

    formatter = logging.Formatter(LOG_FORMAT)

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)

    file_handler = logging.FileHandler(
        log_dir / "portfolio.log",
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    root.addHandler(console)
    root.addHandler(file_handler)