"""Single source of truth for allowed AI models.

This module defines all allowed model lists for different AI providers.
Models can be configured via .env file or use defaults.

Architecture:
- All Pydantic schemas import from here
- Mureka models configurable via MUREKA_MODELS env var
"""

from config.settings import MUREKA_MODELS
from config.settings import OLLAMA_ALLOWED_MODELS as _OLLAMA_MODELS_RAW


# Ollama Models (configured via .env OLLAMA_ALLOWED_MODELS, comma-separated)
# Used for template-based generation, chat, compression
OLLAMA_ALLOWED_MODELS = [m.strip() for m in _OLLAMA_MODELS_RAW.split(",") if m.strip()]

# Mureka Models (configured via .env MUREKA_MODELS, comma-separated)
MUREKA_ALLOWED_MODELS = [m.strip() for m in MUREKA_MODELS.split(",") if m.strip()]
