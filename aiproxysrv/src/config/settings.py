"""
Zentrale Konfiguration für alle Module
"""

import os

from dotenv import load_dotenv


load_dotenv()

# --------------------------------------------------
# Celery Config
# --------------------------------------------------
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")

# --------------------------------------------------
# MUREKA Config
# --------------------------------------------------
MUREKA_GENERATE_ENDPOINT = os.getenv("MUREKA_GENERATE_ENDPOINT")
MUREKA_INSTRUMENTAL_GENERATE_ENDPOINT = os.getenv("MUREKA_INSTRUMENTAL_GENERATE_ENDPOINT")
MUREKA_INSTRUMENTAL_STATUS_ENDPOINT = os.getenv("MUREKA_INSTRUMENTAL_STATUS_ENDPOINT")
MUREKA_STEM_GENERATE_ENDPOINT = os.getenv("MUREKA_STEM_GENERATE_ENDPOINT")
MUREKA_STATUS_ENDPOINT = os.getenv("MUREKA_STATUS_ENDPOINT")
MUREKA_API_KEY = os.getenv("MUREKA_API_KEY")
MUREKA_BILLING_URL = os.getenv("MUREKA_BILLING_URL")
MUREKA_TIMEOUT = int(os.getenv("MUREKA_TIMEOUT", "30"))
MUREKA_POLL_INTERVAL = int(os.getenv("MUREKA_POLL_INTERVAL", "15"))
MUREKA_MAX_POLL_ATTEMPTS = int(os.getenv("MUREKA_MAX_POLL_ATTEMPTS", "240"))

# Adaptive Polling Intervals
MUREKA_POLL_INTERVAL_SHORT = int(os.getenv("MUREKA_POLL_INTERVAL_SHORT", "5"))
MUREKA_POLL_INTERVAL_MEDIUM = int(os.getenv("MUREKA_POLL_INTERVAL_MEDIUM", "15"))
MUREKA_POLL_INTERVAL_LONG = int(os.getenv("MUREKA_POLL_INTERVAL_LONG", "30"))

# Number of song choices to generate (Mureka API 'n' parameter: min 1, max 3)
_mureka_choices = int(os.getenv("MUREKA_CHOICES", "2"))
MUREKA_CHOICES = max(1, min(3, _mureka_choices))  # Enforce min=1, max=3

# --------------------------------------------------
# OpenAI Config (Images + Chat + Admin API)
# --------------------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ADMIN_API_KEY = os.getenv("OPENAI_ADMIN_API_KEY")
OPENAI_ADMIN_BASE_URL = os.getenv("OPENAI_ADMIN_BASE_URL", "https://api.openai.com/v1")
OPENAI_IMAGE_MODEL = os.getenv("OPENAI_IMAGE_MODEL", "dall-e-3")
OPENAI_CHAT_MODELS = os.getenv(
    "OPENAI_CHAT_MODELS", "gpt-5,gpt-5-mini,gpt-5-nano,gpt-4o,gpt-4o-mini,gpt-4.1,gpt-4.1-mini"
)
OPENAI_TIMEOUT = int(os.getenv("OPENAI_TIMEOUT", "120"))
OPENAI_ADMIN_TIMEOUT = int(os.getenv("OPENAI_ADMIN_TIMEOUT", "30"))

# Backwards compatibility (deprecated - use OPENAI_ADMIN_BASE_URL + endpoints)
OPENAI_URL = os.getenv("OPENAI_URL", f"{OPENAI_ADMIN_BASE_URL}/images")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", OPENAI_IMAGE_MODEL)

# --------------------------------------------------
# Image URL Config
# --------------------------------------------------
IMAGE_BASE_URL = os.getenv("IMAGE_BASE_URL", "http://localhost:8000/api/v1/image")

# --------------------------------------------------
# Flask Server Config
# --------------------------------------------------
FLASK_SERVER_PORT = int(os.getenv("FLASK_SERVER_PORT", "5050"))
FLASK_SERVER_HOST = os.getenv("FLASK_SERVER_HOST", "0.0.0.0")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# --------------------------------------------------
# loguru
# --------------------------------------------------
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG" if DEBUG else "WARNING")


# --------------------------------------------------
# Chat Debug Config
# --------------------------------------------------
CHAT_DEBUG_LOGGING = os.getenv("CHAT_DEBUG_LOGGING", "false").lower() == "true"


# --------------------------------------------------
# Image Storage Config
# --------------------------------------------------
IMAGES_DIR = os.getenv("IMAGES_DIR", "./images" if DEBUG else "/images")
# Control if physical files should be deleted (defaults to true if not set)
# Only set to false in special cases where you want to keep files but delete DB records
DELETE_PHYSICAL_FILES = os.getenv("DELETE_PHYSICAL_FILES", "true").lower() == "true"

# --------------------------------------------------
# Redis Config (falls verwendet)
# --------------------------------------------------
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# --------------------------------------------------
# Ollama Config
# --------------------------------------------------
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://10.0.1.120:11434")
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "60"))
OLLAMA_CHAT_MODELS = os.getenv("OLLAMA_CHAT_MODELS", "")
OLLAMA_DEFAULT_MODEL = os.getenv("OLLAMA_DEFAULT_MODEL", "llama3.2:3b")

# --------------------------------------------------
# JWT Authentication Config
# --------------------------------------------------
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# --------------------------------------------------
# Database Config
# --------------------------------------------------
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://aiproxy:aiproxy123@localhost:5432/aiproxysrv"
    if DEBUG
    else "postgresql://aiproxy:aiproxy123@postgres:5432/aiproxysrv",
)
DATABASE_ECHO = os.getenv("DATABASE_ECHO", "false").lower() == "true"

# Database Connection Pool Settings
# pool_size: Number of permanent connections in the pool
# max_overflow: Additional connections when pool is exhausted
# pool_pre_ping: Test connections before using (prevents stale connections)
# pool_recycle: Recycle connections after N seconds (prevents stale connections)
DATABASE_POOL_SIZE = int(os.getenv("DATABASE_POOL_SIZE", "10"))
DATABASE_MAX_OVERFLOW = int(os.getenv("DATABASE_MAX_OVERFLOW", "20"))
DATABASE_POOL_PRE_PING = os.getenv("DATABASE_POOL_PRE_PING", "true").lower() == "true"
DATABASE_POOL_RECYCLE = int(os.getenv("DATABASE_POOL_RECYCLE", "3600"))  # 1 hour default
