#!/usr/bin/env python3
import os
import subprocess
import hmac
import hashlib
from flask import Flask, request, Response
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET')

if not WEBHOOK_SECRET:
    raise ValueError("WEBHOOK_SECRET не найден в .env файле!")


@app.route('/webhook', methods=['POST'])
def webhook():
    # 1. Проверяем, что запрос от GitHub (по подписи)
    signature = request.headers.get('X-Hub-Signature-256')
    if not signature:
        return Response('Missing signature', status=401)

    # 2. Проверяем секретный ключ
    payload = request.get_data()
    expected = 'sha256=' + hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(signature, expected):
        return Response('Invalid signature', status=401)

    # 3. Проверяем, что это push-событие
    event = request.headers.get('X-GitHub-Event')
    if event != 'push':
        return Response('OK', status=200)

    # 4. Запускаем скрипт обновления в фоне
    subprocess.Popen(['/home/botuser/bots/VK_FinTracker_Bot/update.sh'])

    return Response('Update started', status=200)


@app.route('/health', methods=['GET'])
def health():
    return Response('OK', status=200)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001, debug=False)
