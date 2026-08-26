#!/bin/bash
export PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin

echo "=========================================="
echo "🚀 Начинаем обновление бота"
echo "Время: $(date)"
echo "=========================================="

cd /home/botuser/bots/VK_FinTracker_Bot || exit 1

# Находим git
GIT=$(which git)
if [ -z "$GIT" ]; then
    echo "❌ Git не найден!"
    exit 1
fi
echo "📌 Git: $GIT"

# ПРИНУДИТЕЛЬНО используем ветку master
BRANCH="master"
echo "📌 Ветка: $BRANCH (принудительно)"

# Проверяем изменения
$GIT fetch origin $BRANCH
LOCAL=$($GIT rev-parse HEAD)
REMOTE=$($GIT rev-parse origin/$BRANCH)

if [ "$LOCAL" = "$REMOTE" ]; then
    echo "✅ Код актуален. Обновление не требуется."
    exit 0
fi

echo "📥 Обнаружены изменения. Обновляем код..."

# Сохраняем .env и credentials.json
for file in .env credentials.json; do
    if [ -f "$file" ]; then
        cp "$file" "$file.backup"
    fi
done

# Обновляем код (принудительно с ветки master)
$GIT pull origin $BRANCH

# Восстанавливаем .env и credentials.json
for file in .env credentials.json; do
    if [ -f "$file.backup" ]; then
        mv -f "$file.backup" "$file"
    fi
done

# Обновляем зависимости
if [ -f requirements.txt ]; then
    echo "📦 Обновляем зависимости..."
    source venv/bin/activate
    pip install -r requirements.txt
fi

# Перезапускаем бота
echo "🔄 Перезапускаем бота..."
sudo systemctl restart vk-fintracker-bot

echo "✅ Обновление завершено!"
echo "=========================================="
