import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

APP_NAME = "VoiceNote"
APP_SUBTITLE = "Local AI Voice Notes & Analytics"
VERSION = "0.1.0"

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GROQ_STT_MODEL = "whisper-large-v3"
LOCAL_STT_MODEL = "small"

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RECORDINGS_DIR = DATA_DIR / "recordings"

# Database Configuration (Strictly PostgreSQL Engine)
DB_ENGINE = "postgres"
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_DB = os.getenv("POSTGRES_DB", "voicenote")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
RECORDINGS_DIR.mkdir(exist_ok=True)