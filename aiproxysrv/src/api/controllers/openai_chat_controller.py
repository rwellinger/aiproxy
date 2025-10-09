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
            "temperature": temperature,
        }

        if max_tokens:
            payload["max_tokens"] = max_tokens

        # Set headers with API key
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        logger.debug("Calling OpenAI Chat API", api_url=api_url, model=model)

        try:
            resp = requests.post(
                api_url,
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            resp.raise_for_status()

            resp_json = resp.json()
            logger.debug("OpenAI Chat API response received")

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
                raise OpenAIAPIError("Invalid API response format: no choices found")

        except requests.exceptions.RequestException as e:
            logger.error("OpenAI API Network Error", error=str(e))
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
            "gpt-4o": 128000,
            "gpt-4o-mini": 128000,
            "gpt-5": 128000,  # Assuming same as gpt-4o
            "gpt-5-mini": 128000,  # Assuming same as gpt-4o-mini
            "gpt-4-turbo": 128000,
            "gpt-4": 8192,
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
