"""OpenAI Chat Controller - Handles business logic for OpenAI Chat API operations."""
import traceback
import requests
from typing import Tuple, Dict, Any, List
from utils.logger import logger
from config.settings import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_TIMEOUT


class OpenAIChatController:
    """Controller for OpenAI Chat API integration."""

    def __init__(self):
        self.api_key = OPENAI_API_KEY
        self.base_url = OPENAI_BASE_URL
        self.timeout = OPENAI_TIMEOUT

    def send_chat_message(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = None
    ) -> Tuple[str, int, int]:
        """
        Send chat message to OpenAI API.

        Args:
            model: OpenAI model name (e.g., "gpt-4o")
            messages: List of messages with role and content
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens to generate (optional)

        Returns:
            Tuple of (assistant_content, prompt_tokens, completion_tokens)

        Raises:
            OpenAIAPIError: If API call fails
        """
        if not self.api_key:
            raise OpenAIAPIError("OpenAI API key not configured")

        # Build API URL
        api_url = f"{self.base_url}/chat/completions"

        # Build request payload
        payload = {
            "model": model,
            "messages": messages,
        }

        # GPT-5 models don't support custom temperature (only default 1.0)
        # Other models support temperature 0.0-2.0
        if not model.startswith("gpt-5"):
            payload["temperature"] = temperature

        if max_tokens:
            payload["max_tokens"] = max_tokens

        # Set headers with API key
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Debug: Log complete request details
        logger.debug(
            f"OpenAI Chat API Request | "
            f"URL: {api_url} | "
            f"Model: {model} | "
            f"Temperature: {'temperature' in payload} | "
            f"Messages: {len(messages)} | "
            f"Payload: {payload}"
        )

        try:
            resp = requests.post(
                api_url,
                headers=headers,
                json=payload,
                timeout=self.timeout
            )

            # Log response details before raising for status
            logger.debug(f"OpenAI API Response Status: {resp.status_code}")

            # Check for HTTP errors
            if resp.status_code != 200:
                error_body = resp.text
                logger.error(
                    "OpenAI API HTTP Error",
                    status_code=resp.status_code,
                    response_body=error_body[:500]  # First 500 chars
                )
                raise OpenAIAPIError(f"HTTP {resp.status_code}: {error_body[:200]}")

            resp_json = resp.json()

            # Debug: Log response details
            logger.debug(
                f"OpenAI Chat API Response | "
                f"Response Model: {resp_json.get('model')} | "
                f"Choices: {len(resp_json.get('choices', []))} | "
                f"Usage: {resp_json.get('usage')}"
            )

            # Extract assistant message and token counts
            if "choices" in resp_json and len(resp_json["choices"]) > 0:
                choice = resp_json["choices"][0]
                content = choice.get("message", {}).get("content", "")

                # Extract token usage
                usage = resp_json.get("usage", {})
                prompt_tokens = usage.get("prompt_tokens", 0)
                completion_tokens = usage.get("completion_tokens", 0)

                logger.debug(
                    "Token counts extracted",
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens
                )

                return content, prompt_tokens, completion_tokens
            else:
                logger.error("Invalid OpenAI response format", response=resp_json)
                raise OpenAIAPIError("Invalid API response format: no choices found")

        except requests.exceptions.RequestException as e:
            logger.error("OpenAI API Network Error", error=str(e), error_type=type(e).__name__)
            raise OpenAIAPIError(f"Network Error: {e}")
        except Exception as e:
            logger.error(
                "Unexpected OpenAI API error",
                error_type=type(e).__name__,
                error=str(e),
                stacktrace=traceback.format_exc()
            )
            raise OpenAIAPIError(f"Unexpected Error: {e}")

    def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Get list of available OpenAI Chat models from configuration.

        Returns:
            List of model dictionaries with name and context_window
        """
        from config.settings import OPENAI_CHAT_MODELS

        # Parse configured models
        model_names = [m.strip() for m in OPENAI_CHAT_MODELS.split(",")]

        # Define context windows for known models
        context_windows = {
            # GPT-5 Series
            "gpt-5": 200000,
            "gpt-5-pro": 200000,
            "gpt-5-mini": 200000,
            "gpt-5-nano": 200000,
            "gpt-5-codex": 200000,
            "gpt-5-chat-latest": 200000,
            # GPT-4.1 Series
            "gpt-4.1": 128000,
            "gpt-4.1-mini": 128000,
            "gpt-4.1-nano": 128000,
            # GPT-4o Series
            "gpt-4o": 128000,
            "gpt-4o-mini": 128000,
            # GPT-4 Series
            "gpt-4-turbo": 128000,
            "gpt-4": 8192,
            # GPT-3.5 Series
            "gpt-3.5-turbo": 16385,
        }

        models = []
        for model_name in model_names:
            models.append({
                "name": model_name,
                "context_window": context_windows.get(model_name, 8192)  # Default to 8k
            })

        return models


class OpenAIAPIError(Exception):
    """Custom exception for OpenAI API errors."""
    pass
