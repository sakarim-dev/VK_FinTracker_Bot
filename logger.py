"""Логирование приложения."""
import logging
import sys
from datetime import datetime
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logger(name: str = "VKBot", log_file: str | None = None) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    if logger.handlers:
        return logger
    if log_file is None:
        log_file = f"bot_{datetime.now():%Y%m%d}"

    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)
    logger.addHandler(console)

    file_handler = logging.FileHandler(LOG_DIR / f"{log_file}.log", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    error_handler = logging.FileHandler(LOG_DIR / f"{log_file}_errors.log", encoding="utf-8")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)
    return logger


logger = setup_logger()


def log_user_action(user_id: int, action: str, details: str = ""):
    logger.info("User %s -> %s: %s", user_id, action, details)


def log_error(error: Exception, context: str = ""):
    logger.exception("Ошибка: %s | Контекст: %s", error, context)


def log_sheets_action(action: str, details: str = ""):
    logger.debug("Sheets: %s - %s", action, details)
