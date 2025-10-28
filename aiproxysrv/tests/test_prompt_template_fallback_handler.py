"""Tests for PromptTemplateFallbackHandler - Business logic unit tests"""

from unittest.mock import Mock

from business.prompt_template_fallback_handler import (
    FallbackReason,
    PromptTemplateFallbackHandler,
)


class TestResolveModel:
    """Test model resolution with fallback tracking"""

    def test_resolve_model_from_template(self):
        """Template has valid model - no fallback"""
        template = Mock(model="llama3.2:3b", id=1)

        model, used_fallback = PromptTemplateFallbackHandler.resolve_model(template, "test_cat", "test_action")

        assert model == "llama3.2:3b"
        assert used_fallback is False

    def test_resolve_model_fallback_none(self):
        """Template.model is None - uses fallback"""
        template = Mock(model=None, id=42)

        model, used_fallback = PromptTemplateFallbackHandler.resolve_model(template, "lyrics", "generate")

        assert model == "llama3.2:3b"  # Default
        assert used_fallback is True

    def test_resolve_model_fallback_empty_string(self):
        """Template.model is empty string - uses fallback"""
        template = Mock(model="", id=42)

        model, used_fallback = PromptTemplateFallbackHandler.resolve_model(template, "music", "enhance")

        assert model == "llama3.2:3b"
        assert used_fallback is True

    def test_resolve_model_fallback_whitespace(self):
        """Template.model is whitespace only - uses fallback"""
        template = Mock(model="   ", id=42)

        model, used_fallback = PromptTemplateFallbackHandler.resolve_model(template, "image", "enhance")

        assert model == "llama3.2:3b"
        assert used_fallback is True


class TestResolveTemperature:
    """Test temperature resolution with fallback tracking"""

    def test_resolve_temperature_from_template(self):
        """Template has valid temperature - no fallback"""
        template = Mock(temperature=0.8, id=1)

        temp, used_fallback = PromptTemplateFallbackHandler.resolve_temperature(template, "test_cat", "test_action")

        assert temp == 0.8
        assert used_fallback is False

    def test_resolve_temperature_zero_valid(self):
        """Temperature 0.0 is valid - no fallback"""
        template = Mock(temperature=0.0, id=1)

        temp, used_fallback = PromptTemplateFallbackHandler.resolve_temperature(template, "test_cat", "test_action")

        assert temp == 0.0
        assert used_fallback is False

    def test_resolve_temperature_fallback_none(self):
        """Template.temperature is None - uses fallback"""
        template = Mock(temperature=None, id=42)

        temp, used_fallback = PromptTemplateFallbackHandler.resolve_temperature(template, "lyrics", "generate")

        assert temp == 0.7  # Default
        assert used_fallback is True

    def test_resolve_temperature_one_valid(self):
        """Temperature 1.0 is valid - no fallback"""
        template = Mock(temperature=1.0, id=1)

        temp, used_fallback = PromptTemplateFallbackHandler.resolve_temperature(template, "test_cat", "test_action")

        assert temp == 1.0
        assert used_fallback is False


class TestResolveMaxTokens:
    """Test max_tokens resolution with fallback tracking"""

    def test_resolve_max_tokens_from_template(self):
        """Template has valid max_tokens - no fallback"""
        template = Mock(max_tokens=1000, id=1)

        tokens, used_fallback = PromptTemplateFallbackHandler.resolve_max_tokens(template, "test_cat", "test_action")

        assert tokens == 1000
        assert used_fallback is False

    def test_resolve_max_tokens_zero_valid(self):
        """max_tokens 0 is technically valid (though unusual)"""
        template = Mock(max_tokens=0, id=1)

        tokens, used_fallback = PromptTemplateFallbackHandler.resolve_max_tokens(template, "test_cat", "test_action")

        assert tokens == 0
        assert used_fallback is False

    def test_resolve_max_tokens_fallback_none(self):
        """Template.max_tokens is None - uses fallback"""
        template = Mock(max_tokens=None, id=42)

        tokens, used_fallback = PromptTemplateFallbackHandler.resolve_max_tokens(template, "lyrics", "generate")

        assert tokens == 2048  # Default
        assert used_fallback is True


