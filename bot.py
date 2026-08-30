#!/usr/bin/env python3
"""Точка входа VK Finance Tracker.

Активные функции: старт, доходы, расходы, удаление.
Статистика и отчёты отключены на уровне регистрации обработчиков,
но их будущая интеграция не требует изменения ядра.
"""
import json

from vkbottle import Bot, GroupEventType
from vkbottle.bot import MessageEvent
from vkbottle.bot import Message

from config import VK_TOKEN, ALLOWED_USERS, USER_NAMES
from handlers import (
    register_start_handlers,
    register_transaction_handlers,
    register_delete_handlers,
    register_navigation_handlers,
)
from handlers.transaction import handle_category, handle_subcategory, handle_skip, process_text_input
from categories import get_categories_by_type, get_subcategories  # noqa: F401 (используется в callback_handler)
from handlers.delete import confirm_delete, cancel_delete
from keyboards import (
    keyboard_main,
    get_category_keyboard,
    get_subcategory_keyboard,
    get_amount_keyboard,
)
from state import ctx_storage
from logger import logger, log_error

bot = Bot(token=VK_TOKEN)

register_start_handlers(bot)
register_transaction_handlers(bot)
register_delete_handlers(bot)
register_navigation_handlers(bot)


async def _allowed(user_id: int) -> bool:
    return not ALLOWED_USERS or user_id in ALLOWED_USERS


@bot.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=MessageEvent)
async def callback_handler(event: MessageEvent):
    """Единая точка обработки всех callback-кнопок."""
    user_id = event.user_id
    name = USER_NAMES.get(user_id, f"User_{user_id}")
    if not await _allowed(user_id):
        await event.show_snackbar("Доступ запрещен")
        return

    payload = event.payload
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except json.JSONDecodeError:
            payload = {"action": payload}
    payload = payload or {}
    action = payload.get("action", "")

    try:
        if action.startswith("subcategory:"):
            subcategory = action.split(":", 1)[1]
            keyboard = await handle_subcategory(user_id, subcategory)
            if keyboard is None:
                await event.show_snackbar("Подкатегория недоступна")
                return
            await event.edit_message("Подкатегория выбрана. Введите сумму:", keyboard=keyboard)
            return

        if action == "skip":
            result = await handle_skip(user_id)
            if result is None:
                await event.show_snackbar("Сейчас пропуск недоступен")
                return
            message, keyboard = result
            if message == "__SAVE__":
                # Callback не является Message, поэтому сохраняем запись напрямую.
                from sheets import add_record
                from utils import get_date_str, get_time_str, format_amount
                state = ctx_storage.get(user_id)
                try:
                    add_record(
                        date=get_date_str(), time=get_time_str(), amount=state["amount"],
                        category=state["category"], subcategory=state.get("subcategory", ""),
                        vk_id=name, record_type=state["type"], description="",
                    )
                except Exception as save_error:
                    log_error(save_error, f"skip/__SAVE__, user={user_id}")
                    await event.show_snackbar("Не удалось сохранить запись. Попробуйте ещё раз.")
                    return
                amount = state["amount"]
                record_type = state["type"]
                category = state["category"]
                ctx_storage.delete(user_id)
                await event.edit_message(
                    f"Запись добавлена.\nТип: {record_type}\nСумма: {format_amount(amount)}\nКатегория: {category}",
                    keyboard=keyboard_main.get_json(),
                )
            else:
                await event.edit_message(message, keyboard=keyboard)
            return

        if action == "back":
            state = ctx_storage.get(user_id)
            if not state:
                await event.edit_message("Главное меню:", keyboard=keyboard_main.get_json())
                return
            step = state.get("step")
            record_type = state.get("type")
            if step == "subcategory":
                state["step"] = "category"
                ctx_storage.set(user_id, state)
                await event.edit_message("Выберите категорию:", keyboard=get_category_keyboard(get_categories_by_type(record_type)).get_json())
            elif step == "amount":
                # Если подкатегория была выбрана автоматически, возвращаемся
                # сразу к выбору категории, не показывая лишний экран.
                if state.get("subcategory_auto"):
                    state["step"] = "category"
                    state.pop("subcategory", None)
                    state.pop("subcategory_auto", None)
                    ctx_storage.set(user_id, state)
                    await event.edit_message(
                        "Выберите категорию:",
                        keyboard=get_category_keyboard(get_categories_by_type(record_type)).get_json(),
                    )
                else:
                    state["step"] = "subcategory"
                    ctx_storage.set(user_id, state)
                    await event.edit_message(
                        "Выберите подкатегорию:",
                        keyboard=get_subcategory_keyboard(get_subcategories(state["category"])).get_json(),
                    )
            elif step == "description":
                state["step"] = "amount"
                ctx_storage.set(user_id, state)
                await event.edit_message("Введите сумму:", keyboard=get_amount_keyboard().get_json())
            else:
                ctx_storage.delete(user_id)
                await event.edit_message("Главное меню:", keyboard=keyboard_main.get_json())
            return

        if action == "cancel":
            ctx_storage.delete(user_id)
            await event.edit_message("Операция отменена.", keyboard=keyboard_main.get_json())
            return

        if action == "delete_confirm":
            ok, text = await confirm_delete(user_id)
            await event.edit_message(text, keyboard=keyboard_main.get_json())
            return

        if action == "delete_cancel":
            text = await cancel_delete(user_id)
            await event.edit_message(text, keyboard=keyboard_main.get_json())
            return

        await event.show_snackbar("Неизвестное действие")
    except Exception as error:
        log_error(error, f"callback action={action}, user={user_id}")
        await event.show_snackbar("Произошла ошибка")


@bot.on.private_message()
async def fallback_handler(message: Message):
    """Единый catch-all: обрабатывает FSM (категория/сумма/описание) и показывает меню."""
    if not await _allowed(message.from_id):
        return
    if await process_text_input(message):
        return
    await message.answer("Используйте кнопки меню:", keyboard=keyboard_main.get_json())


if __name__ == "__main__":
    logger.info("VK Finance Tracker запущен")
    bot.run()
