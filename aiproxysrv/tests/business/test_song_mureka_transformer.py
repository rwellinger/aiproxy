"""Unit tests for SongMurekaTransformer"""

from business.song_mureka_transformer import SongMurekaTransformer


class TestParseMurekaResult:
    """Tests for parse_mureka_result()"""

    def test_parse_mureka_result_complete(self):
        """Test parsing complete MUREKA response with all fields"""
        # Arrange
        result_data = {
            "status": "SUCCESS",
            "result": {
                "status": "succeeded",
                "model": "mureka-7.5",
                "choices": [
                    {
                        "id": "choice-abc-123",
                        "index": 0,
                        "url": "https://mureka.ai/songs/abc.mp3",
                        "flac_url": "https://mureka.ai/songs/abc.flac",
                        "video_url": "https://mureka.ai/songs/abc.mp4",
                        "image_url": "https://mureka.ai/songs/abc.jpg",
                        "duration": 180567.89,
                        "title": "Amazing Song",
                        "tags": ["pop", "upbeat", "electronic"],
                    },
                    {
                        "id": "choice-def-456",
                        "index": 1,
                        "url": "https://mureka.ai/songs/def.mp3",
                        "duration": 150000.0,
                        "title": "Another Song",
                        "tags": ["rock"],
                    },
                ],
            },
            "completed_at": 1234567890,
        }

        # Act
        parsed = SongMurekaTransformer.parse_mureka_result(result_data)

        # Assert - Top-level fields
        assert parsed["mureka_result"] == result_data["result"]
        assert parsed["mureka_status"] == "succeeded"
        assert parsed["model"] == "mureka-7.5"
        assert parsed["completed_at"] == 1234567890
        assert parsed["choices_count"] == 2

        # Assert - First choice
        choice1 = parsed["choices"][0]
        assert choice1["mureka_choice_id"] == "choice-abc-123"
        assert choice1["choice_index"] == 0
        assert choice1["mp3_url"] == "https://mureka.ai/songs/abc.mp3"
        assert choice1["flac_url"] == "https://mureka.ai/songs/abc.flac"
        assert choice1["video_url"] == "https://mureka.ai/songs/abc.mp4"
        assert choice1["image_url"] == "https://mureka.ai/songs/abc.jpg"
        assert choice1["duration"] == 180567.89
        assert choice1["title"] == "Amazing Song"
        assert choice1["tags"] == "pop,upbeat,electronic"

        # Assert - Second choice
        choice2 = parsed["choices"][1]
        assert choice2["mureka_choice_id"] == "choice-def-456"
        assert choice2["choice_index"] == 1
        assert choice2["mp3_url"] == "https://mureka.ai/songs/def.mp3"
        assert choice2["flac_url"] is None
        assert choice2["video_url"] is None
        assert choice2["image_url"] is None
        assert choice2["duration"] == 150000.0
        assert choice2["title"] == "Another Song"
        assert choice2["tags"] == "rock"

    def test_parse_mureka_result_minimal(self):
        """Test parsing minimal MUREKA response"""
        # Arrange - Only required fields
        result_data = {
            "result": {
                "status": "succeeded",
                "choices": [],
            }
        }

        # Act
        parsed = SongMurekaTransformer.parse_mureka_result(result_data)

        # Assert
        assert parsed["mureka_result"] == result_data["result"]
        assert parsed["mureka_status"] == "succeeded"
        assert parsed["model"] is None
        assert parsed["completed_at"] is None
        assert parsed["choices_count"] == 0
        assert parsed["choices"] == []

    def test_parse_mureka_result_no_result_key(self):
        """Test parsing response without result key"""
        # Arrange
        result_data = {"status": "ERROR", "completed_at": 1234567890}

        # Act
        parsed = SongMurekaTransformer.parse_mureka_result(result_data)

        # Assert
        assert parsed["mureka_result"] is None
        assert parsed["mureka_status"] is None
        assert parsed["model"] is None
        assert parsed["completed_at"] == 1234567890
        assert parsed["choices_count"] == 0
        assert parsed["choices"] == []

    def test_parse_mureka_result_empty_result(self):
        """Test parsing response with empty result"""
        # Arrange
        result_data = {"result": {}}

        # Act
        parsed = SongMurekaTransformer.parse_mureka_result(result_data)

        # Assert
        assert parsed["mureka_result"] == {}
        assert parsed["mureka_status"] is None
        assert parsed["model"] is None
        assert parsed["completed_at"] is None
        assert parsed["choices_count"] == 0
        assert parsed["choices"] == []

    def test_parse_mureka_result_null_result(self):
        """Test parsing response with null result"""
        # Arrange
        result_data = {"result": None}

        # Act
        parsed = SongMurekaTransformer.parse_mureka_result(result_data)

        # Assert
        assert parsed["mureka_result"] is None
        assert parsed["mureka_status"] is None


