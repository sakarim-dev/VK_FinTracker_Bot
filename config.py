import os
from dotenv import load_dotenv

load_dotenv()

TABLE_ID = os.getenv('TABLE_ID')
VK_TOKEN = os.getenv('VK_TOKEN')
USER_1 = os.getenv('USER_1')
USER_2 = os.getenv('USER_2')

ALLOWED_USERS = [USER_1, USER_2]

USER_NAMES = {
    USER_1: 'Иван',
    USER_2: 'Анна',
}

# Webhook
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', 'your_secret_key_here')

# Временная зона
TIMEZONE_OFFSET = 5

"""Проверка webhook"""


