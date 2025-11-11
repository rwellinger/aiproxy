"""Tests for PromptTemplateValidator - Business logic unit tests"""

import pytest

from business.prompt_template_validator import (
    PromptTemplateValidationError,
    PromptTemplateValidator,
)


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


class TestValidationErrorException:
    """Test PromptTemplateValidationError exception"""

    def test_validation_error_is_exception(self):
        """PromptTemplateValidationError is an Exception"""
        assert issubclass(PromptTemplateValidationError, Exception)

    def test_validation_error_can_be_raised(self):
        """PromptTemplateValidationError can be raised with message"""
        with pytest.raises(PromptTemplateValidationError, match="Test error message"):
            raise PromptTemplateValidationError("Test error message")
