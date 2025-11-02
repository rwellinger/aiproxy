"""Unit tests for SongTransformer"""

from datetime import datetime
from unittest.mock import Mock

from business.song_transformer import SongTransformer


class TestTransformSongToListFormat:
    """Tests for transform_song_to_list_format()"""

    def test_transform_song_to_list_format_complete(self):
        """Test transforming song with all fields"""
        # Arrange
        song = Mock(spec=["id", "lyrics", "title", "model", "tags", "workflow", "is_instrumental", "created_at"])
        song.id = 123
        song.lyrics = "Test lyrics"
        song.title = "Test Song"
        song.model = "mureka-7.5"
        song.tags = "pop,rock"
        song.workflow = "simple"
        song.is_instrumental = False
        song.created_at = datetime(2024, 1, 15, 10, 30, 0)

        # Act
        result = SongTransformer.transform_song_to_list_format(song)

        # Assert
        assert result == {
            "id": "123",
            "lyrics": "Test lyrics",
            "title": "Test Song",
            "model": "mureka-7.5",
            "tags": "pop,rock",
            "workflow": "simple",
            "is_instrumental": False,
            "project_id": None,
            "project_name": None,
            "created_at": "2024-01-15T10:30:00",
        }

    def test_transform_song_to_list_format_minimal(self):
        """Test transforming song with minimal fields"""
        # Arrange
        song = Mock(spec=["id", "lyrics", "title", "model", "tags", "workflow", "is_instrumental", "created_at"])
        song.id = 456
        song.lyrics = None
        song.title = None
        song.model = None
        song.tags = None
        song.workflow = "draft"
        song.is_instrumental = True
        song.created_at = None

        # Act
        result = SongTransformer.transform_song_to_list_format(song)

        # Assert
        assert result == {
            "id": "456",
            "lyrics": None,
            "title": None,
            "model": None,
            "tags": None,
            "workflow": "draft",
            "is_instrumental": True,
            "project_id": None,
            "project_name": None,
            "created_at": None,
        }


