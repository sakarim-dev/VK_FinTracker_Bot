from vkbottle.bot import Message, Bot
from vkbottle import EMPTY_KEYBOARD
from vkbottle.tools import CtxStorage
from sheets import get_categories_by_type
from keyboards import get_category_keyboard, get_cancel_keyboard, keyboard_main

ctx_storage = CtxStorage()


def register_income_handlers(bot: Bot):
    @bot.on.private_message(text=["Добавить доход"])
    async def income_handler(message: Message):
        user_id = message.from_id
        categories = get_categories_by_type('Доход')

        if not categories:
            await message.answer("Нет доступных категорий.", keyboard=keyboard_main.get_json())
            return

        ctx_storage.set(user_id, {'step': 'income_category'})
        await message.answer(
            "Выберите источник дохода:",
            keyboard=get_category_keyboard(categories).get_json()
        )
        