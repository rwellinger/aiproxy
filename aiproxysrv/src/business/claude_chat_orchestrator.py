"""Claude Chat Orchestrator - Coordinates Claude Messages API operations (NOT testable, orchestration only)."""

from typing import Any

from adapters.claude.api_client import ClaudeAPIClient
from business.claude_chat_transformer import build_messages_payload, get_available_models, parse_messages_response
from config.settings import CHAT_DEBUG_LOGGING, CLAUDE_CHAT_MODELS
from utils.logger import logger


class ClaudeChatOrchestrator:
    """Orchestrator for Claude Messages API integration (coordinates services, NO business logic)."""

    def __init__(self):
        self.api_client = ClaudeAPIClient()

    def send_chat_message(
        self, model: str, messages: list[dict[str, str]], max_tokens: int, temperature: float = 0.7
    ) -> tuple[str, int, int]:
        """
        Send chat message to Claude Messages API (orchestrates transformer + API client).

        Args:
            model: Claude model name (e.g., "claude-sonnet-4-5-20250929")
            messages: List of messages with role and content
            max_tokens: Maximum tokens to generate (REQUIRED by Claude)
            temperature: Sampling temperature (0.0-1.0)

        Returns:
            Tuple of (assistant_content, input_tokens, output_tokens)

        Raises:
            ClaudeAPIError: If API call fails
        """
        # Build payload using transformer
        payload = build_messages_payload(model, messages, max_tokens, temperature)

        # Call API client
        resp_json = self.api_client.messages_create(payload)

        # Parse response using transformer
        content, input_tokens, output_tokens = parse_messages_response(resp_json)

        if CHAT_DEBUG_LOGGING:
            logger.debug(
                "Token counts extracted",
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                content_length=len(content),
            )

        return content, input_tokens, output_tokens

    def get_available_models(self) -> list[dict[str, Any]]:
        """
        Get list of available Claude Chat models from configuration.

        Returns:
            List of model dictionaries with name and context_window
        """
        # Use transformer to parse models config
        return get_available_models(CLAUDE_CHAT_MODELS)
