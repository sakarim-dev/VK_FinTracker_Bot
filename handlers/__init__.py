"""Регистрация активных обработчиков.

Stats/reports намеренно не регистрируются. Их модули можно вернуть позже
без изменения основной архитектуры.
"""
from .start import register_start_handlers
from .transaction import register_transaction_handlers
from .delete import register_delete_handlers
from .navigation import register_navigation_handlers
