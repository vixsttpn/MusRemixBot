#!/bin/bash

# MusRemixBot Setup Script
# Автоматическая инициализация проекта

set -e

echo "================================"
echo "🎵 MusRemixBot Setup"
echo "================================"
echo ""

# Проверка Python
echo "1️⃣  Проверка Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не установлен!"
    echo "Установите Python 3.10+ перед запуском"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
echo "✅ Python $PYTHON_VERSION найден"

# Проверка FFmpeg
echo ""
echo "2️⃣  Проверка FFmpeg..."
if ! command -v ffmpeg &> /dev/null; then
    echo "❌ FFmpeg не установлен!"
    echo ""
    echo "Установите FFmpeg:"
    echo "  Ubuntu/Debian: sudo apt-get install ffmpeg"
    echo "  macOS: brew install ffmpeg"
    echo "  Windows: https://ffmpeg.org/download.html"
    exit 1
fi

FFMPEG_VERSION=$(ffmpeg -version | head -n1 | cut -d' ' -f3)
echo "✅ FFmpeg $FFMPEG_VERSION найден"

# Создание виртуального окружения
echo ""
echo "3️⃣  Создание виртуального окружения..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Виртуальное окружение создано"
else
    echo "✅ Виртуальное окружение уже существует"
fi

# Активация виртуального окружения
source venv/bin/activate

# Обновление pip
echo ""
echo "4️⃣  Обновление pip..."
pip install --upgrade pip setuptools wheel > /dev/null

# Установка зависимостей
echo ""
echo "5️⃣  Установка зависимостей..."
pip install -r requirements.txt

# Создание .env
echo ""
echo "6️⃣  Конфигурация..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ Создан файл .env"
    echo ""
    echo "⚠️  ВНИМАНИЕ: Отредактируйте .env и добавьте:"
    echo "   - BOT_TOKEN (от @BotFather)"
    echo "   - ADMIN_ID (ваш Telegram ID)"
    echo "   - VK_TOKEN (опционально)"
else
    echo "✅ Файл .env уже существует"
fi

# Создание директорий
echo ""
echo "7️⃣  Создание директорий..."
mkdir -p logs assets tmp
echo "✅ Директории готовы"

# Итого
echo ""
echo "================================"
echo "✅ Установка завершена!"
echo "================================"
echo ""
echo "Далее:"
echo "1. Отредактируйте .env файл:"
echo "   nano .env"
echo ""
echo "2. Запустите бота:"
echo "   python main.py"
echo ""
echo "3. Или используйте Docker:"
echo "   docker build -t musremixbot ."
echo "   docker run -e BOT_TOKEN=... -e ADMIN_ID=... musremixbot"
echo ""
