"""Configuration module for MusRemixBot"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ============ TELEGRAM ============
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# ============ VK API ============
VK_TOKEN = os.getenv("VK_TOKEN", "")
VK_VERSION = os.getenv("VK_VERSION", "5.131")

# ============ VOICE RECOGNITION ============
YANDEX_SPEECH_KEY = os.getenv("YANDEX_SPEECH_KEY", "")
GOOGLE_SPEECH_KEY = os.getenv("GOOGLE_SPEECH_KEY", "")

# ============ PATHS ============
BASE_DIR = Path(__file__).parent.parent
ASSETS_DIR = BASE_DIR / "assets"
TEMP_DIR = Path(os.getenv("TEMP_DIR", "/tmp/remix_bot"))
LOGS_DIR = BASE_DIR / "logs"

# ============ LIMITS ============
MAX_SEARCH_RESULTS = 5
MAX_TOTAL_RESULTS = 50
VOICE_MAX_DURATION = 60
AUDIO_MAX_SIZE = 50 * 1024 * 1024  # 50MB
REMIX_TIMEOUT = 120

# ============ SEARCH ============
FUZZY_THRESHOLD = 0.6
SEARCH_TIMEOUT = 10

# ============ CACHE ============
CACHE_TTL = 3600
ENABLE_CACHE = True

# Создание директорий
TEMP_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

# Валидация
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не установлен!")
if not ADMIN_ID or ADMIN_ID == 0:
    raise ValueError("ADMIN_ID не установлен!")
