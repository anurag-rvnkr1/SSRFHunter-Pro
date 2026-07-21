"""Logging helpers for SSRFHunter Pro."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from rich.console import Console
from rich.logging import RichHandler


def build_logger(
    name: str = "ssrfhunter", verbose: bool = False, debug: bool = False
) -> logging.Logger:
    """Create a configured logger with Rich output and rotating file logging."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    logger.propagate = False

    if logger.handlers:
        return logger

    console = Console(stderr=True)
    handler = RichHandler(console=console, rich_tracebacks=True, show_path=False)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)

    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    rotating_handler = RotatingFileHandler(
        log_dir / "ssrfhunter.log", maxBytes=2_097_152, backupCount=3, encoding="utf-8"
    )
    rotating_handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    )
    logger.addHandler(rotating_handler)

    return logger
