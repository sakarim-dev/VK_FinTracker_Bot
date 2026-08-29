from vkbottle import Keyboard, KeyboardButtonColor, Text

# Главное меню
keyboard_main = (
    Keyboard(one_time=False)
    .add(Text("Добавить расход"))
    .add(Text("Добавить доход"))
    .row()
    .add(Text("Удалить последнюю запись"))
)


def get_category_keyboard(categories):
    keyboard = Keyboard(one_time=True)

    # Добавляем все категории по 2 в ряд
    for i, cat in enumerate(categories):
        keyboard.add(Text(cat))
        if (i + 1) % 2 == 0:  # После каждой второй кнопки - перенос строки
            keyboard.row()

    # Если последняя строка неполная, добавляем перенос
    if len(categories) % 2 != 0:
        keyboard.row()

    # Кнопка возврата в главное меню
    keyboard.add(Text("Назад в меню"))

    return keyboard


def get_subcategory_keyboard(subcategories):
    keyboard = Keyboard(one_time=True)

    # Добавляем все подкатегории по 2 в ряд
    for i, sub in enumerate(subcategories):
        keyboard.add(Text(sub))
        if (i + 1) % 2 == 0:
            keyboard.row()

    # Если последняя строка неполная, добавляем перенос
    if len(subcategories) % 2 != 0:
        keyboard.row()

    keyboard.add(Text("Пропустить"))
    keyboard.add(Text("Назад"))
    return keyboard


def get_cancel_keyboard():
    return Keyboard(one_time=True).add(Text("Пропустить")).add(Text("Отмена"))


def get_delete_keyboard():
    return Keyboard(one_time=True).add(Text("Да, удалить")).add(Text("Нет"))
