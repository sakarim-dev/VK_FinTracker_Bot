"""
Список категорий и подкатегорий для финансового бота
"""

CATEGORIES = {
    'Доход': {
        'Зарплата': ['Основная', 'Премия', 'Аванс', 'Бонус'],
        'Подарок': ['Подарок'],
        'Прочие доходы': ['Другие доходы']
    },
    'Расход': {
        'Долги': ['Общая'],
        'Еда': ['Доставка', 'Кафе', 'Перекусы', 'Продукты', 'Продукты (заказ)'],
        'ЖКХ': ['Квартира НВ', 'Квартира Тюмень'],
        'Здоровье': ['Аптека', 'Врачи', 'Анализы'],
        'Интернет': ['Квартира НВ', 'Квартира Тюмень'],
        'Кредиты': ['Потребительский'],
        'Маркетплейс': ['Ozon', 'Wildberries', 'Прочие'],
        'На подарки': ['Близким', 'Друг другу', 'Себе'],
        'Подписки': ['Яндекс Плюс', 'Лента', 'AdminVPS', 'ИВИ', 'СберПрайм'],
        'Прочие расходы': ['Другие расходы'],
        'Развлечения': ['Игры', 'Кино', 'Концерты', 'Хобби'],
        'Связь': ['Билайн', 'Мегафон'],
        'Штрафы': ['Solaris', 'Hilux'],
        'Автомобили': ['Топливо', 'Ремонт'],
        'Никотин': ['Никотин'],
    },
}


def get_categories_by_type(category_type):
    if category_type not in CATEGORIES:
        return []

    return list(CATEGORIES[category_type].keys())


def get_subcategories(category_name):
    # Ищем категорию во всех типах
    for cat_type, categories in CATEGORIES.items():
        if category_name in categories:
            return categories[category_name]

    return []


def get_all_categories():
    result = {}
    for cat_type, categories in CATEGORIES.items():
        result[cat_type] = list(categories.keys())
    return result


def get_all_subcategories():
    result = {}
    for categories in CATEGORIES.values():
        for category, subcategories in categories.items():
            result[category] = subcategories
    return result


def category_exists(category_name):
    for categories in CATEGORIES.values():
        if category_name in categories:
            return True
    return False


def subcategory_exists(category_name, subcategory_name):
    subcategories = get_subcategories(category_name)
    return subcategory_name in subcategories
