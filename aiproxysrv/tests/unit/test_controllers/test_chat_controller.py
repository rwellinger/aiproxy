"""Unit tests for ChatController"""

from unittest.mock import MagicMock

import pytest
import requests

from api.controllers.chat_controller import ChatController, OllamaAPIError


@pytest.mark.unit
class TestChatControllerGenerateChat:
    """Test ChatController.generate_chat method"""

    def test_generate_chat_success(self, mocker, sample_ollama_response, mock_env_vars):
        """Test successful chat generation"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_ollama_response
        mock_response.raise_for_status.return_value = None

        mocker.patch("requests.post", return_value=mock_response)

        controller = ChatController()
        result, status_code = controller.generate_chat(
            model="llama3.2:3b",
            pre_condition="You are helpful",
            prompt="Hello",
            post_condition="Be brief",
            temperature=0.7,
            max_tokens=100,
        )

        assert status_code == 200
        assert "response" in result
        assert result["response"] == "This is a test response"
        # Verify context was cleaned
        assert "context" not in result

    def test_generate_chat_missing_model(self, mocker, mock_env_vars):
        """Test chat generation with missing model"""
        controller = ChatController()
        result, status_code = controller.generate_chat(
            model="",
            pre_condition="",
            prompt="Hello",
            post_condition="",
        )

        assert status_code == 400
        assert "error" in result
        assert "Missing model or prompt" in result["error"]

    def test_generate_chat_missing_prompt(self, mocker, mock_env_vars):
        """Test chat generation with missing prompt"""
        controller = ChatController()
        result, status_code = controller.generate_chat(
            model="llama3.2:3b",
            pre_condition="",
            prompt="",
            post_condition="",
        )

        assert status_code == 400
        assert "error" in result

    def test_generate_chat_network_error(self, mocker, mock_env_vars):
        """Test chat generation with network error"""
        mocker.patch("requests.post", side_effect=requests.exceptions.ConnectionError("Network error"))

        controller = ChatController()
        result, status_code = controller.generate_chat(
            model="llama3.2:3b",
            pre_condition="",
            prompt="Hello",
            post_condition="",
        )

        assert status_code == 500
        assert "error" in result
        assert "Ollama API Error" in result["error"]

    def test_generate_chat_timeout(self, mocker, mock_env_vars):
        """Test chat generation with timeout"""
        mocker.patch("requests.post", side_effect=requests.exceptions.Timeout("Timeout"))

        controller = ChatController()
        result, status_code = controller.generate_chat(
            model="llama3.2:3b",
            pre_condition="",
            prompt="Hello",
            post_condition="",
        )

        assert status_code == 500
        assert "error" in result

    def test_generate_chat_http_error(self, mocker, mock_env_vars):
        """Test chat generation with HTTP error response"""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal server error"
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("HTTP Error")

        mocker.patch("requests.post", return_value=mock_response)

        controller = ChatController()
        result, status_code = controller.generate_chat(
            model="llama3.2:3b",
            pre_condition="",
            prompt="Hello",
            post_condition="",
        )

        assert status_code == 500
        assert "error" in result


@pytest.mark.unit
class TestChatControllerPromptBuilding:
    """Test ChatController prompt construction"""

    def test_prompt_building_full(self, mocker, sample_ollama_response, mock_env_vars):
        """Test full prompt with all parts"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_ollama_response
        mock_response.raise_for_status.return_value = None

        mock_post = mocker.patch("requests.post", return_value=mock_response)

        controller = ChatController()
        controller.generate_chat(
            model="llama3.2:3b",
            pre_condition="You are helpful",
            prompt="Translate this",
            post_condition="Use JSON",
            temperature=0.3,
            max_tokens=50,
        )

        # Verify the prompt was constructed correctly
        call_args = mock_post.call_args
        payload = call_args[1]["json"]

        assert "[INSTRUCTION]" in payload["prompt"]
        assert "You are helpful" in payload["prompt"]
        assert "[USER]" in payload["prompt"]
        assert "Translate this" in payload["prompt"]
        assert "[FORMAT]" in payload["prompt"]
        assert "Use JSON" in payload["prompt"]

    def test_prompt_building_minimal(self, mocker, sample_ollama_response, mock_env_vars):
        """Test minimal prompt with only required fields"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_ollama_response
        mock_response.raise_for_status.return_value = None

        mock_post = mocker.patch("requests.post", return_value=mock_response)

        controller = ChatController()
        controller.generate_chat(
            model="llama3.2:3b",
            pre_condition="",
            prompt="Hello",
            post_condition="",
        )

        # Verify the prompt structure exists even with empty conditions
        call_args = mock_post.call_args
        payload = call_args[1]["json"]

        assert "[INSTRUCTION]" in payload["prompt"]
        assert "[USER]" in payload["prompt"]
        assert "[FORMAT]" in payload["prompt"]
        assert "Hello" in payload["prompt"]


@pytest.mark.unit
class TestChatControllerAPICall:
    """Test ChatController._call_ollama_api method"""

    def test_call_ollama_api_success(self, mocker, sample_ollama_response, mock_env_vars):
        """Test successful API call"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_ollama_response
        mock_response.raise_for_status.return_value = None

        mocker.patch("requests.post", return_value=mock_response)

        controller = ChatController()
        result = controller._call_ollama_api(
            model="llama3.2:3b",
            prompt="Test prompt",
            temperature=0.7,
            max_tokens=100,
        )

        assert result == sample_ollama_response
        assert "response" in result

    def test_call_ollama_api_invalid_json_response(self, mocker, mock_env_vars):
        """Test API call with invalid JSON response"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "Not JSON"
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.raise_for_status.return_value = None

        mocker.patch("requests.post", return_value=mock_response)

        controller = ChatController()

        with pytest.raises(OllamaAPIError, match="Invalid API response format"):
            controller._call_ollama_api(
                model="llama3.2:3b",
                prompt="Test",
                temperature=0.7,
                max_tokens=100,
            )

    def test_call_ollama_api_request_exception(self, mocker, mock_env_vars):
        """Test API call with request exception"""
        mocker.patch("requests.post", side_effect=requests.exceptions.RequestException("Error"))

        controller = ChatController()

        with pytest.raises(OllamaAPIError, match="Network Error"):
            controller._call_ollama_api(
                model="llama3.2:3b",
                prompt="Test",
                temperature=0.7,
                max_tokens=100,
            )


@pytest.mark.unit
class TestChatControllerResponseCleaning:
    """Test ChatController._clean_ollama_response method"""

    def test_clean_response_removes_context(self, sample_ollama_response):
        """Test that context field is removed from response"""
        controller = ChatController()

        # Verify sample has context
        assert "context" in sample_ollama_response

        cleaned = controller._clean_ollama_response(sample_ollama_response)

        assert "context" not in cleaned
        assert "response" in cleaned
        assert cleaned["response"] == sample_ollama_response["response"]

    def test_clean_response_preserves_other_fields(self, sample_ollama_response):
        """Test that other fields are preserved"""
        controller = ChatController()

        cleaned = controller._clean_ollama_response(sample_ollama_response)

        assert cleaned["model"] == sample_ollama_response["model"]
        assert cleaned["response"] == sample_ollama_response["response"]
        assert cleaned["done"] == sample_ollama_response["done"]

    def test_clean_response_no_context(self):
        """Test cleaning response without context field"""
        controller = ChatController()

        response_without_context = {
            "model": "llama3.2:3b",
            "response": "Test response",
            "done": True,
        }

        cleaned = controller._clean_ollama_response(response_without_context)

        # Should not raise error
        assert cleaned == response_without_context

    def test_clean_response_does_not_modify_original(self, sample_ollama_response):
        """Test that cleaning creates a copy and doesn't modify original"""
        controller = ChatController()

        original_keys = set(sample_ollama_response.keys())
        cleaned = controller._clean_ollama_response(sample_ollama_response)

        # Original should still have context
        assert "context" in sample_ollama_response
        assert set(sample_ollama_response.keys()) == original_keys

        # Cleaned should not have context
        assert "context" not in cleaned


@pytest.mark.unit
class TestOllamaAPIError:
    """Test OllamaAPIError exception"""

    def test_error_instantiation(self):
        """Test creating OllamaAPIError"""
        error = OllamaAPIError("Test error message")

        assert str(error) == "Test error message"
        assert isinstance(error, Exception)

    def test_error_with_dict(self):
        """Test OllamaAPIError with dict message"""
        error_dict = {"error": "Model not found", "status": 404}
        error = OllamaAPIError(error_dict)

        assert str(error) == str(error_dict)
