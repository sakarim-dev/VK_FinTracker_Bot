"""Совместимость со старой структурой.

Логика доходов перенесена в handlers.transaction, чтобы исключить
дублирование с расходами. Файл оставлен, чтобы старые импорты не ломались.
"""
from .transaction import start_transaction


def register_income_handlers(bot):
    # Не регистрируем второй обработчик: это делается в transaction.py.
    return None
