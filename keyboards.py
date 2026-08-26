from vkbottle import Keyboard, KeyboardButtonColor, Text

# Главное меню
keyboard_main = (
    Keyboard(one_time=False)
    .add(Text("Добавить доход"))
    .add(Text("Добавить расход"))
    .row()
    .add(Text("Статистика"))
    .add(Text("Удалить последнюю запись"))
    .row()
    .add(Text("Общий отчёт"))
    .add(Text("Отчёт по категориям"))
    .row()
    .add(Text("Моя статистика"))
)


def get_category_keyboard(categories):
    """Клавиатура с категориями"""
    keyboard = Keyboard(one_time=True)
    for i, cat in enumerate(categories[:12]):
        keyboard.add(Text(cat))
        if (i + 1) % 2 == 0:
            keyboard.row()
    if len(categories) % 2 != 0:
        keyboard.row()
    keyboard.add(Text("Назад"))
    return keyboard


def get_subcategory_keyboard(subcategories):
    """Клавиатура с подкатегориями"""
    keyboard = Keyboard(one_time=True)
    for i, sub in enumerate(subcategories[:12]):
        keyboard.add(Text(sub))
        if (i + 1) % 2 == 0:
            keyboard.row()
    if len(subcategories) % 2 != 0:
        keyboard.row()
    keyboard.add(Text("Пропустить"))
    keyboard.add(Text("Назад"))
    return keyboard


def get_cancel_keyboard():
    """Клавиатура с отменой"""
    return Keyboard(one_time=True).add(Text("Отмена"))


def get_delete_keyboard():
    """Клавиатура для подтверждения удаления"""
    return Keyboard(one_time=True).add(Text("Да, удалить")).add(Text("Нет"))
