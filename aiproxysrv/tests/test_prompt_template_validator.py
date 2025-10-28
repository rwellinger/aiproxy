"""Tests for PromptTemplateValidator - Business logic unit tests"""

import pytest

from business.prompt_template_validator import (
    PromptTemplateValidationError,
    PromptTemplateValidator,
)


class TestValidateVersionIncrement:
    """Test version increment logic (auto-increment by 0.1)"""

    def test_version_increment_from_none(self):
        """None version starts at 1.0"""
        assert PromptTemplateValidator.validate_version_increment(None) == "1.0"

    def test_version_increment_from_1_0(self):
        """1.0 increments to 1.1"""
        assert PromptTemplateValidator.validate_version_increment("1.0") == "1.1"

    def test_version_increment_from_2_5(self):
        """2.5 increments to 2.6"""
        assert PromptTemplateValidator.validate_version_increment("2.5") == "2.6"

    def test_version_increment_from_9_9(self):
        """9.9 increments to 10.0"""
        assert PromptTemplateValidator.validate_version_increment("9.9") == "10.0"

    def test_version_increment_from_0_0(self):
        """0.0 increments to 0.1"""
        assert PromptTemplateValidator.validate_version_increment("0.0") == "0.1"

    def test_version_increment_invalid_string(self):
        """Invalid string defaults to 1.0"""
        assert PromptTemplateValidator.validate_version_increment("invalid") == "1.0"

    def test_version_increment_empty_string(self):
        """Empty string defaults to 1.0"""
        assert PromptTemplateValidator.validate_version_increment("") == "1.0"

    def test_version_increment_whitespace(self):
        """Whitespace string defaults to 1.0"""
        assert PromptTemplateValidator.validate_version_increment("   ") == "1.0"

    def test_version_increment_non_numeric(self):
        """Non-numeric string defaults to 1.0"""
        assert PromptTemplateValidator.validate_version_increment("abc") == "1.0"

    def test_version_increment_large_number(self):
        """Large version number increments correctly"""
        assert PromptTemplateValidator.validate_version_increment("99.9") == "100.0"

    def test_version_increment_integer_string(self):
        """Integer string (no decimal) increments correctly"""
        assert PromptTemplateValidator.validate_version_increment("5") == "5.1"


class TestValidateCategoryActionFormat:
    """Test category and action validation"""

    def test_valid_category_and_action(self):
        """Valid category and action - no exception"""
        PromptTemplateValidator.validate_category_action_format("lyrics", "generate")
        # No assertion needed - should not raise

    def test_empty_category_raises(self):
        """Empty category raises exception"""
        with pytest.raises(PromptTemplateValidationError, match="Category is required"):
            PromptTemplateValidator.validate_category_action_format("", "generate")

    def test_empty_action_raises(self):
        """Empty action raises exception"""
        with pytest.raises(PromptTemplateValidationError, match="Action is required"):
            PromptTemplateValidator.validate_category_action_format("lyrics", "")

    def test_whitespace_category_raises(self):
        """Whitespace-only category raises exception"""
        with pytest.raises(PromptTemplateValidationError, match="Category is required"):
            PromptTemplateValidator.validate_category_action_format("   ", "generate")

    def test_whitespace_action_raises(self):
        """Whitespace-only action raises exception"""
        with pytest.raises(PromptTemplateValidationError, match="Action is required"):
            PromptTemplateValidator.validate_category_action_format("lyrics", "   ")

    def test_both_empty_raises(self):
        """Both empty raises exception (category first)"""
        with pytest.raises(PromptTemplateValidationError, match="Category is required"):
            PromptTemplateValidator.validate_category_action_format("", "")

    def test_various_valid_categories(self):
        """Various valid category/action combinations"""
        valid_pairs = [
            ("lyrics", "generate"),
            ("image", "enhance"),
            ("music", "translate"),
            ("title", "generate"),
            ("custom_category", "custom_action"),
        ]
        for category, action in valid_pairs:
            PromptTemplateValidator.validate_category_action_format(category, action)


