"""Конфигурация бота."""
import os
from dotenv import load_dotenv

load_dotenv()

TABLE_ID = os.getenv("TABLE_ID")
VK_TOKEN = os.getenv("VK_TOKEN")

ALLOWED_USERS = [
    int(value.strip())
    for value in os.getenv("ALLOWED_USERS", "").split(",")
    if value.strip()
]

USER_NAMES = {
    user_id: os.getenv(f"USER_{user_id}_NAME", f"User_{user_id}")
    for user_id in ALLOWED_USERS
}

TIMEZONE_OFFSET = int(os.getenv("TIMEZONE_OFFSET", "5"))
