"""Клавиатуры VK.

Главное меню намеренно остаётся обычной текстовой клавиатурой.
Все остальные кнопки — callback/inline: нажатие не создаёт новое
сообщение пользователя и не засоряет диалог.
"""
from vkbottle import Keyboard, KeyboardButtonColor, Callback, Text


def _callback_keyboard(buttons, columns=2):
    keyboard = Keyboard(inline=True, one_time=True)
    for index, (label, action, color) in enumerate(buttons, 1):
        keyboard.add(Callback(label, payload={"action": action}), color=color)
        if index % columns == 0 and index != len(buttons):
            keyboard.row()
    return keyboard


# Единственная обычная текстовая клавиатура.
keyboard_main = (
    Keyboard(one_time=False, inline=False)
    .add(Text("Добавить расход"))
    .add(Text("Добавить доход"))
    .row()
    .add(Text("Удалить последнюю запись"))
)


def get_category_keyboard(categories):
    return _callback_keyboard([
        (category, f"category:{category}", KeyboardButtonColor.PRIMARY)
        for category in categories
    ])


def get_subcategory_keyboard(subcategories):
    buttons = [
        (subcategory, f"subcategory:{subcategory}", KeyboardButtonColor.PRIMARY)
        for subcategory in subcategories
    ]
    buttons += [
        ("Пропустить", "skip", KeyboardButtonColor.POSITIVE),
        ("Назад", "back", KeyboardButtonColor.SECONDARY),
    ]
    return _callback_keyboard(buttons)


def get_amount_keyboard():
    """Клавиатура для ввода суммы: пропуск суммы запрещён."""
    return _callback_keyboard([
        ("Назад", "back", KeyboardButtonColor.SECONDARY),
        ("Отмена", "cancel", KeyboardButtonColor.NEGATIVE),
    ], columns=2)


def get_description_keyboard():
    """Клавиатура для необязательного описания."""
    return _callback_keyboard([
        ("Пропустить", "skip", KeyboardButtonColor.POSITIVE),
        ("Назад", "back", KeyboardButtonColor.SECONDARY),
        ("Отмена", "cancel", KeyboardButtonColor.NEGATIVE),
    ], columns=3)


# Совместимость со старым именем.
get_text_step_keyboard = get_description_keyboard


def get_delete_keyboard():
    return _callback_keyboard([
        ("Да, удалить", "delete_confirm", KeyboardButtonColor.NEGATIVE),
        ("Нет", "delete_cancel", KeyboardButtonColor.SECONDARY),
    ])
