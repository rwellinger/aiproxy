"""Ollama Controller - Proxy for Ollama API calls."""

from typing import Any

import requests

from config.model_context_windows import get_context_window_size
from config.settings import OLLAMA_CHAT_MODELS, OLLAMA_DEFAULT_MODEL, OLLAMA_TIMEOUT, OLLAMA_URL
from utils.logger import logger


class OllamaController:
    """Controller for proxying Ollama API requests."""

    @staticmethod
    def get_models() -> tuple[dict[str, Any], int]:
        """
        Get available Ollama models.

        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            api_url = f"{OLLAMA_URL}/api/tags"
            logger.debug("Fetching Ollama models", api_url=api_url)

            response = requests.get(api_url, timeout=OLLAMA_TIMEOUT)
            response.raise_for_status()

            data = response.json()
            logger.info("Ollama models fetched successfully", model_count=len(data.get("models", [])))

            return data, 200

        except requests.exceptions.Timeout:
            logger.error("Ollama API timeout", url=OLLAMA_URL)
            return {"error": "Ollama API timeout"}, 504

        except requests.exceptions.ConnectionError:
            logger.error("Ollama API connection failed", url=OLLAMA_URL)
            return {"error": "Cannot connect to Ollama API"}, 503

        except requests.exceptions.RequestException as e:
            logger.error("Ollama API request failed", error=str(e))
            return {"error": f"Ollama API error: {str(e)}"}, 500

        except Exception as e:
            logger.error("Unexpected error in get_models", error=str(e))
            return {"error": f"Unexpected error: {str(e)}"}, 500

    @staticmethod
    def get_available_chat_models() -> tuple[dict[str, Any], int]:
        """
        Get available Ollama chat models based on configuration.

        Behavior:
        - OLLAMA_CHAT_MODELS empty: Fetch all models from Ollama server
        - OLLAMA_CHAT_MODELS set: Return only whitelisted models (static)

        Returns:
            Tuple of (response_data, status_code)
            Response format: {"models": [{"name": str, "context_window": int, "is_default": bool}]}
        """
        try:
            # Parse configured models (empty string = fetch all from server)
            configured_models = [m.strip() for m in OLLAMA_CHAT_MODELS.split(",") if m.strip()]

            if configured_models:
                # Static mode: Use whitelist from configuration
                logger.info("Using static Ollama model list", model_count=len(configured_models))
                models = []
                for model_name in configured_models:
                    models.append(
                        {
                            "name": model_name,
                            "context_window": get_context_window_size(model_name),
                            "is_default": model_name == OLLAMA_DEFAULT_MODEL,
                        }
                    )
            else:
                # Dynamic mode: Fetch all models from Ollama server
                logger.info("Fetching dynamic Ollama model list from server")
                api_url = f"{OLLAMA_URL}/api/tags"
                response = requests.get(api_url, timeout=OLLAMA_TIMEOUT)
                response.raise_for_status()

                data = response.json()
                server_models = data.get("models", [])

                models = []
                for model in server_models:
                    model_name = model.get("name", "")
                    if model_name:
                        models.append(
                            {
                                "name": model_name,
                                "context_window": get_context_window_size(model_name),
                                "is_default": model_name == OLLAMA_DEFAULT_MODEL,
                            }
                        )

                logger.info("Ollama models fetched successfully", model_count=len(models))

            return {"models": models}, 200

        except requests.exceptions.Timeout:
            logger.error("Ollama API timeout", url=OLLAMA_URL)
            return {"error": "Ollama API timeout"}, 504

        except requests.exceptions.ConnectionError:
            logger.error("Ollama API connection failed", url=OLLAMA_URL)
            return {"error": "Cannot connect to Ollama API"}, 503

        except requests.exceptions.RequestException as e:
            logger.error("Ollama API request failed", error=str(e))
            return {"error": f"Ollama API error: {str(e)}"}, 500

        except Exception as e:
            logger.error("Unexpected error in get_available_chat_models", error=str(e))
            return {"error": f"Unexpected error: {str(e)}"}, 500
