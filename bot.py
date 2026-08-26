#!/usr/bin/env python3
from vkbottle.bot import Bot
from vkbottle.tools import CtxStorage
from config import VK_TOKEN
from middleware.access import check_access
from handlers import (
    register_start_handlers,
    register_income_handlers,
    register_expense_handlers,
    register_stats_handlers,
    register_delete_handlers,
    register_reports_handlers,
)

# Создаём бота
bot = Bot(token=VK_TOKEN)
ctx_storage = CtxStorage()


# Регистрируем middleware для проверки доступа
@bot.on.private_message()
async def access_middleware(message):
    return await check_access(message)


# Регистрируем все обработчики
register_start_handlers(bot)
register_income_handlers(bot)
register_expense_handlers(bot)
register_stats_handlers(bot)
register_delete_handlers(bot)
register_reports_handlers(bot)


# Общий обработчик для всего остального
@bot.on.private_message()
async def default_handler(message):
    user_id = message.from_id
    state = ctx_storage.get(user_id)
    if state:
        return  # Если в диалоге — не мешаем
    from keyboards import keyboard_main
    await message.answer(
        "Я вас не понимаю. Используйте кнопки меню.",
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
