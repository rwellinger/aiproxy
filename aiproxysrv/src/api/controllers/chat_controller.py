"""Chat Controller - HTTP request/response handling for Chat operations (Controller layer)."""

from typing import Any

from business.chat_orchestrator import ChatOrchestrator


class ChatController:
    """Controller for chat generation (HTTP handling only, delegates to orchestrator)."""

    def __init__(self):
        self.orchestrator = ChatOrchestrator()

    def generate_chat(
        self,
        model: str,
        pre_condition: str,
        prompt: str,
        post_condition: str,
        temperature: float = 0.3,
        max_tokens: int = 30,
        user_instructions: str = "",
    ) -> tuple[dict[str, Any], int]:
        """
        Generate chat response with Ollama.

        Args:
            model: Ollama model to use (e.g. "llama3.2:3b")
            pre_condition: Text to prepend to prompt
            prompt: Main prompt text
            post_condition: Text to append to prompt
            temperature: Sampling temperature (default 0.3)
            max_tokens: Maximum tokens to generate (default 30)
            user_instructions: Optional user-specific instructions (placed between prompt and post_condition)

        Returns:
            Tuple of (response_data, status_code)
        """
        return self.orchestrator.generate_chat(
            model, pre_condition, prompt, post_condition, temperature, max_tokens, user_instructions
        )
