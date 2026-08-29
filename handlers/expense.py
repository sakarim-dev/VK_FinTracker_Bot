from vkbottle.bot import Message, Bot
from vkbottle.tools import CtxStorage
from sheets import get_categories_by_type, get_subcategories, add_record
from keyboards import get_category_keyboard, get_subcategory_keyboard, get_cancel_keyboard, keyboard_main
from utils import get_date_str, get_time_str

ctx_storage = CtxStorage()


def register_expense_handlers(bot: Bot):
    @bot.on.private_message(text=["Добавить расход"])
    async def expense_handler(message: Message):
        user_id = message.from_id
        categories = get_categories_by_type('Расход')

        if not categories:
            await message.answer("Нет доступных категорий.", keyboard=keyboard_main.get_json())
            return

        ctx_storage.set(user_id, {
            'step': 'expense_category',
            'type': 'Расход'
        })
        await message.answer(
            "Выберите категорию расхода:",
            keyboard=get_category_keyboard(categories).get_json()
        )

    @bot.on.private_message(text=["Назад"])
    async def back_handler(message: Message):
        user_id = message.from_id
        state = ctx_storage.get(user_id)

        if not state:
            await message.answer("Главное меню:", keyboard=keyboard_main.get_json())
            return

        step = state.get('step', '')

        if step == 'expense_category' or step == 'income_category':
            ctx_storage.delete(user_id)
            await message.answer("Главное меню:", keyboard=keyboard_main.get_json())

        elif step == 'expense_subcategory' or step == 'income_subcategory':
            # Возврат к выбору категории
            state['step'] = 'expense_category' if 'Расход' in state.get('type', '') else 'income_category'
            categories = get_categories_by_type(state.get('type', 'Расход'))
            ctx_storage.set(user_id, state)
            await message.answer(
                "Выберите категорию:",
                keyboard=get_category_keyboard(categories).get_json()
            )

        elif step == 'expense_amount' or step == 'income_amount':
            # Возврат к выбору подкатегории
            state['step'] = 'expense_subcategory' if 'Расход' in state.get('type', '') else 'income_subcategory'
            subcategories = get_subcategories(state.get('category', ''))
            ctx_storage.set(user_id, state)
            await message.answer(
                "Выберите подкатегорию или пропустите:",
                keyboard=get_subcategory_keyboard(subcategories).get_json()
            )

    @bot.on.private_message(text=["Отмена"])
    async def cancel_handler(message: Message):
        user_id = message.from_id
        ctx_storage.delete(user_id)
        await message.answer("Действие отменено.", keyboard=keyboard_main.get_json())

    # Обработчик выбора категории
    @bot.on.private_message()
    async def handle_expense_input(message: Message):
        user_id = message.from_id
        state = ctx_storage.get(user_id)

        if not state:
            return

        step = state.get('step', '')
        text = message.text

        # Выбор категории
        if step == 'expense_category':
            categories = get_categories_by_type('Расход')
            if text in categories:
                state['category'] = text
                state['step'] = 'expense_subcategory'
                subcategories = get_subcategories(text)
                ctx_storage.set(user_id, state)
                await message.answer(
                    f"Выбрана категория: {text}\nВыберите подкатегорию или нажмите 'Пропустить':",
                    keyboard=get_subcategory_keyboard(subcategories).get_json()
                )
            else:
                await message.answer("Выберите категорию из списка.")

        # Выбор подкатегории
        elif step == 'expense_subcategory':
            subcategories = get_subcategories(state.get('category', ''))
            if text == "Пропустить":
                state['subcategory'] = ''
                state['step'] = 'expense_amount'
                ctx_storage.set(user_id, state)
                await message.answer(
                    "Введите сумму расхода (например: 500 или 500.50):",
                    keyboard=get_cancel_keyboard().get_json()
                )
            elif text in subcategories:
                state['subcategory'] = text
                state['step'] = 'expense_amount'
                ctx_storage.set(user_id, state)
                await message.answer(
                    f"Выбрана подкатегория: {text}\nВведите сумму расхода:",
                    keyboard=get_cancel_keyboard().get_json()
                )
            else:
                await message.answer("Выберите подкатегорию из списка или нажмите 'Пропустить'.")

        # Ввод суммы
        elif step == 'expense_amount':
            try:
                amount = float(text.replace(',', '.'))
                if amount <= 0:
                    await message.answer("Сумма должна быть больше 0.")
                    return

                state['amount'] = amount
                state['step'] = 'expense_description'
                ctx_storage.set(user_id, state)
                await message.answer(
                    "Введите описание (или нажмите 'Пропустить'):",
                    keyboard=get_cancel_keyboard().get_json()
                )
            except ValueError:
                await message.answer("Пожалуйста, введите число (например: 500 или 500.50)")

        # Ввод описания
        elif step == 'expense_description':
            if text == "Пропустить":
                state['description'] = ''
            else:
                state['description'] = text

            # Сохраняем запись
            try:
                add_record(
                    date=get_date_str(),
                    time=get_time_str(),
                    amount=state['amount'],
                    category=state['category'],
                    subcategory=state.get('subcategory', ''),
                    vk_id=user_id,
                    record_type='Расход',
                    description=state.get('description', '')
                )
                ctx_storage.delete(user_id)
                await message.answer(
                    f"✅ Расход добавлен!\n"
                    f"Сумма: {state['amount']:,.2f} руб.\n"
                    f"Категория: {state['category']}\n"
                    f"Подкатегория: {state.get('subcategory', 'не указана')}\n"
                    f"Описание: {state.get('description', 'не указано')}",
                    keyboard=keyboard_main.get_json()
                )
            except Exception as e:
                await message.answer(f"❌ Ошибка: {e}", keyboard=keyboard_main.get_json())