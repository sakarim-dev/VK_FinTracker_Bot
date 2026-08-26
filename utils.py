from datetime import datetime, timedelta
from config import TIMEZONE_OFFSET


def get_now():
    """Возвращает текущее время в часовом поясе UTC+5"""
    return datetime.utcnow() + timedelta(hours=TIMEZONE_OFFSET)


def get_date_str():
    return get_now().strftime('%d.%m.%Y')


def get_time_str():
    return get_now().strftime('%H:%M')


def format_amount(amount):
    """Форматирует сумму"""
    return f"{amount:,.2f} руб."
