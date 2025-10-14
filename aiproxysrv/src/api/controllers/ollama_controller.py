"""Ollama Controller - Proxy for Ollama API calls."""

from typing import Any

import requests

from config.settings import OLLAMA_TIMEOUT, OLLAMA_URL
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
