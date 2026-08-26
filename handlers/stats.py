from vkbottle.bot import Message, Bot
from config import USER_NAMES
from sheets import get_user_stats
from keyboards import keyboard_main


def register_stats_handlers(bot: Bot):
    @bot.on.private_message(text=["Статистика"])
    async def stats_handler(message: Message):
        user_id = message.from_id
        name = USER_NAMES.get(user_id, f"User_{user_id}")

        stats = get_user_stats(user_id)

        response = f"📊 Статистика для {name}\n"
        response += "-" * 30 + "\n\n"
        response += f"📅 За сегодня:\n"
        response += f"  Трат: {stats['today']['count']}\n"
        response += f"  Сумма: {stats['today']['total']:,.2f} руб.\n\n"
        response += f"📆 За месяц:\n"
        response += f"  Трат: {stats['month']['count']}\n"
        response += f"  Сумма: {stats['month']['total']:,.2f} руб.\n\n"
        response += f"💰 Доходы: {stats['income']['total']:,.2f} руб.\n"
        response += f"💸 Расходы: {stats['expense']['total']:,.2f} руб.\n"
        response += f"📈 Баланс: {stats['income']['total'] - stats['expense']['total']:,.2f} руб.\n\n"

        if stats['by_category']:
            response += "📂 По категориям:\n"
            sorted_cats = sorted(stats['by_category'].items(), key=lambda x: x[1], reverse=True)
            for cat, amount in sorted_cats[:5]:
                response += f"  {cat}: {amount:,.2f} руб.\n"

        await message.answer(response, keyboard=keyboard_main.get_json())
