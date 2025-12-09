"""Single source of truth for allowed AI models.

This module defines all allowed model lists for different AI providers.
When adding a new model, update ONLY this file.

Architecture:
- All Pydantic schemas import from here
- No hardcoded model lists anywhere else in the codebase
"""

# Ollama Models (used for template-based generation, chat, compression)
OLLAMA_ALLOWED_MODELS = [
    "llama3.2:3b",
    "gpt-oss:20b",
    "deepseek-r1:8b",
    "gemma3:4b",
]

# Mureka Models (used for song generation)
MUREKA_ALLOWED_MODELS = [
    "auto",
    "mureka-7.6",
    "mureka-7.5",
    "mureka-o2",
    "mureka-o1",
]
