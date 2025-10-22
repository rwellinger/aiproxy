"""Unit tests for ImageBusinessService (excluding DB operations)"""

import hashlib
from unittest.mock import MagicMock, patch

import pytest

from business.image_business_service import ImageBusinessService


@pytest.mark.unit
class TestImageBusinessService:
    """Test ImageBusinessService methods (non-DB)"""

    @pytest.fixture
    def service(self):
        """Create ImageBusinessService instance"""
        return ImageBusinessService()

    def test_generate_prompt_hash(self, service):
        """Test prompt hash generation"""
        prompt = "A beautiful sunset over the ocean"
        expected_hash = hashlib.md5(prompt.encode()).hexdigest()[:10]

        result = service._generate_prompt_hash(prompt)

        assert result == expected_hash
        assert len(result) == 10

    def test_generate_prompt_hash_deterministic(self, service):
        """Test that same prompt generates same hash"""
        prompt = "Test prompt"

        hash1 = service._generate_prompt_hash(prompt)
        hash2 = service._generate_prompt_hash(prompt)

        assert hash1 == hash2

    def test_generate_prompt_hash_different_prompts(self, service):
        """Test that different prompts generate different hashes"""
        prompt1 = "First prompt"
        prompt2 = "Second prompt"

        hash1 = service._generate_prompt_hash(prompt1)
        hash2 = service._generate_prompt_hash(prompt2)

        assert hash1 != hash2

    def test_validate_generation_request_valid(self, service):
        """Test validation with valid parameters"""
        # Should not raise
        service._validate_generation_request("valid prompt", "1024x1024")

    def test_validate_generation_request_empty_prompt(self, service):
        """Test validation fails with empty prompt"""
        from business.image_business_service import ImageGenerationError

        with pytest.raises(ImageGenerationError, match="Prompt is required"):
            service._validate_generation_request("", "1024x1024")

    def test_validate_generation_request_whitespace_prompt(self, service):
        """Test validation fails with whitespace-only prompt"""
        from business.image_business_service import ImageGenerationError

        with pytest.raises(ImageGenerationError, match="Prompt is required"):
            service._validate_generation_request("   ", "1024x1024")

    def test_validate_generation_request_none_prompt(self, service):
        """Test validation fails with None prompt"""
        from business.image_business_service import ImageGenerationError

        with pytest.raises(ImageGenerationError, match="Prompt is required"):
            service._validate_generation_request(None, "1024x1024")

    def test_validate_generation_request_empty_size(self, service):
        """Test validation fails with empty size"""
        from business.image_business_service import ImageGenerationError

        with pytest.raises(ImageGenerationError, match="Size is required"):
            service._validate_generation_request("valid prompt", "")

    def test_validate_generation_request_none_size(self, service):
        """Test validation fails with None size"""
        from business.image_business_service import ImageGenerationError

        with pytest.raises(ImageGenerationError, match="Size is required"):
            service._validate_generation_request("valid prompt", None)


    def test_generate_prompt_hash_handles_unicode(self, service):
        """Test hash generation with unicode characters"""
        prompt = "A beautiful 日本 sunset"

        result = service._generate_prompt_hash(prompt)

        assert len(result) == 10
        assert isinstance(result, str)
