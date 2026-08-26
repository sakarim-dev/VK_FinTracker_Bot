from vkbottle.bot import Message, Bot
from vkbottle.tools import CtxStorage
from sheets import get_last_user_record, delete_record
from keyboards import keyboard_main, get_delete_keyboard

ctx_storage = CtxStorage()


def register_delete_handlers(bot: Bot):
    @bot.on.private_message(text=["Удалить последнюю запись"])
    async def delete_last_handler(message: Message):
        user_id = message.from_id
        row_num, record = get_last_user_record(user_id)

        if not row_num:
            await message.answer(
                "Нет записей для удаления (или запись старше часа).",
                keyboard=keyboard_main.get_json()
            )
            return

        record_type = record.get('Тип', 'неизвестно')
        amount = record.get('Сумма', 0)
        category = record.get('Категория', 'без категории')
        description = record.get('Описание', 'без описания')

        await message.answer(
            f"Найдена последняя запись:\n"
            f"Тип: {record_type}\n"
            f"Сумма: {amount:,.2f} руб.\n"
            f"Категория: {category}\n"
            f"Описание: {description}\n\n"
            f"Удалить?",
            keyboard=get_delete_keyboard().get_json()
        )
        ctx_storage.set(user_id, {'delete_row': row_num})

    @bot.on.private_message(text=["Да, удалить"])
    async def confirm_delete_handler(message: Message):
        user_id = message.from_id
        state = ctx_storage.get(user_id)

        if not state or 'delete_row' not in state:
            await message.answer("Нет записи для удаления.", keyboard=keyboard_main.get_json())
            return

        try:
            delete_record(state['delete_row'])
            ctx_storage.delete(user_id)
            await message.answer("Запись удалена.", keyboard=keyboard_main.get_json())
        except Exception as e:
            await message.answer(f"Ошибка: {e}", keyboard=keyboard_main.get_json())
            