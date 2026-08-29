"""Общие утилиты."""
from datetime import datetime, timedelta
from config import TIMEZONE_OFFSET


def get_now() -> datetime:
    """Возвращает локальное время бота без зависимости от системного TZ."""
    return datetime.utcnow() + timedelta(hours=TIMEZONE_OFFSET)


def get_date_str() -> str:
    return get_now().strftime("%d.%m.%Y")


def get_time_str() -> str:
    return get_now().strftime("%H:%M")


def format_amount(amount: float) -> str:
    return f"{amount:,.2f} руб."
