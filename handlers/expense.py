"""Совместимость со старой структурой.

Логика расходов перенесена в handlers.transaction.
"""
from .transaction import start_transaction


def register_expense_handlers(bot):
    return None
