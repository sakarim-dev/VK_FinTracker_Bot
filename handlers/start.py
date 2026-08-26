from vkbottle.bot import Message, Bot
from config import USER_NAMES
from keyboards import keyboard_main


def register_start_handlers(bot: Bot):
    @bot.on.private_message(text=["/start", "Начать", "Привет", "start"])
    async def start_handler(message: Message):
        user_id = message.from_id
        name = USER_NAMES.get(user_id, f"User_{user_id}")

        await message.answer(
            f"Привет, {name}! Я финансовый помощник.\n\n"
            f"Что я умею:\n"
            f"- Добавлять доходы и расходы\n"
            f"- Показывать статистику\n"
            f"- Удалять последнюю запись (если прошло меньше часа)\n"
            f"- Показывать отчёты по категориям\n\n"
            f"Выберите действие:",
            keyboard=keyboard_main.get_json()
        )
