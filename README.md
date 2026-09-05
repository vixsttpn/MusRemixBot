# 🎵 MusRemixBot - Advanced Telegram Music Search & Remix Bot

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Active-success.svg)

Продвинутый Telegram-бот для поиска музыки из ВК с поддержкой 10+ типов обработки аудио и голосового поиска.

## ✨ Основные фишки

- 🔍 **Умный поиск**: нормализация, fuzzy matching, исправление ошибок
- 🎤 **Голосовой поиск**: распознавание речи и автоматический поиск
- 🎵 **ВК как основной источник**: официальная музыка в отличном качестве
- 🎧 **10+ типов обработки**:
  - Original
  - Slowed
  - Sped Up
  - Bass Boosted
  - Nightcore
  - Reverb
  - Lofi
  - Acoustic
  - Instrumental
  - Live
- ⚡ **Быстрая архитектура**: асинхронная обработка, кэширование
- 🛡️ **Надежность**: полная обработка ошибок, валидация
- 🎨 **Чистый интерфейс**: интуитивные кнопки, аккуратное оформление

## 📋 Требования

- Python 3.10+
- FFmpeg
- pip

## 🚀 Установка

### 1. Клонирование репо

```bash
git clone https://github.com/yourusername/MusRemixBot.git
cd MusRemixBot
```

### 2. Установка зависимостей

```bash
# Установить FFmpeg
# Ubuntu/Debian:
sudo apt-get install ffmpeg

# macOS:
brew install ffmpeg

# Windows: скачайте с https://ffmpeg.org/download.html

# Установить Python зависимости
pip install -r requirements.txt
```

### 3. Конфигурация

```bash
# Скопировать пример конфига
cp .env.example .env

# Отредактировать .env
nano .env
```

**Необходимые переменные:**
- `BOT_TOKEN` - токен бота (получить на [@BotFather](https://t.me/BotFather))
- `ADMIN_ID` - ваш Telegram ID
- `VK_TOKEN` - сервисный ключ ВК (опционально, но рекомендуется)

### 4. Запуск

```bash
python main.py
```

## 📁 Структура проекта

```
MusRemixBot/
├── bot/
│   ├── handlers/          # Обработчики команд
│   ├── services/          # Бизнес-логика
│   │   ├── vk_service.py       # Работа с ВК
│   │   ├── search_service.py   # Поиск с нормализацией
│   │   ├── voice_service.py    # Распознавание голоса
│   │   └── remix_service.py    # Обработка аудио
│   ├── keyboards/         # Клавиатуры
│   ├── states/           # FSM состояния
│   ├── models/           # Модели данных
│   ├── utils/            # Утилиты
│   └── config.py         # Конфигурация
│
├── assets/               # Картинки
│   ├── search/
│   ├── remix/
│   └── errors/
│
├── logs/                 # Логи
├── tests/                # Тесты
├── main.py              # Точка входа
├── requirements.txt
├── .env.example
└── README.md
```

## 🎯 Как использовать

### Текстовый поиск

1. Напиши название песни или исполнителя
2. Выбери трек из результатов
3. Выбери тип обработки
4. Получи готовый файл!

### Голосовой поиск

1. Отправь голосовое сообщение
2. Бот распознает текст
3. Покажет результаты поиска
4. Выбери трек и обработку

### Примеры запросов

✅ Хорошо:
- "Очередной день"
- "The Weeknd - Starboy"
- "Lofi hip hop"
- "я помню этот вечер" (слова из песни)

❌ Плохо:
- "м" (слишком коротко)
- "???????" (только символы)

## 🔌 Интеграции

### VK API

Для включения поиска в ВК:
1. Создайте приложение на https://vk.com/dev
2. Получите сервисный ключ
3. Добавьте в `.env`:
   ```
   VK_TOKEN=your_token_here
   ```

### Голосовой поиск

Поддерживаются:
- **Yandex SpeechKit** (рекомендуется)
- **Google Cloud Speech**

Добавьте ключ в `.env`:
```
YANDEX_SPEECH_KEY=your_key_here
```

## 🛠️ Разработка

### Запуск в режиме разработки

```bash
# С логами DEBUG
LOG_LEVEL=DEBUG python main.py

# С hot-reload (требует watchdog)
pip install watchdog
watchmedo auto-restart -d bot -d main.py -p '*.py' python main.py
```

### Запуск тестов

```bash
pytest tests/ -v
```

### Форматирование кода

```bash
# Black formatting
black .

# Import sorting
isort .

# Linting
flake8 .

# Type checking
mypy .
```

## 📊 Архитектура

### Services

Каждый сервис отвечает за отдельную область:

- **VKService**: поиск и скачивание из ВК
- **SearchService**: нормализация запроса, fuzzy search
- **VoiceService**: распознавание голоса (Yandex/Google)
- **RemixService**: обработка аудио через FFmpeg

### FSM States

- `SearchStates`: поиск музыки
- `RemixStates`: выбор типа обработки
- `VoiceStates`: голосовые сообщения

### User Context

Каждый пользователь имеет собственный контекст:
- текущий запрос
- результаты поиска
- выбранный трек
- выбранный тип обработки

Контекст сбрасывается после каждого завершённого действия.

## ⚡ Производительность

- Асинхронная обработка всех операций
- Кэширование результатов поиска
- Оптимизированные FFmpeg команды
- Удаление временных файлов

## 🐛 Обработка ошибок

Обработаны:
- Ничего не найдено
- ВК недоступен
- Аудио удалено
- Ошибка FFmpeg
- Таймауты
- Сетевые ошибки
- Невалидные выборы

## 🔐 Безопасность

- Валидация всех входных данных
- Санитизация путей файлов
- Таймауты на все операции
- Очистка временных файлов
- Логирование всех действий

## 📈 Мониторинг

Логи сохраняются в `logs/bot.log`:

```
2024-01-15 10:30:45 - __main__ - INFO - ✅ MusRemixBot started
2024-01-15 10:31:02 - bot.services.search_service - INFO - Searching for: adele hello
2024-01-15 10:31:05 - bot.services.vk_service - INFO - Found 15 tracks in VK
```

## 🚀 Деплой

### GitHub Actions (CI/CD)

Смотри `.github/workflows/` для примеров.

### Docker (рекомендуется)

```bash
docker build -t musremixbot .
docker run -e BOT_TOKEN=... -e ADMIN_ID=... musremixbot
```

### Heroku/Railway/Render

1. Создайте репо на GitHub
2. Подключите сервис
3. Добавьте переменные окружения
4. Деплой!

## 📝 Лицензия

MIT License - смотри LICENSE файл

## 💬 Поддержка

Возникли проблемы? 
- Проверьте логи: `tail -f logs/bot.log`
- Создайте Issue на GitHub
- Проверьте FFmpeg: `ffmpeg -version`

## 🤝 Contributing

Pull requests приветствуются! 

1. Fork проект
2. Создайте feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit изменения (`git commit -m 'Add some AmazingFeature'`)
4. Push в branch (`git push origin feature/AmazingFeature`)
5. Откройте Pull Request

## 📚 Документация

- [Telegram Bot API](https://core.telegram.org/bots/api)
- [aiogram](https://docs.aiogram.dev/)
- [VK API](https://vk.com/dev/methods)
- [FFmpeg](https://ffmpeg.org/documentation.html)

---

Made with ❤️ for music lovers 🎵

**Версия**: 2.0.0  
**Последнее обновление**: Январь 2024
