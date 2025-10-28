"""Ollama Controller - Proxy for Ollama API calls (uses Transformer Pattern)"""

from typing import Any

import requests

from business.ollama_model_transformer import OllamaModelTransformer
from config.settings import OLLAMA_CHAT_MODELS, OLLAMA_DEFAULT_MODEL, OLLAMA_TIMEOUT, OLLAMA_URL
from utils.logger import logger


class OllamaController:
    """Controller for proxying Ollama API requests (uses transformer for business logic)"""

    @staticmethod
    def get_models() -> tuple[dict[str, Any], int]:
        """
        Get available Ollama models (raw response from server).

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
            logger.error("Ollama API request failed", error=str(e), error_type=type(e).__name__)
            return {"error": f"Ollama API error: {str(e)}"}, 500

        except Exception as e:
            logger.error("Unexpected error in get_models", error=str(e), error_type=type(e).__name__)
            return {"error": f"Unexpected error: {str(e)}"}, 500

    @staticmethod
    def get_available_chat_models() -> tuple[dict[str, Any], int]:
        """
        Get available Ollama chat models based on configuration.

        Behavior (via transformer):
        - OLLAMA_CHAT_MODELS empty: Fetch all models from Ollama server
        - OLLAMA_CHAT_MODELS set: Return only whitelisted models (static)

        Returns:
            Tuple of (response_data, status_code)
            Response format: {"models": [{"name": str, "context_window": int, "is_default": bool}]}
        """
        try:
            # Business Logic: Parse configured models using transformer
            configured_models = OllamaModelTransformer.parse_configured_models(OLLAMA_CHAT_MODELS)

            if configured_models:
                # Static mode: Use whitelist from configuration
                logger.info("Using static Ollama model list", model_count=len(configured_models))

                # Business Logic: Build static model list using transformer
                models = OllamaModelTransformer.build_static_model_list(configured_models, OLLAMA_DEFAULT_MODEL)

            else:
                # Dynamic mode: Fetch all models from Ollama server
                logger.info("Fetching dynamic Ollama model list from server")
                api_url = f"{OLLAMA_URL}/api/tags"
                response = requests.get(api_url, timeout=OLLAMA_TIMEOUT)
                response.raise_for_status()

                data = response.json()
                server_models = data.get("models", [])

                # Business Logic: Transform server models using transformer
                models = OllamaModelTransformer.transform_server_models_to_frontend(server_models, OLLAMA_DEFAULT_MODEL)

                logger.info("Ollama models fetched and transformed", model_count=len(models))

            return {"models": models}, 200

        except requests.exceptions.Timeout:
            logger.error("Ollama API timeout", url=OLLAMA_URL)
            return {"error": "Ollama API timeout"}, 504

        except requests.exceptions.ConnectionError:
            logger.error("Ollama API connection failed", url=OLLAMA_URL)
            return {"error": "Cannot connect to Ollama API"}, 503

        except requests.exceptions.RequestException as e:
            logger.error("Ollama API request failed", error=str(e), error_type=type(e).__name__)
            return {"error": f"Ollama API error: {str(e)}"}, 500

        except Exception as e:
            logger.error("Unexpected error in get_available_chat_models", error=str(e), error_type=type(e).__name__)
            return {"error": f"Unexpected error: {str(e)}"}, 500