class TestTransformSongToDetailFormat:
    """Tests for transform_song_to_detail_format()"""

    def test_transform_song_to_detail_format_complete(self):
        """Test transforming song with all fields and choices"""
        # Arrange - Song
        song = Mock()
        song.id = 789
        song.task_id = "task-123"
        song.job_id = "job-456"
        song.lyrics = "Detailed lyrics"
        song.prompt = "Test prompt"
        song.model = "mureka-7.5"
        song.title = "Detailed Song"
        song.tags = "electronic"
        song.workflow = "simple"
        song.is_instrumental = False
        song.status = "SUCCESS"
        song.progress_info = "100%"
        song.error_message = None
        song.mureka_response = '{"status": "succeeded"}'
        song.mureka_status = "succeeded"
        song.created_at = datetime(2024, 1, 15, 10, 0, 0)
        song.updated_at = datetime(2024, 1, 15, 10, 30, 0)
        song.completed_at = datetime(2024, 1, 15, 11, 0, 0)

        # Arrange - Choice
        choice = Mock()
        choice.id = 111
        choice.mureka_choice_id = "choice-abc"
        choice.choice_index = 0
        choice.mp3_url = "https://mp3.url"
        choice.flac_url = "https://flac.url"
        choice.video_url = "https://video.url"
        choice.image_url = "https://image.url"
        choice.stem_url = "https://stem.url"
        choice.stem_generated_at = datetime(2024, 1, 15, 12, 0, 0)
        choice.duration = 180000.0  # 3 minutes in ms
        choice.title = "Choice Title"
        choice.tags = "pop,upbeat"
        choice.rating = 1
        choice.created_at = datetime(2024, 1, 15, 10, 30, 0)

        song.choices = [choice]

        # Act
        result = SongTransformer.transform_song_to_detail_format(song)

        # Assert - Song fields
        assert result["id"] == "789"
        assert result["task_id"] == "task-123"
        assert result["job_id"] == "job-456"
        assert result["lyrics"] == "Detailed lyrics"
        assert result["prompt"] == "Test prompt"
        assert result["model"] == "mureka-7.5"
        assert result["title"] == "Detailed Song"
        assert result["tags"] == "electronic"
        assert result["workflow"] == "simple"
        assert result["is_instrumental"] is False
        assert result["status"] == "SUCCESS"
        assert result["progress_info"] == "100%"
        assert result["error_message"] is None
        assert result["mureka_response"] == '{"status": "succeeded"}'
        assert result["mureka_status"] == "succeeded"
        assert result["choices_count"] == 1
        assert result["created_at"] == "2024-01-15T10:00:00"
        assert result["updated_at"] == "2024-01-15T10:30:00"
        assert result["completed_at"] == "2024-01-15T11:00:00"

        # Assert - Choice fields
        assert len(result["choices"]) == 1
        choice_result = result["choices"][0]
        assert choice_result["id"] == "111"
        assert choice_result["mureka_choice_id"] == "choice-abc"
        assert choice_result["choice_index"] == 0
        assert choice_result["mp3_url"] == "https://mp3.url"
        assert choice_result["flac_url"] == "https://flac.url"
        assert choice_result["video_url"] == "https://video.url"
        assert choice_result["image_url"] == "https://image.url"
        assert choice_result["stem_url"] == "https://stem.url"
        assert choice_result["stem_generated_at"] == "2024-01-15T12:00:00"
        assert choice_result["duration"] == 180000.0
        assert choice_result["title"] == "Choice Title"
        assert choice_result["tags"] == "pop,upbeat"
        assert choice_result["rating"] == 1
        assert choice_result["formattedDuration"] == "03:00"
        assert choice_result["created_at"] == "2024-01-15T10:30:00"

    def test_transform_song_to_detail_format_no_choices(self):
        """Test transforming song with no choices"""
        # Arrange
        song = Mock()
        song.id = 999
        song.task_id = "task-999"
        song.job_id = "job-999"
        song.lyrics = "No choices"
        song.prompt = "Test"
        song.model = None
        song.title = None
        song.tags = None
        song.workflow = "draft"
        song.is_instrumental = True
        song.status = "PROCESSING"
        song.progress_info = "50%"
        song.error_message = None
        song.mureka_response = None
        song.mureka_status = None
        song.created_at = datetime(2024, 1, 15, 10, 0, 0)
        song.updated_at = None
        song.completed_at = None
        song.choices = []

        # Act
        result = SongTransformer.transform_song_to_detail_format(song)

        # Assert
        assert result["id"] == "999"
        assert result["choices_count"] == 0
        assert result["choices"] == []

    def test_transform_song_to_detail_format_multiple_choices(self):
        """Test transforming song with multiple choices"""
        # Arrange
        song = Mock()
        song.id = 888
        song.task_id = "task-888"
        song.job_id = "job-888"
        song.lyrics = "Multiple choices"
        song.prompt = "Test"
        song.model = "mureka-7.5"
        song.title = "Multi Choice Song"
        song.tags = "test"
        song.workflow = "simple"
        song.is_instrumental = False
        song.status = "SUCCESS"
        song.progress_info = "100%"
        song.error_message = None
        song.mureka_response = "{}"
        song.mureka_status = "succeeded"
        song.created_at = datetime(2024, 1, 15, 10, 0, 0)
        song.updated_at = datetime(2024, 1, 15, 10, 30, 0)
        song.completed_at = datetime(2024, 1, 15, 11, 0, 0)

        # Create 3 choices
        choice1 = Mock()
        choice1.id = 1
        choice1.mureka_choice_id = "c1"
        choice1.choice_index = 0
        choice1.mp3_url = "url1"
        choice1.flac_url = None
        choice1.video_url = None
        choice1.image_url = None
        choice1.stem_url = None
        choice1.stem_generated_at = None
        choice1.duration = 120000.0
        choice1.title = "Choice 1"
        choice1.tags = None
        choice1.rating = None
        choice1.created_at = datetime(2024, 1, 15, 10, 30, 0)

        choice2 = Mock()
        choice2.id = 2
        choice2.mureka_choice_id = "c2"
        choice2.choice_index = 1
        choice2.mp3_url = "url2"
        choice2.flac_url = None
        choice2.video_url = None
        choice2.image_url = None
        choice2.stem_url = None
        choice2.stem_generated_at = None
        choice2.duration = 150000.0
        choice2.title = "Choice 2"
        choice2.tags = None
        choice2.rating = 1
        choice2.created_at = datetime(2024, 1, 15, 10, 30, 0)

        choice3 = Mock()
        choice3.id = 3
        choice3.mureka_choice_id = "c3"
        choice3.choice_index = 2
        choice3.mp3_url = "url3"
        choice3.flac_url = None
        choice3.video_url = None
        choice3.image_url = None
        choice3.stem_url = None
        choice3.stem_generated_at = None
        choice3.duration = None
        choice3.title = "Choice 3"
        choice3.tags = None
        choice3.rating = 0
        choice3.created_at = datetime(2024, 1, 15, 10, 30, 0)

        song.choices = [choice1, choice2, choice3]

        # Act
        result = SongTransformer.transform_song_to_detail_format(song)

        # Assert
        assert result["choices_count"] == 3
        assert len(result["choices"]) == 3
        assert result["choices"][0]["id"] == "1"
        assert result["choices"][0]["formattedDuration"] == "02:00"
        assert result["choices"][1]["id"] == "2"
        assert result["choices"][1]["formattedDuration"] == "02:30"
        assert result["choices"][2]["id"] == "3"
        assert result["choices"][2]["formattedDuration"] is None


class TestFormatDurationFromMs:
    """Tests for format_duration_from_ms()"""

    def test_format_duration_zero(self):
        """Test formatting zero duration"""
        assert SongTransformer.format_duration_from_ms(0) == "00:00"

    def test_format_duration_none(self):
        """Test formatting None duration"""
        assert SongTransformer.format_duration_from_ms(None) == "00:00"

    def test_format_duration_seconds_only(self):
        """Test formatting duration under 1 minute"""
        assert SongTransformer.format_duration_from_ms(30000) == "00:30"  # 30 seconds
        assert SongTransformer.format_duration_from_ms(45000) == "00:45"  # 45 seconds

    def test_format_duration_minutes_and_seconds(self):
        """Test formatting duration with minutes and seconds"""
        assert SongTransformer.format_duration_from_ms(90000) == "01:30"  # 1:30
        assert SongTransformer.format_duration_from_ms(125000) == "02:05"  # 2:05
        assert SongTransformer.format_duration_from_ms(180000) == "03:00"  # 3:00

    def test_format_duration_long(self):
        """Test formatting long duration"""
        assert SongTransformer.format_duration_from_ms(600000) == "10:00"  # 10:00
        assert SongTransformer.format_duration_from_ms(3661000) == "61:01"  # 61:01

    def test_format_duration_with_milliseconds(self):
        """Test formatting duration with milliseconds (should be truncated)"""
        assert SongTransformer.format_duration_from_ms(30567.89) == "00:30"  # 30.567 seconds -> 30
        assert SongTransformer.format_duration_from_ms(125999.99) == "02:05"  # 125.999 seconds -> 125
