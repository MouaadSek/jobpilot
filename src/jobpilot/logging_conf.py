"""Central logging setup. Library code logs here; it never uses print()."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler

from jobpilot.config import get_settings

_CONFIGURED = False


def setup_logging(level: int = logging.INFO) -> None:
    """Idempotent: attaches a rotating file handler + console handler once."""
    global _CONFIGURED
    if _CONFIGURED:
        return

    settings = get_settings()
    settings.log_dir.mkdir(parents=True, exist_ok=True)

    fmt = logging.Formatter(
        "%(asctime)s %(levelname)-7s %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )

    file_handler = RotatingFileHandler(
        settings.log_dir / "jobpilot.log", maxBytes=2_000_000, backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(fmt)

    console = logging.StreamHandler()
    console.setFormatter(fmt)

    root = logging.getLogger("jobpilot")
    root.setLevel(level)
    root.addHandler(file_handler)
    root.addHandler(console)
    root.propagate = False

    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    setup_logging()
    return logging.getLogger(f"jobpilot.{name}")
