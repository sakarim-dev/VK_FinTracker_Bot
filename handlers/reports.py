from vkbottle.bot import Message, Bot
from config import USER_NAMES
from sheets import spreadsheet
from keyboards import keyboard_main


def register_reports_handlers(bot: Bot):
    @bot.on.private_message(text=["Общий отчёт"])
    async def general_report_handler(message: Message):
        user_id = message.from_id
        name = USER_NAMES.get(user_id, f"User_{user_id}")

        try:
            dashboard = spreadsheet.worksheet('Дашборд_Общий')
            data = dashboard.get_all_values()

            if len(data) < 2:
                await message.answer("Нет данных.", keyboard=keyboard_main.get_json())
                return

            response = f"📊 ОБЩИЙ ОТЧЁТ для {name}\n"
            response += "-" * 30 + "\n\n"

            for row in data[1:]:
                if len(row) >= 2:
                    response += f"{row[0]}: {row[1]}\n"

            await message.answer(response, keyboard=keyboard_main.get_json())

        except Exception as e:
            await message.answer(f"Ошибка: {e}", keyboard=keyboard_main.get_json())

    @bot.on.private_message(text=["Отчёт по категориям"])
    async def category_report_handler(message: Message):
        user_id = message.from_id
        name = USER_NAMES.get(user_id, f"User_{user_id}")

        try:
            dashboard = spreadsheet.worksheet('Дашборд_Категории')
            data = dashboard.get_all_values()

            if len(data) < 2:
                await message.answer("Нет данных.", keyboard=keyboard_main.get_json())
                return

            expenses = []
            incomes = []

            for row in data[1:]:
                if len(row) >= 5:
                    category = row[0]
                    amount = row[1]
                    count = row[2]
                    avg = row[3]
                    typ = row[4]

                    line = f"{category}: {amount} руб. ({count} шт., ср. {avg} руб.)"

                    if typ == 'Расход':
                        expenses.append(line)
                    elif typ == 'Доход':
                        incomes.append(line)

            response = f"📂 ОТЧЁТ ПО КАТЕГОРИЯМ для {name}\n"
            response += "-" * 30 + "\n\n"

            if expenses:
                response += "💸 РАСХОДЫ:\n"
                for line in expenses[:10]:
                    response += f"  {line}\n"
                response += "\n"

            if incomes:
                response += "💰 ДОХОДЫ:\n"
                for line in incomes[:10]:
                    response += f"  {line}\n"

            if not expenses and not incomes:
                response += "Нет данных."

            await message.answer(response, keyboard=keyboard_main.get_json())

        except Exception as e:
            await message.answer(f"Ошибка: {e}", keyboard=keyboard_main.get_json())

    @bot.on.private_message(text=["Моя статистика"])
    async def my_stats_handler(message: Message):
        user_id = message.from_id
        name = USER_NAMES.get(user_id, f"User_{user_id}")

        from sheets import get_user_stats
        stats = get_user_stats(user_id)

        response = f"📊 МОЯ СТАТИСТИКА для {name}\n"
        response += "-" * 30 + "\n\n"
        response += f"💰 Доходы:\n"
        response += f"  Всего: {stats['income']['total']:,.2f} руб.\n"
        response += f"  Операций: {stats['income']['count']}\n\n"
        response += f"💸 Расходы:\n"
        response += f"  Всего: {stats['expense']['total']:,.2f} руб.\n"
        response += f"  Операций: {stats['expense']['count']}\n\n"
        response += f"📈 Баланс: {stats['income']['total'] - stats['expense']['total']:,.2f} руб."

        await message.answer(response, keyboard=keyboard_main.get_json())
        