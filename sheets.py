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
    """Находит последнюю запись пользователя, ориентируясь только на столбец A.

    Вспомогательные списки/валидации в B:H могут быть протянуты далеко вниз.
    Поэтому последняя строка определяется не размером листа и не содержимым
    других столбцов, а последней ячейкой A, содержащей корректную дату записи.
    """
    from utils import get_now

    try:
        col_a = sheet_source.col_values(1)

        # Ищем последнюю строку именно с датой в A.
        # Пустые A ниже неё полностью игнорируются, даже если B:H заполнены.
        last_row = 1
        for row_num in range(len(col_a), 1, -1):
            value = str(col_a[row_num - 1]).strip()
            if not value:
                continue
            try:
                datetime.datetime.strptime(value, "%d.%m.%Y")
                last_row = row_num
                break
            except ValueError:
                # Не считаем мусор/заголовок реальной финансовой записью.
                continue

        if last_row < 2:
            return None, None

        values = sheet_source.get(f"A2:H{last_row}")
        if not values:
            return None, None

        now = get_now()

        for row_num in range(last_row, 1, -1):
            row_values = values[row_num - 2] if row_num - 2 < len(values) else []
            row = dict(zip(
                HEADERS,
                row_values + [""] * max(0, len(HEADERS) - len(row_values))
            ))

            if str(row.get("ID", "")).strip() != str(vk_id).strip():
                continue

            try:
                record_date = datetime.datetime.strptime(
                    str(row.get("Дата", "")).strip(), "%d.%m.%Y"
                ).date()
                record_time = datetime.datetime.strptime(
                    str(row.get("Время", "")).strip(), "%H:%M"
                ).time()
            except (TypeError, ValueError):
                continue

            record_dt = datetime.datetime.combine(record_date, record_time)
            age = now - record_dt

            if datetime.timedelta(0) <= age <= datetime.timedelta(hours=max_age_hours):
                return row_num, row

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
