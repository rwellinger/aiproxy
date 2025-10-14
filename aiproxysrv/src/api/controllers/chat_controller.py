"""Chat Controller - Handles business logic for chat operations"""

import traceback
from typing import Any

import requests

from config.settings import CHAT_DEBUG_LOGGING, OLLAMA_TIMEOUT, OLLAMA_URL
from utils.logger import logger


class ChatController:
    """Controller for chat generation via Ollama"""

    def generate_chat(
        self,
        model: str,
        pre_condition: str,
        prompt: str,
        post_condition: str,
        temperature: float = 0.3,
        max_tokens: int = 30,
    ) -> tuple[dict[str, Any], int]:
        """
        Generate chat response with Ollama

        Args:
            model: Ollama model to use (e.g. "llama3.2:3b")
            pre_condition: Text to prepend to prompt
            prompt: Main prompt text
            post_condition: Text to append to prompt
            temperature: Sampling temperature (default 0.3)
            max_tokens: Maximum tokens to generate (default 30)

        Returns:
            Tuple of (response_data, status_code)
        """
        # Validate input
        if not model or not prompt:
            return {"error": "Missing model or prompt"}, 400

        # Build full prompt optimized for gpt-oss:20b with clear instruction separation
        full_prompt = f"[INSTRUCTION] {pre_condition or ''} [USER] {prompt} [FORMAT] {post_condition or ''}"

        try:
            # Conditional logging based on CHAT_DEBUG_LOGGING
            if CHAT_DEBUG_LOGGING:
                logger.debug(
                    "Ollama Chat Request",
                    model=model,
                    pre_condition=pre_condition,
                    prompt=prompt,
                    post_condition=post_condition,
                    full_prompt=full_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            else:
                logger.info("Ollama chat request", model=model, prompt_length=len(prompt))

            # Call Ollama API
            response_data = self._call_ollama_api(model, full_prompt, temperature, max_tokens)

            # Clean response (remove context)
            cleaned_response = self._clean_ollama_response(response_data)

            if CHAT_DEBUG_LOGGING:
                logger.debug("Ollama Chat Response", model=model, response_data=cleaned_response)
            else:
                logger.info("Ollama chat completed", model=model)

            return cleaned_response, 200

        except OllamaAPIError as e:
            logger.error("Ollama API Error during chat generation", error=str(e), stacktrace=traceback.format_exc())
            return {"error": f"Ollama API Error: {e}"}, 500
        except Exception as e:
            logger.error(
                "Unexpected error in chat generation",
                error_type=type(e).__name__,
                error=str(e),
                stacktrace=traceback.format_exc(),
            )
            return {"error": f"Unexpected Error: {e}"}, 500

    def _call_ollama_api(self, model: str, prompt: str, temperature: float, max_tokens: int) -> dict[str, Any]:
        """Call Ollama API and return response"""
        headers = {"Content-Type": "application/json"}

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature, "max_tokens": max_tokens},
        }

        api_url = f"{OLLAMA_URL}/api/generate"

        if CHAT_DEBUG_LOGGING:
            logger.debug("Ollama API Request Details", api_url=api_url, full_payload=payload)
        else:
            logger.debug("Calling Ollama API", api_url=api_url, model=model)

        try:
            resp = requests.post(api_url, headers=headers, json=payload, timeout=OLLAMA_TIMEOUT)

            if CHAT_DEBUG_LOGGING:
                logger.debug("Ollama API response received", status_code=resp.status_code)

            resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(
                "Ollama API Network Error", error_type=type(e).__name__, error=str(e), stacktrace=traceback.format_exc()
            )
            raise OllamaAPIError(f"Network Error: {e}")
        except Exception as e:
            logger.error(
                "Unexpected Ollama API error",
                error_type=type(e).__name__,
                error=str(e),
                stacktrace=traceback.format_exc(),
            )
            raise OllamaAPIError(f"Network Error: {e}")

        if resp.status_code != 200:
            logger.error("Ollama API Error Response", status_code=resp.status_code, response_text=resp.text)
            try:
                error_data = resp.json()
                raise OllamaAPIError(error_data)
            except ValueError:
                raise OllamaAPIError(f"HTTP {resp.status_code}: {resp.text}")

        try:
            resp_json = resp.json()

            if CHAT_DEBUG_LOGGING:
                logger.debug("Ollama API raw response parsed", response_keys=list(resp_json.keys()))

            return resp_json
        except ValueError as e:
            logger.error(
                "Error parsing Ollama API response",
                error=str(e),
                response_text=resp.text,
                stacktrace=traceback.format_exc(),
            )
            raise OllamaAPIError(f"Invalid API response format: {e}")

    def _clean_ollama_response(self, response_data: dict[str, Any]) -> dict[str, Any]:
        """Clean Ollama response by removing context field"""
        cleaned = response_data.copy()

        # Remove context field if present
        if "context" in cleaned:
            del cleaned["context"]

        return cleaned


class OllamaAPIError(Exception):
    """Custom exception for Ollama API errors"""

    pass
