"""
Model Context Window Configuration

Maps Ollama model names to their context window sizes (in tokens).
Default: 2048 tokens (Ollama standard)
"""

MODEL_CONTEXT_WINDOWS = {
    # GPT-OSS Models
    "gpt-oss:20b": 8192,

    # LLaMA Models
    "llama2:7b": 4096,
    "llama2:13b": 4096,
    "llama2:70b": 4096,
    "llama3:8b": 8192,
    "llama3:70b": 8192,
    "llama3.1:8b": 131072,  # 128k context
    "llama3.1:70b": 131072,  # 128k context
    "llama3.2:1b": 131072,  # 128k context
    "llama3.2:3b": 131072,  # 128k context

    # Mistral Models
    "mistral:7b": 8192,
    "mistral:instruct": 8192,
    "mixtral:8x7b": 32768,  # 32k context

    # Gemma Models
    "gemma:2b": 8192,
    "gemma:7b": 8192,
    "gemma2:9b": 8192,
    "gemma2:27b": 8192,

    # CodeLlama Models
    "codellama:7b": 16384,  # 16k context
    "codellama:13b": 16384,
    "codellama:34b": 16384,

    # Phi Models
    "phi3:mini": 4096,
    "phi3:medium": 4096,

    # Qwen Models
    "qwen:7b": 8192,
    "qwen:14b": 8192,
    "qwen2:7b": 32768,  # 32k context

    # Default fallback
    "default": 2048
}


def get_context_window_size(model_name: str) -> int:
    """
    Get context window size for a given model.

    Args:
        model_name: Ollama model name (e.g., "gpt-oss:20b", "llama3.1:8b")

    Returns:
        Context window size in tokens

    Examples:
        >>> get_context_window_size("gpt-oss:20b")
        8192
        >>> get_context_window_size("llama3.1:8b")
        131072
        >>> get_context_window_size("unknown-model")
        2048
    """
    # Try exact match first
    if model_name in MODEL_CONTEXT_WINDOWS:
        return MODEL_CONTEXT_WINDOWS[model_name]

    # Try base model match (e.g., "llama3:8b-instruct" -> "llama3:8b")
    base_model = model_name.split("-")[0]
    if base_model in MODEL_CONTEXT_WINDOWS:
        return MODEL_CONTEXT_WINDOWS[base_model]

    # Try family match (e.g., "llama3" from "llama3:custom")
    model_family = model_name.split(":")[0]
    for key in MODEL_CONTEXT_WINDOWS:
        if key.startswith(model_family):
            return MODEL_CONTEXT_WINDOWS[key]

    # Return default
    return MODEL_CONTEXT_WINDOWS["default"]
