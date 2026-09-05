FROM python:3.11-slim

# Метаданные
LABEL maintainer="MusRemixBot"
LABEL description="Advanced Telegram Music Search & Remix Bot"

# Установить зависимости системы
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /app

# Скопировать requirements
COPY requirements.txt .

# Установить Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Скопировать весь проект
COPY . .

# Создать user для безопасности
RUN useradd -m -u 1000 botuser && chown -R botuser:botuser /app
USER botuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import asyncio; print('OK')" || exit 1

# Запуск бота
EXPOSE 10000

CMD ["python", "run_render.py"]
