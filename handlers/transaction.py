"""Единый сценарий добавления дохода/расхода.

До рефакторинга income.py и expense.py содержали почти одинаковую FSM-логику.
Теперь различается только тип операции, что уменьшает количество точек отказа.
"""
from vkbottle.bot import Bot, Message
from sheets import get_categories_by_type, get_subcategories, add_record
from keyboards import (
    keyboard_main,
    get_category_keyboard,
    get_subcategory_keyboard,
    get_amount_keyboard,
    get_description_keyboard,
)
from state import ctx_storage
from utils import get_date_str, get_time_str, format_amount
from logger import log_user_action, log_error


async def start_transaction(message: Message, record_type: str):
    user_id = message.from_id
    categories = get_categories_by_type(record_type)
    if not categories:
        await message.answer("Нет доступных категорий.", keyboard=keyboard_main.get_json())
        return

    ctx_storage.set(user_id, {"step": "category", "type": record_type})
    await message.answer(
        f"Выберите категорию ({record_type.lower()}):",
        keyboard=get_category_keyboard(categories).get_json(),
    )


async def process_text_input(message: Message):
    """Обрабатывает только свободный пользовательский ввод: сумма/описание."""
    state = ctx_storage.get(message.from_id)
    if not state:
        return False

    step = state.get("step")
    text = (message.text or "").strip()
    record_type = state.get("type")

    if step == "amount":
        try:
            normalized = text.replace(" ", "").replace(",", ".")
            amount = float(normalized)
        except ValueError:
            await message.answer("Введите корректную сумму, например: 500 или 500.50")
            return True
        if amount <= 0:
            await message.answer("Сумма должна быть больше 0.")
            return True

        state["amount"] = amount
        state["step"] = "description"
        ctx_storage.set(message.from_id, state)
        await message.answer(
            "Введите описание или нажмите «Пропустить»:",
            keyboard=get_description_keyboard().get_json(),
        )
        return True

    if step == "description":
        state["description"] = text
        try:
            add_record(
                date=get_date_str(),
                time=get_time_str(),
                amount=state["amount"],
                category=state["category"],
                subcategory=state.get("subcategory", ""),
                vk_id=message.from_id,
                record_type=record_type,
                description=state.get("description", ""),
            )
        except Exception as error:
            log_error(error, f"Сохранение {record_type}, user={message.from_id}")
            await message.answer("Не удалось сохранить запись. Попробуйте ещё раз.")
            return True

        amount = state["amount"]
        category = state["category"]
        subcategory = state.get("subcategory") or "не указана"
        description = state.get("description") or "не указано"
        ctx_storage.delete(message.from_id)
        log_user_action(message.from_id, "add_record", f"{record_type}: {amount}")

        await message.answer(
            f"Запись добавлена.\n"
            f"Тип: {record_type}\n"
            f"Сумма: {format_amount(amount)}\n"
            f"Категория: {category}\n"
            f"Подкатегория: {subcategory}\n"
            f"Описание: {description}",
            keyboard=keyboard_main.get_json(),
        )
        return True

    return False


def register_transaction_handlers(bot: Bot):
    @bot.on.private_message(text="Добавить доход")
    async def add_income(message: Message):
        await start_transaction(message, "Доход")

    @bot.on.private_message(text="Добавить расход")
    async def add_expense(message: Message):
        await start_transaction(message, "Расход")


async def handle_category(user_id: int, category: str):
    state = ctx_storage.get(user_id)
    if not state or state.get("step") != "category":
        return None

    record_type = state["type"]
    if category not in get_categories_by_type(record_type):
        return None

    state.update(category=category, step="subcategory")
    ctx_storage.set(user_id, state)
    return get_subcategory_keyboard(get_subcategories(category)).get_json()


async def handle_subcategory(user_id: int, subcategory: str | None):
    state = ctx_storage.get(user_id)
    if not state or state.get("step") != "subcategory":
        return None

    available = get_subcategories(state.get("category", ""))
    if subcategory is not None and subcategory not in available:
        return None

    state["subcategory"] = subcategory or ""
    state["step"] = "amount"
    ctx_storage.set(user_id, state)
    return get_amount_keyboard().get_json()


async def handle_skip(user_id: int):
    state = ctx_storage.get(user_id)
    if not state:
        return None
    step = state.get("step")
    if step == "subcategory":
        state["subcategory"] = ""
        state["step"] = "amount"
        ctx_storage.set(user_id, state)
        return "Введите сумму:", get_amount_keyboard().get_json()
    if step == "description":
        # Для callback «Пропустить» на описании создаём запись без описания.
        state["description"] = ""
        return "__SAVE__", None
    return None
