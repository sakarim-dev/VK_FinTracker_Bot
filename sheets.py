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
HEADERS = ["Дата", "Время", "Сумма", "Категория", "Подкатегория", "Имя", "Тип", "Описание"]


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

    Последняя строка с данными определяется как первая строка, где ячейка A
    пуста (не содержит значения). Форматирование, заливка и границы не влияют
    на результат — проверяется исключительно наличие значения в ячейке.

    col_values() отрезает пустые хвосты и не подходит, если ниже данных
    есть отформатированные пустые строки. Поэтому используем get() на весь
    столбец с явным указанием диапазона до максимальной строки листа.
    """
    from utils import get_now

    try:
        rows_a = sheet_source.get(
            "A1:A",
            value_render_option="UNFORMATTED_VALUE",
        )
        last_row = 1  # индекс последней строки с данными (1-based)
        for idx, cell in enumerate(rows_a[1:], start=2):  # пропускаем строку 1
            value = str(cell[0]).strip() if cell else ""
            if not value:
                # Первая пустая A — данные закончились на предыдущей строке
                last_row = idx - 1
                break
        else:
            # Пустых строк не встретили — данные идут до конца полученного диапазона
            last_row = len(rows_a)

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
