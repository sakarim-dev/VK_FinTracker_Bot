from vkbottle.bot import Message
from config import ALLOWED_USERS


async def check_access(message: Message):
    """Проверяет доступ пользователя"""
    user_id = message.from_id
    if user_id not in ALLOWED_USERS:
        await message.answer("Доступ запрещен.")
        return False
    return True
