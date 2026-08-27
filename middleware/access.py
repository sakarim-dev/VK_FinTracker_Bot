from vkbottle.bot import Message
from config import ALLOWED_USERS
from logger import logger, log_user_action


async def check_access(message: Message):
    user_id = message.from_id

    if user_id not in ALLOWED_USERS:
        logger.warning(f"🚫 Доступ запрещён для {user_id}")
        await message.answer("Доступ запрещен.")
        return False

    logger.debug(f"✅ Доступ разрешён для {user_id}")
    return True
