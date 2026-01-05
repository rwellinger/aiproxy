"""Claude Chat Transformer - Pure functions for Claude Messages API payload building and response parsing."""

from typing import Any


def build_messages_payload(
    model: str, messages: list[dict[str, str]], max_tokens: int, temperature: float = 0.7
) -> dict[str, Any]:
    """
    Build payload for Claude Messages API request.

    Args:
        model: Claude model name (e.g., "claude-sonnet-4-5-20250929")
        messages: List of messages with role and content (user/assistant only)
        max_tokens: Maximum tokens to generate (REQUIRED by Claude API)
        temperature: Sampling temperature (0.0-1.0)

    Returns:
        Dictionary with Claude Messages API payload

    Notes:
        - System messages must be extracted and placed in separate 'system' field
        - Claude API requires max_tokens (not optional like OpenAI)
        - Temperature range is 0.0-1.0 (not 0.0-2.0 like OpenAI)

    Examples:
        >>> payload = build_messages_payload(
        ...     "claude-sonnet-4-5-20250929",
        ...     [{"role": "user", "content": "Hi"}],
        ...     max_tokens=1024
        ... )
        >>> payload["model"]
        'claude-sonnet-4-5-20250929'
        >>> payload["max_tokens"]
        1024
    """
    # Extract system message if present (Claude expects it in separate field)
    system_message = None
    filtered_messages = []

    for msg in messages:
        if msg.get("role") == "system":
            system_message = msg.get("content", "")
        else:
            filtered_messages.append(msg)

    # Build base payload
    payload: dict[str, Any] = {
        "model": model,
        "max_tokens": max_tokens,  # Required by Claude API
        "messages": filtered_messages,
    }

    # Add system message if present
    if system_message:
        payload["system"] = system_message

    # Add temperature (0.0-1.0 range)
    if temperature is not None:
        payload["temperature"] = max(0.0, min(1.0, temperature))  # Clamp to 0.0-1.0

    return payload


def parse_messages_response(response_json: dict[str, Any]) -> tuple[str, int, int]:
    """
    Parse Claude Messages API response and extract content + token counts.

    Args:
        response_json: Claude Messages API response JSON

    Returns:
        Tuple of (assistant_content, input_tokens, output_tokens)

    Raises:
        ValueError: If response format is invalid

    Notes:
        - Claude returns content as array of objects: [{"type": "text", "text": "..."}]
        - Usage has "input_tokens" and "output_tokens" (not prompt_tokens/completion_tokens)

    Examples:
        >>> response = {
        ...     "content": [{"type": "text", "text": "Hello!"}],
        ...     "usage": {"input_tokens": 10, "output_tokens": 5}
        ... }
        >>> content, input_tokens, output_tokens = parse_messages_response(response)
        >>> content
        'Hello!'
        >>> input_tokens
        10
        >>> output_tokens
        5
    """
    if "content" not in response_json or len(response_json["content"]) == 0:
        raise ValueError("Invalid API response format: no content found")

    # Extract text from content array
    content_blocks = response_json["content"]
    text_parts = []
    for block in content_blocks:
        if block.get("type") == "text":
            text_parts.append(block.get("text", ""))

    content = "".join(text_parts)

    # Extract token usage
    usage = response_json.get("usage", {})
    input_tokens = usage.get("input_tokens", 0)
    output_tokens = usage.get("output_tokens", 0)

    return content, input_tokens, output_tokens


def get_model_context_window(_model_name: str) -> int:
    """
    Get context window size for Claude model.

    Args:
        _model_name: Claude model name (unused, all models have same context window)

    Returns:
        Context window size in tokens

    Notes:
        - All current Claude models have 200k context window
        - This includes Sonnet, Haiku, and Opus variants

    Examples:
        >>> get_model_context_window("claude-sonnet-4-5-20250929")
        200000
        >>> get_model_context_window("claude-haiku-4-5-20250929")
        200000
        >>> get_model_context_window("claude-opus-4-5-20251101")
        200000
    """
    # All current Claude models have 200k context window
    return 200000


def get_available_models(models_config: str) -> list[dict[str, Any]]:
    """
    Parse comma-separated model names and return list with context windows.

    Args:
        models_config: Comma-separated model names (e.g., "claude-sonnet-4-5-20250929,claude-haiku-4-5-20250929")

    Returns:
        List of model dictionaries with name and context_window

    Examples:
        >>> models = get_available_models("claude-sonnet-4-5-20250929,claude-haiku-4-5-20250929")
        >>> len(models)
        2
        >>> models[0]["name"]
        'claude-sonnet-4-5-20250929'
        >>> models[0]["context_window"]
        200000
    """
    model_names = [m.strip() for m in models_config.split(",") if m.strip()]

    models = []
    for model_name in model_names:
        models.append(
            {
                "name": model_name,
                "context_window": get_model_context_window(model_name),
            }
        )

    return models
