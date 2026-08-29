"""Стартовый обработчик и главное меню."""
from vkbottle.bot import Message, Bot
from config import ALLOWED_USERS, USER_NAMES
from keyboards import keyboard_main
from state import ctx_storage


def register_start_handlers(bot: Bot):
    @bot.on.private_message(text=["/start", "Начать", "Привет", "start"])
    async def start_handler(message: Message):
        user_id = message.from_id
        if ALLOWED_USERS and user_id not in ALLOWED_USERS:
            await message.answer("Доступ запрещен")
            return

        ctx_storage.delete(user_id)
        name = USER_NAMES.get(user_id, f"User_{user_id}")
        await message.answer(
            f"Привет, {name}! Я финансовый помощник.\n\n"
            "Доступно:\n"
            "- добавление доходов и расходов\n"
            "- удаление последней записи за последний час\n\n"
            "Выберите действие:",
            keyboard=keyboard_main.get_json(),
        )
