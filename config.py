import os
from dotenv import load_dotenv

load_dotenv()

TABLE_ID = os.getenv('TABLE_ID')
VK_TOKEN = os.getenv('VK_TOKEN')

ALLOWED_USERS = [int(x.strip()) for x in os.getenv('ALLOWED_USERS', '').split(',') if x.strip()]

USER_NAMES = {}
for user_id in ALLOWED_USERS:
    USER_NAMES[user_id] = os.getenv(f'USER_{user_id}_NAME', f'User_{user_id}')

TIMEZONE_OFFSET = 5
