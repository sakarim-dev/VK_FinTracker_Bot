import logging
import sys
from datetime import datetime
from pathlib import Path

# Создаём папку для логов
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Настройка формата логов
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logger(name: str = "VKBot", log_file: str = None) -> logging.Logger:
    """
    Настраивает логгер с выводом в консоль и файл

    Args:
        name: Имя логгера
        log_file: Имя файла лога (без расширения)

    Returns:
        logging.Logger: Настроенный логгер
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Очищаем существующие обработчики
    logger.handlers.clear()

    # 1. Консольный обработчик (цветной)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # 2. Файловый обработчик (все уровни)
    if log_file is None:
        log_file = f"bot_{datetime.now().strftime('%Y%m%d')}"

    file_path = LOG_DIR / f"{log_file}.log"
    file_handler = logging.FileHandler(file_path, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # 3. Файл для ошибок (только ERROR и выше)
    error_path = LOG_DIR / f"{log_file}_errors.log"
    error_handler = logging.FileHandler(error_path, encoding="utf-8")
    error_handler.setLevel(logging.ERROR)
    error_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    error_handler.setFormatter(error_formatter)
    logger.addHandler(error_handler)

    return logger


# Создаём основной логгер
logger = setup_logger("VKBot")


def log_user_action(user_id: int, action: str, details: str = ""):
    """Логирует действие пользователя"""
    logger.info(f"👤 User {user_id} → {action}: {details}")


def log_error(error: Exception, context: str = ""):
    """Логирует ошибку с контекстом"""
    logger.error(f"❌ Ошибка: {error}\nКонтекст: {context}")


def log_command(user_id: int, command: str):
    """Логирует команду от пользователя"""
    logger.info(f"📩 Команда от {user_id}: {command}")


def log_sheets_action(action: str, details: str = ""):
    """Логирует действие с Google Sheets"""
    logger.debug(f"📊 Sheets: {action} - {details}")