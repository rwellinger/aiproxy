"""Unit tests for OllamaController"""

from unittest.mock import MagicMock

import pytest
import requests

from api.controllers.ollama_controller import OllamaController


@pytest.mark.unit
class TestOllamaControllerGetModels:
    """Test OllamaController.get_models method"""

    def test_get_models_success(self, mocker, sample_ollama_models_response):
        """Test successful model retrieval"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_ollama_models_response
        mock_response.raise_for_status.return_value = None

        mocker.patch("requests.get", return_value=mock_response)

        controller = OllamaController()
        result, status_code = controller.get_models()

        assert status_code == 200
        assert "models" in result
        assert len(result["models"]) == 2
        assert result["models"][0]["name"] == "llama3.2:3b"

    def test_get_models_timeout(self, mocker):
        """Test model retrieval with timeout"""
        mocker.patch("requests.get", side_effect=requests.exceptions.Timeout("Timeout"))

        controller = OllamaController()
        result, status_code = controller.get_models()

        assert status_code == 504
        assert "error" in result
        assert "timeout" in result["error"].lower()

    def test_get_models_connection_error(self, mocker):
        """Test model retrieval with connection error"""
        mocker.patch("requests.get", side_effect=requests.exceptions.ConnectionError("Connection failed"))

        controller = OllamaController()
        result, status_code = controller.get_models()

        assert status_code == 503
        assert "error" in result
        assert "connect" in result["error"].lower()

    def test_get_models_request_exception(self, mocker):
        """Test model retrieval with generic request exception"""
        mocker.patch("requests.get", side_effect=requests.exceptions.RequestException("Request failed"))

        controller = OllamaController()
        result, status_code = controller.get_models()

        assert status_code == 500
        assert "error" in result

    def test_get_models_unexpected_error(self, mocker):
        """Test model retrieval with unexpected error"""
        mocker.patch("requests.get", side_effect=Exception("Unexpected error"))

        controller = OllamaController()
        result, status_code = controller.get_models()

        assert status_code == 500
        assert "error" in result


@pytest.mark.unit
class TestOllamaControllerGetChatModels:
    """Test OllamaController.get_available_chat_models method"""

    def test_get_chat_models_static_list(self, mocker):
        """Test getting chat models from static configuration"""
        # Patch settings at import location in controller module
        mocker.patch("api.controllers.ollama_controller.OLLAMA_CHAT_MODELS", "llama3.2:3b,mistral:7b")
        mocker.patch("api.controllers.ollama_controller.OLLAMA_DEFAULT_MODEL", "llama3.2:3b")

        # Mock context window function
        def mock_context_window(model_name):
            return 4096 if "llama" in model_name else 8192

        mocker.patch("api.controllers.ollama_controller.get_context_window_size", side_effect=mock_context_window)

        controller = OllamaController()
        result, status_code = controller.get_available_chat_models()

        assert status_code == 200
        assert "models" in result
        assert len(result["models"]) == 2
        assert result["models"][0]["name"] == "llama3.2:3b"
        assert result["models"][0]["is_default"] is True
        assert result["models"][0]["context_window"] == 4096
        assert result["models"][1]["name"] == "mistral:7b"
        assert result["models"][1]["is_default"] is False

    def test_get_chat_models_dynamic_from_server(self, mocker, sample_ollama_models_response, mock_env_vars):
        """Test getting chat models dynamically from Ollama server"""
        # Empty config = fetch from server
        mocker.patch("config.settings.OLLAMA_CHAT_MODELS", "")
        mocker.patch("config.settings.OLLAMA_DEFAULT_MODEL", "llama3.2:3b")

        # Mock HTTP response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_ollama_models_response
        mock_response.raise_for_status.return_value = None

        mocker.patch("requests.get", return_value=mock_response)

        # Mock context window function
        mocker.patch("api.controllers.ollama_controller.get_context_window_size", return_value=4096)

        controller = OllamaController()
        result, status_code = controller.get_available_chat_models()

        assert status_code == 200
        assert "models" in result
        assert len(result["models"]) == 2

    def test_get_chat_models_dynamic_timeout(self, mocker, mock_env_vars):
        """Test dynamic model fetch with timeout"""
        mocker.patch("config.settings.OLLAMA_CHAT_MODELS", "")
        mocker.patch("requests.get", side_effect=requests.exceptions.Timeout("Timeout"))

        controller = OllamaController()
        result, status_code = controller.get_available_chat_models()

        assert status_code == 504
        assert "error" in result

    def test_get_chat_models_dynamic_connection_error(self, mocker, mock_env_vars):
        """Test dynamic model fetch with connection error"""
        mocker.patch("config.settings.OLLAMA_CHAT_MODELS", "")
        mocker.patch("requests.get", side_effect=requests.exceptions.ConnectionError("Connection failed"))

        controller = OllamaController()
        result, status_code = controller.get_available_chat_models()

        assert status_code == 503
        assert "error" in result

    def test_get_chat_models_empty_whitelist(self, mocker, mock_env_vars):
        """Test with empty whitelist (should fetch from server)"""
        mocker.patch("config.settings.OLLAMA_CHAT_MODELS", "   ")  # Only whitespace

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"models": []}
        mock_response.raise_for_status.return_value = None

        mocker.patch("requests.get", return_value=mock_response)
        mocker.patch("api.controllers.ollama_controller.get_context_window_size", return_value=2048)

        controller = OllamaController()
        result, status_code = controller.get_available_chat_models()

        assert status_code == 200
        assert "models" in result
        assert len(result["models"]) == 0  # Empty list from server

    def test_get_chat_models_whitelist_with_spaces(self, mocker):
        """Test whitelist with spaces in model names"""
        mocker.patch("api.controllers.ollama_controller.OLLAMA_CHAT_MODELS", " llama3.2:3b , mistral:7b ")
        mocker.patch("api.controllers.ollama_controller.OLLAMA_DEFAULT_MODEL", "llama3.2:3b")
        mocker.patch("api.controllers.ollama_controller.get_context_window_size", return_value=4096)

        controller = OllamaController()
        result, status_code = controller.get_available_chat_models()

        assert status_code == 200
        assert len(result["models"]) == 2
        # Verify spaces were stripped
        assert all(" " not in model["name"] for model in result["models"])