class TestResolveAllParameters:
    """Test comprehensive parameter resolution with fallback tracking"""

    def test_all_parameters_complete_no_fallback(self):
        """Template has all parameters - no fallbacks"""
        template = Mock(model="llama3.2", temperature=0.8, max_tokens=1000, id=1)

        result = PromptTemplateFallbackHandler.resolve_all_parameters(template, "test_cat", "test_action")

        assert result["model"] == "llama3.2"
        assert result["temperature"] == 0.8
        assert result["max_tokens"] == 1000
        assert result["fallback_count"] == 0
        assert result["fallbacks_used"]["model"] is False
        assert result["fallbacks_used"]["temperature"] is False
        assert result["fallbacks_used"]["max_tokens"] is False

    def test_all_parameters_missing_all_fallbacks(self):
        """Template has no parameters - all fallbacks"""
        template = Mock(model=None, temperature=None, max_tokens=None, id=42)

        result = PromptTemplateFallbackHandler.resolve_all_parameters(template, "lyrics", "generate")

        assert result["model"] == "llama3.2:3b"
        assert result["temperature"] == 0.7
        assert result["max_tokens"] == 2048
        assert result["fallback_count"] == 3
        assert result["fallbacks_used"]["model"] is True
        assert result["fallbacks_used"]["temperature"] is True
        assert result["fallbacks_used"]["max_tokens"] is True

    def test_partial_fallbacks_model_only(self):
        """Only model missing - partial fallback"""
        template = Mock(model=None, temperature=0.9, max_tokens=1500, id=42)

        result = PromptTemplateFallbackHandler.resolve_all_parameters(template, "image", "enhance")

        assert result["fallback_count"] == 1
        assert result["fallbacks_used"]["model"] is True
        assert result["fallbacks_used"]["temperature"] is False
        assert result["fallbacks_used"]["max_tokens"] is False

    def test_partial_fallbacks_temperature_only(self):
        """Only temperature missing - partial fallback"""
        template = Mock(model="llama3.2", temperature=None, max_tokens=1500, id=42)

        result = PromptTemplateFallbackHandler.resolve_all_parameters(template, "music", "enhance")

        assert result["fallback_count"] == 1
        assert result["fallbacks_used"]["model"] is False
        assert result["fallbacks_used"]["temperature"] is True
        assert result["fallbacks_used"]["max_tokens"] is False

    def test_partial_fallbacks_max_tokens_only(self):
        """Only max_tokens missing - partial fallback"""
        template = Mock(model="llama3.2", temperature=0.9, max_tokens=None, id=42)

        result = PromptTemplateFallbackHandler.resolve_all_parameters(template, "lyrics", "translate")

        assert result["fallback_count"] == 1
        assert result["fallbacks_used"]["model"] is False
        assert result["fallbacks_used"]["temperature"] is False
        assert result["fallbacks_used"]["max_tokens"] is True

    def test_partial_fallbacks_two_missing(self):
        """Two parameters missing - 2 fallbacks"""
        template = Mock(model=None, temperature=None, max_tokens=1500, id=42)

        result = PromptTemplateFallbackHandler.resolve_all_parameters(template, "title", "generate")

        assert result["fallback_count"] == 2
        assert result["fallbacks_used"]["model"] is True
        assert result["fallbacks_used"]["temperature"] is True
        assert result["fallbacks_used"]["max_tokens"] is False


class TestFallbackReasons:
    """Test FallbackReason constants for structured logging"""

    def test_fallback_reasons_defined(self):
        """Verify all fallback reason constants are defined"""
        assert FallbackReason.TEMPLATE_NOT_FOUND == "template_not_found"
        assert FallbackReason.MODEL_MISSING == "model_missing"
        assert FallbackReason.MODEL_EMPTY == "model_empty"
        assert FallbackReason.TEMPERATURE_MISSING == "temperature_missing"
        assert FallbackReason.MAX_TOKENS_MISSING == "max_tokens_missing"


class TestDefaultValues:
    """Test default value constants"""

    def test_default_values_defined(self):
        """Verify default values are sensible"""
        assert PromptTemplateFallbackHandler.DEFAULT_MODEL == "llama3.2:3b"
        assert PromptTemplateFallbackHandler.DEFAULT_TEMPERATURE == 0.7
        assert PromptTemplateFallbackHandler.DEFAULT_MAX_TOKENS == 2048

    def test_default_temperature_range(self):
        """Default temperature should be between 0 and 1"""
        temp = PromptTemplateFallbackHandler.DEFAULT_TEMPERATURE
        assert 0.0 <= temp <= 1.0

    def test_default_max_tokens_positive(self):
        """Default max_tokens should be positive"""
        tokens = PromptTemplateFallbackHandler.DEFAULT_MAX_TOKENS
        assert tokens > 0
