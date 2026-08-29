"""Удаление последней записи пользователя."""
from vkbottle.bot import Bot, Message
from keyboards import keyboard_main, get_delete_keyboard
from state import ctx_storage
from sheets import get_last_user_record, delete_record
from utils import format_amount
from logger import log_user_action, log_error


def register_delete_handlers(bot: Bot):
    @bot.on.private_message(text="Удалить последнюю запись")
    async def delete_last_handler(message: Message):
        user_id = message.from_id
        row_num, record = get_last_user_record(user_id)
        if row_num is None:
            await message.answer(
                "Нет записи пользователя за последний час.",
                keyboard=keyboard_main.get_json(),
            )
            return

        ctx_storage.set(user_id, {"step": "delete_confirm", "delete_row": row_num})
        amount = record.get("Сумма", 0)
        try:
            amount_text = format_amount(float(amount))
        except (TypeError, ValueError):
            amount_text = str(amount)

        await message.answer(
            "Найдена последняя запись:\n"
            f"Тип: {record.get('Тип', 'неизвестно')}\n"
            f"Сумма: {amount_text}\n"
            f"Категория: {record.get('Категория', 'без категории')}\n"
            f"Описание: {record.get('Описание') or 'без описания'}\n\n"
            "Удалить?",
            keyboard=get_delete_keyboard().get_json(),
        )


async def confirm_delete(user_id: int):
    state = ctx_storage.get(user_id)
    if not state or state.get("step") != "delete_confirm":
        return False, "Нет активного удаления."
    try:
        delete_record(int(state["delete_row"]))
        ctx_storage.delete(user_id)
        log_user_action(user_id, "delete_record", f"row={state['delete_row']}")
        return True, "Запись удалена."
    except Exception as error:
        log_error(error, f"Удаление строки {state.get('delete_row')}")
        return False, "Не удалось удалить запись."


async def cancel_delete(user_id: int):
    state = ctx_storage.get(user_id)
    if state and state.get("step") == "delete_confirm":
        ctx_storage.delete(user_id)
    return "Удаление отменено."
