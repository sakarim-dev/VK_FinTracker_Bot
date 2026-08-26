from vkbottle.bot import Message, Bot
from vkbottle.tools import CtxStorage
from sheets import get_categories_by_type, get_subcategories
from keyboards import get_category_keyboard, get_subcategory_keyboard, get_cancel_keyboard, keyboard_main

ctx_storage = CtxStorage()


def register_expense_handlers(bot: Bot):
    @bot.on.private_message(text=["Добавить расход"])
    async def expense_handler(message: Message):
        user_id = message.from_id
        categories = get_categories_by_type('Расход')

        if not categories:
            await message.answer("Нет доступных категорий.", keyboard=keyboard_main.get_json())
            return

        ctx_storage.set(user_id, {'step': 'expense_category'})
        await message.answer(
            "Выберите категорию расхода:",
            keyboard=get_category_keyboard(categories).get_json()
        )
        