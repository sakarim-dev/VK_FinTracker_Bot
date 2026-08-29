#!/usr/bin/env python3
from vkbottle.bot import Bot
from vkbottle.tools import CtxStorage
from vkbottle.user import Message

from config import VK_TOKEN
import logging
from handlers import (
    register_start_handlers,
    register_income_handlers,
    register_expense_handlers,
    register_stats_handlers,
    register_delete_handlers,
    register_reports_handlers,
    register_navigation_handlers,
)
from keyboards import keyboard_main

logging.basicConfig(level=logging.DEBUG)

# Создаём бота
bot = Bot(token=VK_TOKEN)
ctx_storage = CtxStorage()


# Регистрируем все обработчики
register_start_handlers(bot)
register_expense_handlers(bot)
register_income_handlers(bot)
register_navigation_handlers(bot)
register_stats_handlers(bot)
register_delete_handlers(bot)
register_reports_handlers(bot)


# Общий обработчик для всего остального
@bot.on.private_message()
async def default_handler(message: Message):
    user_id = message.from_id
    state = ctx_storage.get(user_id)

    # Если есть состояние, проверяем шаги
    if state:
        step = state.get('step', '')
        # Если шаг содержит 'amount' или 'description', обрабатываем ввод
        if step.endswith('amount') or step.endswith('description'):
            # Здесь логика из обработчиков expense/income
            pass
        return

    # Иначе отправляем главное меню
    await message.answer(
        "Используйте кнопки меню:",
        keyboard=keyboard_main.get_json()
    )


# Запуск
if __name__ == "__main__":
    print("=" * 50)
    print("БОТ ЗАПУЩЕН")
    print("=" * 50)
    print(f"Google Sheets: подключено")
    print("=" * 50 + "\n")
    bot.run()
