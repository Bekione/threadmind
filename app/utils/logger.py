import logging
import os
from logging import Logger
from pythonjsonlogger import jsonlogger
from pathlib import Path

from .config import settings


_LOG_INITIALIZED = False


def setup_logging() -> None:
    global _LOG_INITIALIZED
    if _LOG_INITIALIZED:
        return

    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Console handler (JSON)
    console_handler = logging.StreamHandler()
    console_formatter = jsonlogger.JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(log_level)
    logger.addHandler(console_handler)

    # File handler
    try:
        log_dir = Path("logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_dir / "app.log")
        file_formatter = jsonlogger.JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s")
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(log_level)
        logger.addHandler(file_handler)
    except Exception:
        # If file handler fails, continue with console only.
        pass

    _LOG_INITIALIZED = True


def get_logger(name: str) -> Logger:
    setup_logging()
    return logging.getLogger(name)
