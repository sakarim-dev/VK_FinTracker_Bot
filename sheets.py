import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from logger import logger, log_sheets_action
from config import TABLE_ID
from categories import get_categories_by_type, get_subcategories  # Импортируем из categories.py

# Настройка доступа к Google Sheets
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive',
         'https://www.googleapis.com/auth/spreadsheets']

creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)

spreadsheet = client.open_by_key(TABLE_ID)

# Получаем листы
sheet_source = spreadsheet.worksheet('Исходник')


def add_record(date, time, amount, category, subcategory, vk_id, record_type, description):
    try:
        # 1. Проверяем наличие заголовков
        all_data = sheet_source.get_all_values()
        if not all_data:
            headers = ['Дата', 'Время', 'Сумма', 'Категория', 'Подкатегория', 'ID', 'Тип', 'Описание']
            sheet_source.append_row(headers)
            log_sheets_action("add_record", "Созданы заголовки")
            next_row = 2
        else:
            # 2. Получаем все значения из столбца А (Дата)
            col_a = sheet_source.col_values(1)

            # 3. Ищем первую пустую строку (начиная со строки 2)
            next_row = None

            for i in range(1, len(col_a)):  # i - индекс в списке
                row_num = i + 1  # Номер строки в таблице

                # Проверяем, пустая ли ячейка в столбце А
                cell_value = col_a[i] if i < len(col_a) else ''
                if not cell_value or cell_value.strip() == '':
                    next_row = row_num
                    break

            # Если пустых строк не найдено, добавляем новую в конец
            if next_row is None:
                next_row = len(col_a) + 1

        # 4. Проверяем, не превышает ли лимит строк
        if next_row > sheet_source.row_count:
            rows_to_add = next_row - sheet_source.row_count + 10
            sheet_source.add_rows(rows_to_add)
            log_sheets_action("add_rows", f"Добавлено {rows_to_add} строк")

        # 5. Записываем данные
        sheet_source.update(
            range_name=f'A{next_row}:H{next_row}',
            values=[[date, time, amount, category, subcategory, vk_id, record_type, description]]
        )

        log_sheets_action("add_record", f"{record_type}: {amount} ({category}) в строку {next_row}")
        return True

    except Exception as e:
        logger.error(f"❌ Ошибка записи в Sheets: {e}")
        raise


def get_last_user_record(vk_id):
    """Получает последнюю запись пользователя (для удаления)"""
    from utils import get_now
    from datetime import datetime, timedelta

    try:
        records = sheet_source.get_all_records()
        if not records:
            return None, None

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
                except Exception as e:
                    logger.error(f"Ошибка парсинга даты: {e}")
                    continue
        return None, None
    except Exception as e:
        logger.error(f"Ошибка в get_last_user_record: {e}")
        return None, None


def delete_record(row_num):
    """Удаляет запись по номеру строки"""
    try:
        sheet_source.delete_rows(row_num)
        log_sheets_action("delete_record", f"Удалена строка {row_num}")
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка удаления записи: {e}")
        raise


def get_user_stats(vk_id):
    """Получает полную статистику пользователя"""
    try:
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

            try:
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
                        date_obj = datetime.datetime.strptime(date_str, '%d.%m.%Y')
                        if date_obj.month == int(current_month) and date_obj.year == int(current_year):
                            stats['month']['total'] += amount
                            stats['month']['count'] += 1
                    except:
                        pass
            except Exception as e:
                logger.error(f"Ошибка обработки строки: {e}")
                continue

        return stats
    except Exception as e:
        logger.error(f"Ошибка в get_user_stats: {e}")
        return {
            'today': {'count': 0, 'total': 0},
            'month': {'count': 0, 'total': 0},
            'income': {'count': 0, 'total': 0},
            'expense': {'count': 0, 'total': 0},
            'by_category': {},
        }