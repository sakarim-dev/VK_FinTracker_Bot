from vkbottle.bot import Message, Bot
from vkbottle.tools import CtxStorage
from sheets import get_categories_by_type, get_subcategories
from keyboards import (
    keyboard_main,
    get_category_keyboard,
    get_subcategory_keyboard,
    get_cancel_keyboard
)

ctx_storage = CtxStorage()


def register_navigation_handlers(bot: Bot):
    @bot.on.private_message(text=["Назад"])
    async def back_handler(message: Message):
        """Обработчик кнопки 'Назад' - возврат на предыдущий шаг"""
        user_id = message.from_id
        state = ctx_storage.get(user_id)

        if not state:
            await message.answer("Главное меню:", keyboard=keyboard_main.get_json())
            return

        step = state.get('step', '')
        record_type = state.get('type', '')

        # Логика возврата в зависимости от шага
        if step in ['expense_category', 'income_category']:
            # Возврат в главное меню
            ctx_storage.delete(user_id)
            await message.answer("Главное меню:", keyboard=keyboard_main.get_json())

        elif step in ['expense_subcategory', 'income_subcategory']:
            # Возврат к выбору категории
            state['step'] = 'expense_category' if record_type == 'Расход' else 'income_category'
            categories = get_categories_by_type(record_type)
            ctx_storage.set(user_id, state)
            await message.answer(
                "Выберите категорию:",
                keyboard=get_category_keyboard(categories).get_json()
            )

        elif step in ['expense_amount', 'income_amount']:
            # Возврат к выбору подкатегории
            state['step'] = 'expense_subcategory' if record_type == 'Расход' else 'income_subcategory'
            subcategories = get_subcategories(state.get('category', ''))
            ctx_storage.set(user_id, state)
            await message.answer(
                "Выберите подкатегорию или нажмите 'Пропустить':",
                keyboard=get_subcategory_keyboard(subcategories).get_json()
            )

        elif step in ['expense_description', 'income_description']:
            # Возврат к вводу суммы
            state['step'] = 'expense_amount' if record_type == 'Расход' else 'income_amount'
            ctx_storage.set(user_id, state)
            await message.answer(
                "Введите сумму:",
                keyboard=get_cancel_keyboard().get_json()
            )

        elif step == 'delete_confirm':
            # Отмена удаления
            ctx_storage.delete(user_id)
            await message.answer("Удаление отменено.", keyboard=keyboard_main.get_json())

        else:
            ctx_storage.delete(user_id)
            await message.answer("Главное меню:", keyboard=keyboard_main.get_json())

    @bot.on.private_message(text=["Пропустить"])
    async def skip_handler(message: Message):
        """Обработчик кнопки 'Пропустить' - пропуск подкатегории или описания"""
        user_id = message.from_id
        state = ctx_storage.get(user_id)

        if not state:
            await message.answer("Нет активного действия.", keyboard=keyboard_main.get_json())
            return

        step = state.get('step', '')
        record_type = state.get('type', '')

        # Пропуск подкатегории
        if step in ['expense_subcategory', 'income_subcategory']:
            state['subcategory'] = ''
            state['step'] = 'expense_amount' if record_type == 'Расход' else 'income_amount'
            ctx_storage.set(user_id, state)
            await message.answer(
                "Подкатегория пропущена.\nВведите сумму:",
                keyboard=get_cancel_keyboard().get_json()
            )

        # Пропуск описания
        elif step in ['expense_description', 'income_description']:
            state['description'] = ''
            ctx_storage.set(user_id, state)
            await message.answer(
                "Описание пропущено.\nСохраняю запись...",
                keyboard=keyboard_main.get_json()
            )
            # Здесь можно вызвать сохранение
            from sheets import add_record
            from utils import get_date_str, get_time_str

            try:
                add_record(
                    date=get_date_str(),
                    time=get_time_str(),
                    amount=state['amount'],
                    category=state['category'],
                    subcategory=state.get('subcategory', ''),
                    vk_id=user_id,
                    record_type=record_type,
                    description=''
                )
                ctx_storage.delete(user_id)
                await message.answer(
                    f"✅ Запись добавлена!\n"
                    f"Тип: {record_type}\n"
                    f"Сумма: {state['amount']:,.2f} руб.\n"
                    f"Категория: {state['category']}",
                    keyboard=keyboard_main.get_json()
                )
            except Exception as e:
                await message.answer(f"❌ Ошибка: {e}", keyboard=keyboard_main.get_json())

        else:
            await message.answer("Здесь нечего пропускать.", keyboard=keyboard_main.get_json())

    @bot.on.private_message(text=["Отмена"])
    async def cancel_handler(message: Message):
        """Обработчик кнопки 'Отмена' - полная отмена операции"""
        user_id = message.from_id
        ctx_storage.delete(user_id)
        await message.answer("Операция отменена.", keyboard=keyboard_main.get_json())

    @bot.on.private_message(text=["Назад в меню"])
    async def back_to_menu_handler(message: Message):
        """Возврат в главное меню из любого места"""
        user_id = message.from_id
        ctx_storage.delete(user_id)
        await message.answer("Главное меню:", keyboard=keyboard_main.get_json())