class TestTransformChoiceToDbFormat:
    """Tests for transform_choice_to_db_format()"""

    def test_transform_choice_complete(self):
        """Test transforming choice with all fields"""
        # Arrange
        choice_data = {
            "id": "choice-xyz",
            "index": 2,
            "url": "https://mp3.url",
            "flac_url": "https://flac.url",
            "video_url": "https://video.url",
            "image_url": "https://image.url",
            "duration": 240000.5,
            "title": "Test Choice",
            "tags": ["jazz", "smooth"],
        }

        # Act
        result = SongMurekaTransformer.transform_choice_to_db_format(choice_data)

        # Assert
        assert result["mureka_choice_id"] == "choice-xyz"
        assert result["choice_index"] == 2
        assert result["mp3_url"] == "https://mp3.url"
        assert result["flac_url"] == "https://flac.url"
        assert result["video_url"] == "https://video.url"
        assert result["image_url"] == "https://image.url"
        assert result["duration"] == 240000.5
        assert result["title"] == "Test Choice"
        assert result["tags"] == "jazz,smooth"

    def test_transform_choice_minimal(self):
        """Test transforming choice with minimal fields"""
        # Arrange
        choice_data = {}

        # Act
        result = SongMurekaTransformer.transform_choice_to_db_format(choice_data)

        # Assert
        assert result["mureka_choice_id"] is None
        assert result["choice_index"] is None
        assert result["mp3_url"] is None
        assert result["flac_url"] is None
        assert result["video_url"] is None
        assert result["image_url"] is None
        assert result["duration"] is None
        assert result["title"] is None
        assert result["tags"] is None

    def test_transform_choice_partial_urls(self):
        """Test transforming choice with only some URLs"""
        # Arrange
        choice_data = {
            "id": "choice-partial",
            "url": "https://mp3.url",
            "duration": 120000,
            "tags": ["test"],
        }

        # Act
        result = SongMurekaTransformer.transform_choice_to_db_format(choice_data)

        # Assert
        assert result["mureka_choice_id"] == "choice-partial"
        assert result["mp3_url"] == "https://mp3.url"
        assert result["flac_url"] is None
        assert result["video_url"] is None
        assert result["image_url"] is None
        assert result["duration"] == 120000.0
        assert result["tags"] == "test"


class TestParseTagsArray:
    """Tests for parse_tags_array()"""

    def test_parse_tags_array_multiple(self):
        """Test parsing array with multiple tags"""
        assert SongMurekaTransformer.parse_tags_array(["pop", "rock", "electronic"]) == "pop,rock,electronic"

    def test_parse_tags_array_single(self):
        """Test parsing array with single tag"""
        assert SongMurekaTransformer.parse_tags_array(["jazz"]) == "jazz"

    def test_parse_tags_array_empty(self):
        """Test parsing empty array"""
        assert SongMurekaTransformer.parse_tags_array([]) is None

    def test_parse_tags_array_none(self):
        """Test parsing None value"""
        assert SongMurekaTransformer.parse_tags_array(None) is None

    def test_parse_tags_array_invalid_type_string(self):
        """Test parsing invalid type (string instead of list)"""
        assert SongMurekaTransformer.parse_tags_array("rock") is None

    def test_parse_tags_array_invalid_type_dict(self):
        """Test parsing invalid type (dict instead of list)"""
        assert SongMurekaTransformer.parse_tags_array({"tag": "rock"}) is None

    def test_parse_tags_array_with_numbers(self):
        """Test parsing array with non-string values (should convert to string)"""
        assert SongMurekaTransformer.parse_tags_array([1, 2, 3]) == "1,2,3"

    def test_parse_tags_array_with_mixed_types(self):
        """Test parsing array with mixed types"""
        assert SongMurekaTransformer.parse_tags_array(["pop", 123, "rock"]) == "pop,123,rock"


class TestParseDuration:
    """Tests for parse_duration()"""

    def test_parse_duration_float(self):
        """Test parsing float duration"""
        assert SongMurekaTransformer.parse_duration(180567.89) == 180567.89

    def test_parse_duration_int(self):
        """Test parsing integer duration"""
        assert SongMurekaTransformer.parse_duration(180000) == 180000.0

    def test_parse_duration_string_valid(self):
        """Test parsing valid string duration"""
        assert SongMurekaTransformer.parse_duration("180567.89") == 180567.89
        assert SongMurekaTransformer.parse_duration("180000") == 180000.0

    def test_parse_duration_none(self):
        """Test parsing None duration"""
        assert SongMurekaTransformer.parse_duration(None) is None

    def test_parse_duration_zero(self):
        """Test parsing zero duration"""
        assert SongMurekaTransformer.parse_duration(0) == 0.0
        assert SongMurekaTransformer.parse_duration(0.0) == 0.0

    def test_parse_duration_string_invalid(self):
        """Test parsing invalid string (should return None)"""
        assert SongMurekaTransformer.parse_duration("invalid") is None
        assert SongMurekaTransformer.parse_duration("") is None

    def test_parse_duration_invalid_type_list(self):
        """Test parsing invalid type list (should return None)"""
        assert SongMurekaTransformer.parse_duration([180000]) is None

    def test_parse_duration_invalid_type_dict(self):
        """Test parsing invalid type dict (should return None)"""
        assert SongMurekaTransformer.parse_duration({"duration": 180000}) is None

    def test_parse_duration_negative(self):
        """Test parsing negative duration (valid conversion, even if unusual)"""
        assert SongMurekaTransformer.parse_duration(-100) == -100.0