class TestValidateTemperatureRange:
    """Test temperature range validation (0.0 - 2.0)"""

    def test_temperature_none_is_valid(self):
        """None temperature is valid (optional parameter)"""
        PromptTemplateValidator.validate_temperature_range(None)
        # No assertion needed - should not raise

    def test_temperature_0_0_is_valid(self):
        """Temperature 0.0 is valid"""
        PromptTemplateValidator.validate_temperature_range(0.0)

    def test_temperature_0_7_is_valid(self):
        """Temperature 0.7 is valid (common value)"""
        PromptTemplateValidator.validate_temperature_range(0.7)

    def test_temperature_1_0_is_valid(self):
        """Temperature 1.0 is valid"""
        PromptTemplateValidator.validate_temperature_range(1.0)

    def test_temperature_2_0_is_valid(self):
        """Temperature 2.0 is valid (upper bound)"""
        PromptTemplateValidator.validate_temperature_range(2.0)

    def test_temperature_negative_raises(self):
        """Negative temperature raises exception"""
        with pytest.raises(PromptTemplateValidationError, match="Temperature must be between 0.0 and 2.0"):
            PromptTemplateValidator.validate_temperature_range(-0.1)

    def test_temperature_too_high_raises(self):
        """Temperature > 2.0 raises exception"""
        with pytest.raises(PromptTemplateValidationError, match="Temperature must be between 0.0 and 2.0"):
            PromptTemplateValidator.validate_temperature_range(2.1)

    def test_temperature_way_too_high_raises(self):
        """Temperature way too high raises exception"""
        with pytest.raises(PromptTemplateValidationError, match="Temperature must be between 0.0 and 2.0"):
            PromptTemplateValidator.validate_temperature_range(10.0)

    def test_temperature_way_too_low_raises(self):
        """Temperature way too low raises exception"""
        with pytest.raises(PromptTemplateValidationError, match="Temperature must be between 0.0 and 2.0"):
            PromptTemplateValidator.validate_temperature_range(-5.0)


class TestValidateMaxTokensPositive:
    """Test max_tokens positive validation"""

    def test_max_tokens_none_is_valid(self):
        """None max_tokens is valid (optional parameter)"""
        PromptTemplateValidator.validate_max_tokens_positive(None)
        # No assertion needed - should not raise

    def test_max_tokens_1_is_valid(self):
        """max_tokens 1 is valid (minimum positive)"""
        PromptTemplateValidator.validate_max_tokens_positive(1)

    def test_max_tokens_100_is_valid(self):
        """max_tokens 100 is valid"""
        PromptTemplateValidator.validate_max_tokens_positive(100)

    def test_max_tokens_1000_is_valid(self):
        """max_tokens 1000 is valid (common value)"""
        PromptTemplateValidator.validate_max_tokens_positive(1000)

    def test_max_tokens_2048_is_valid(self):
        """max_tokens 2048 is valid (common value)"""
        PromptTemplateValidator.validate_max_tokens_positive(2048)

    def test_max_tokens_large_is_valid(self):
        """Large max_tokens is valid"""
        PromptTemplateValidator.validate_max_tokens_positive(100000)

    def test_max_tokens_zero_raises(self):
        """max_tokens 0 raises exception"""
        with pytest.raises(PromptTemplateValidationError, match="max_tokens must be positive"):
            PromptTemplateValidator.validate_max_tokens_positive(0)

    def test_max_tokens_negative_raises(self):
        """Negative max_tokens raises exception"""
        with pytest.raises(PromptTemplateValidationError, match="max_tokens must be positive"):
            PromptTemplateValidator.validate_max_tokens_positive(-1)

    def test_max_tokens_very_negative_raises(self):
        """Very negative max_tokens raises exception"""
        with pytest.raises(PromptTemplateValidationError, match="max_tokens must be positive"):
            PromptTemplateValidator.validate_max_tokens_positive(-1000)


class TestValidationErrorException:
    """Test PromptTemplateValidationError exception"""

    def test_validation_error_is_exception(self):
        """PromptTemplateValidationError is an Exception"""
        assert issubclass(PromptTemplateValidationError, Exception)

    def test_validation_error_can_be_raised(self):
        """PromptTemplateValidationError can be raised with message"""
        with pytest.raises(PromptTemplateValidationError, match="Test error message"):
            raise PromptTemplateValidationError("Test error message")
