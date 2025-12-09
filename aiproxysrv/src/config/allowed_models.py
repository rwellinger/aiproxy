"""Single source of truth for allowed AI models.

This module defines all allowed model lists for different AI providers.
Models can be configured via .env file or use defaults.

Architecture:
- All Pydantic schemas import from here
- Mureka models configurable via MUREKA_MODELS env var
"""

from config.settings import MUREKA_MODELS


# Ollama Models (used for template-based generation, chat, compression)
OLLAMA_ALLOWED_MODELS = [
    "llama3.2:3b",
    "gpt-oss:20b",
    "deepseek-r1:8b",
    "gemma3:4b",
]

# Mureka Models (configured via .env MUREKA_MODELS, comma-separated)
MUREKA_ALLOWED_MODELS = [m.strip() for m in MUREKA_MODELS.split(",") if m.strip()]
