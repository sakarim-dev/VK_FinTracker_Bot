"""Навигация сценария через callback-кнопки."""
from vkbottle.bot import Bot, Message
from keyboards import keyboard_main, get_category_keyboard, get_subcategory_keyboard, get_text_step_keyboard
from categories import get_categories_by_type, get_subcategories
from state import ctx_storage


def register_navigation_handlers(bot: Bot):
    # Свободный текст «Назад/Отмена» больше не нужен: все такие действия callback.
    @bot.on.private_message(text="Назад в меню")
    async def legacy_menu(message: Message):
        ctx_storage.delete(message.from_id)
        await message.answer("Главное меню:", keyboard=keyboard_main.get_json())
