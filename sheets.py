import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config import TABLE_ID

# Настройка доступа к Google Sheets
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive',
         'https://www.googleapis.com/auth/spreadsheets']

creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)

spreadsheet = client.open_by_key(TABLE_ID)

# Получаем листы
sheet_source = spreadsheet.worksheet('Исходник')
sheet_categories = spreadsheet.worksheet('Категории')

EXPECTED_CATEGORY_HEADERS = ['Категория', 'Подкатегория', 'Тип']


def get_categories_by_type(category_type):
    """Получает список категорий по типу (Расход/Доход)"""
    try:
        records = sheet_categories.get_all_records(expected_headers=EXPECTED_CATEGORY_HEADERS)
        categories = []
        for row in records:
            if row.get('Тип') == category_type:
                cat = row.get('Категория')
                if cat and cat.strip():
                    categories.append(cat)
        return list(dict.fromkeys(categories))
    except Exception as e:
        print(f"Ошибка в get_categories_by_type: {e}")
        return []


def get_subcategories(category_name):
    """Получает список подкатегорий для категории"""
    try:
        records = sheet_categories.get_all_records(expected_headers=EXPECTED_CATEGORY_HEADERS)
        subcategories = []
        for row in records:
            if row.get('Категория') == category_name:
                sub = row.get('Подкатегория')
                if sub and sub.strip():
                    subcategories.append(sub)
        return list(dict.fromkeys(subcategories))
    except Exception as e:
        print(f"Ошибка в get_subcategories: {e}")
        return []


def add_record(date, time, amount, category, subcategory, vk_id, record_type, description):
    """Добавляет запись в таблицу Исходник"""
    all_data = sheet_source.get_all_values()
    next_row = len(all_data) + 1
    sheet_source.update(
        range_name=f'A{next_row}:H{next_row}',
        values=[[date, time, amount, category, subcategory, vk_id, record_type, description]]
    )
    return True


def get_last_user_record(vk_id):
    """Получает последнюю запись пользователя (для удаления)"""
    from utils import get_now
    from datetime import datetime, timedelta

    records = sheet_source.get_all_records()
    for i in range(len(records) - 1, -1, -1):
        row = records[i]
        if str(row.get('Кто добавил', '')) == str(vk_id):
            try:
                record_date = datetime.strptime(row.get('Дата', ''), '%d.%m.%Y')
                record_time = datetime.strptime(row.get('Время', ''), '%H:%M')
                record_datetime = datetime.combine(record_date.date(), record_time.time())
                now = get_now()
                if (now - record_datetime) < timedelta(hours=1):
                    return i + 2, row
            except:
                pass
    return None, None


def delete_record(row_num):
    """Удаляет запись по номеру строки"""
    sheet_source.delete_rows(row_num)
    return True


def get_user_stats(vk_id):
    """Получает полную статистику пользователя"""
    records = sheet_source.get_all_records()
    stats = {
        'today': {'count': 0, 'total': 0},
        'month': {'count': 0, 'total': 0},
        'income': {'count': 0, 'total': 0},
        'expense': {'count': 0, 'total': 0},
        'by_category': {},
    }

    from utils import get_date_str, get_now
    now = get_now()
    today = get_date_str()
    current_month = now.strftime('%m')
    current_year = now.strftime('%Y')

    for row in records:
        if str(row.get('Кто добавил', '')) != str(vk_id):
            continue

        amount = float(row.get('Сумма', 0))
        typ = row.get('Тип', '')
        cat = row.get('Категория', 'Без категории')
        date_str = row.get('Дата', '')

        # По категориям
        stats['by_category'][cat] = stats['by_category'].get(cat, 0) + amount

        # По типу
        if typ == 'Доход':
            stats['income']['total'] += amount
            stats['income']['count'] += 1
        elif typ == 'Расход':
            stats['expense']['total'] += amount
            stats['expense']['count'] += 1

        # За сегодня
        if date_str == today:
            stats['today']['total'] += amount
            stats['today']['count'] += 1

        # За месяц
        if date_str:
            try:
                date_obj = datetime.strptime(date_str, '%d.%m.%Y')
                if date_obj.month == int(current_month) and date_obj.year == int(current_year):
                    stats['month']['total'] += amount
                    stats['month']['count'] += 1
            except:
                pass

    return stats
