"""Работа с Google Sheets.

Модуль изолирует Google Sheets от handlers. В дальнейшем этот слой можно
заменить на SQLite/PostgreSQL без переписывания пользовательских сценариев.
"""
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from config import TABLE_ID
from categories import get_categories_by_type, get_subcategories
from logger import logger, log_sheets_action

SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets",
]
HEADERS = ["Дата", "Время", "Сумма", "Категория", "Подкатегория", "ID", "Тип", "Описание"]


def _connect():
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", SCOPE)
    return gspread.authorize(creds).open_by_key(TABLE_ID).worksheet("Исходник")


sheet_source = _connect()


def _ensure_headers():
    values = sheet_source.row_values(1)
    if not values:
        sheet_source.update(range_name="A1:H1", values=[HEADERS])
        return
    # Не перезаписываем существующую таблицу: это важно для старых данных.
    if values[: len(HEADERS)] != HEADERS:
        logger.warning("Заголовки Sheets отличаются от ожидаемых: %s", values)


def add_record(date, time, amount, category, subcategory, vk_id, record_type, description):
    """Добавляет финансовую запись одной атомарной операцией append_row."""
    _ensure_headers()
    row = [date, time, amount, category, subcategory, vk_id, record_type, description]
    sheet_source.append_row(row, value_input_option="USER_ENTERED", insert_data_option="INSERT_ROWS")
    log_sheets_action("add_record", f"{record_type}: {amount} ({category})")
    return True


def get_last_user_record(vk_id, max_age_hours=1):
    """Находит последнюю запись пользователя и реальный номер строки Sheets.

    Исправление критической ошибки исходника: таблица хранит ID в колонке
    «ID», а старый код искал колонку «Кто добавил», поэтому запись не находилась.
    Поддерживается и старое имя «Кто добавил» для совместимости.
    """
    from utils import get_now

    try:
        records = sheet_source.get_all_records()
        if not records:
            return None, None

        now = get_now()
        for index in range(len(records) - 1, -1, -1):
            row = records[index]
            owner = row.get("ID", row.get("Кто добавил", ""))
            if str(owner) != str(vk_id):
                continue

            try:
                record_date = datetime.datetime.strptime(str(row.get("Дата", "")), "%d.%m.%Y").date()
                record_time = datetime.datetime.strptime(str(row.get("Время", "")), "%H:%M").time()
                record_dt = datetime.datetime.combine(record_date, record_time)
            except (TypeError, ValueError):
                logger.warning("Пропущена запись с некорректной датой/временем: %s", row)
                continue

            if datetime.timedelta(0) <= now - record_dt <= datetime.timedelta(hours=max_age_hours):
                # get_all_records() начинается со строки 2.
                return index + 2, row
        return None, None
    except Exception:
        logger.exception("Ошибка поиска последней записи пользователя %s", vk_id)
        return None, None


def delete_record(row_num):
    """Удаляет указанную строку из Google Sheets."""
    if not isinstance(row_num, int) or row_num < 2:
        raise ValueError(f"Некорректный номер строки: {row_num}")
    sheet_source.delete_rows(row_num)
    log_sheets_action("delete_record", f"Удалена строка {row_num}")
    return True
