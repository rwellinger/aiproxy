"""Unit tests for SongService database operations"""

import uuid
from unittest.mock import MagicMock

import pytest

from db.models import Song, SongStatus
from db.song_service import SongService


@pytest.mark.unit
class TestSongServiceCreate:
    """Test SongService.create_song method"""

    def test_create_song_success(self, mocker, mock_db_session, sample_song_data):
        """Test successful song creation"""

        # Mock get_db to return our mock session
        def mock_get_db():
            yield mock_db_session

        mocker.patch("db.song_service.get_db", side_effect=mock_get_db)

        # Create song instance that will be returned after add/commit
        created_song = Song(**sample_song_data)
        created_song.id = uuid.uuid4()

        # Mock db operations
        mock_db_session.add = MagicMock()
        mock_db_session.commit = MagicMock()
        mock_db_session.refresh = MagicMock(side_effect=lambda x: setattr(x, "id", created_song.id))

        service = SongService()
        result = service.create_song(
            task_id="test-task-123",
            lyrics="Test lyrics",
            prompt="Test style prompt",
            model="auto",
            is_instrumental=False,
            title="Test Song",
        )

        assert result is not None
        assert mock_db_session.add.called
        assert mock_db_session.commit.called
        assert mock_db_session.close.called

    def test_create_song_db_error(self, mocker, mock_db_session):
        """Test song creation with database error"""

        def mock_get_db():
            yield mock_db_session

        mocker.patch("db.song_service.get_db", side_effect=mock_get_db)

        # Simulate database error on commit
        from sqlalchemy.exc import SQLAlchemyError

        mock_db_session.commit.side_effect = SQLAlchemyError("DB Error")

        service = SongService()
        result = service.create_song(
            task_id="test-task-123",
            lyrics="Test lyrics",
            prompt="Test prompt",
        )

        assert result is None
        assert mock_db_session.rollback.called


@pytest.mark.unit
class TestSongServiceQuery:
    """Test SongService query methods"""

    def test_get_song_by_task_id_found(self, mocker, mock_db_session):
        """Test getting song by task_id when found"""
        # Create a mock song
        mock_song = Song(
            task_id="test-task-123",
            lyrics="Test",
            prompt="Test",
            status="SUCCESS",
        )
        mock_song.id = uuid.uuid4()
        mock_song.choices = []

        def mock_get_db():
            yield mock_db_session

        mocker.patch("db.song_service.get_db", side_effect=mock_get_db)

        # Mock query chain
        mock_query = MagicMock()
        mock_options = MagicMock()
        mock_filter = MagicMock()

        mock_db_session.query.return_value = mock_query
        mock_query.options.return_value = mock_options
        mock_options.filter.return_value = mock_filter
        mock_filter.first.return_value = mock_song

        service = SongService()
        result = service.get_song_by_task_id("test-task-123")

        assert result is not None
        assert result.task_id == "test-task-123"
        assert mock_db_session.close.called

    def test_get_song_by_task_id_not_found(self, mocker, mock_db_session):
        """Test getting song by task_id when not found"""

        def mock_get_db():
            yield mock_db_session

        mocker.patch("db.song_service.get_db", side_effect=mock_get_db)

        # Mock query chain returning None
        mock_query = MagicMock()
        mock_options = MagicMock()
        mock_filter = MagicMock()

        mock_db_session.query.return_value = mock_query
        mock_query.options.return_value = mock_options
        mock_options.filter.return_value = mock_filter
        mock_filter.first.return_value = None

        service = SongService()
        result = service.get_song_by_task_id("nonexistent-task")

        assert result is None

    def test_get_song_by_job_id_found(self, mocker, mock_db_session):
        """Test getting song by job_id when found"""
        mock_song = Song(
            task_id="test-task",
            job_id="job-123",
            lyrics="Test",
            prompt="Test",
        )
        mock_song.id = uuid.uuid4()
        mock_song.choices = []

        def mock_get_db():
            yield mock_db_session

        mocker.patch("db.song_service.get_db", side_effect=mock_get_db)

        # Mock query chain
        mock_query = MagicMock()
        mock_options = MagicMock()
        mock_filter = MagicMock()

        mock_db_session.query.return_value = mock_query
        mock_query.options.return_value = mock_options
        mock_options.filter.return_value = mock_filter
        mock_filter.first.return_value = mock_song

        service = SongService()
        result = service.get_song_by_job_id("job-123")

        assert result is not None
        assert result.job_id == "job-123"


@pytest.mark.unit
class TestSongServiceUpdate:
    """Test SongService update methods"""

    def test_update_song_status_success(self, mocker, mock_db_session):
        """Test successful song status update"""
        mock_song = Song(
            task_id="test-task",
            lyrics="Test",
            prompt="Test",
            status="PENDING",
        )

        def mock_get_db():
            yield mock_db_session

        mocker.patch("db.song_service.get_db", side_effect=mock_get_db)

        # Mock query to return song
        mock_query = MagicMock()
        mock_filter = MagicMock()

        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = mock_song

        service = SongService()
        result = service.update_song_status(
            task_id="test-task",
            status="PROGRESS",
            progress_info={"step": 1},
            job_id="job-123",
        )

        assert result is True
        assert mock_song.status == "PROGRESS"
        assert mock_song.job_id == "job-123"
        assert mock_db_session.commit.called

    def test_update_song_status_not_found(self, mocker, mock_db_session):
        """Test updating status for nonexistent song"""

        def mock_get_db():
            yield mock_db_session

        mocker.patch("db.song_service.get_db", side_effect=mock_get_db)

        # Mock query to return None
        mock_query = MagicMock()
        mock_filter = MagicMock()

        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = None

        service = SongService()
        result = service.update_song_status(
            task_id="nonexistent",
            status="PROGRESS",
        )

        assert result is False

    def test_update_song_error(self, mocker, mock_db_session):
        """Test updating song with error message"""
        mock_song = Song(
            task_id="test-task",
            lyrics="Test",
            prompt="Test",
        )

        def mock_get_db():
            yield mock_db_session

        mocker.patch("db.song_service.get_db", side_effect=mock_get_db)

        # Mock query
        mock_query = MagicMock()
        mock_filter = MagicMock()

        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = mock_song

        service = SongService()
        result = service.update_song_error(
            task_id="test-task",
            error_message="Generation failed",
        )

        assert result is True
        assert mock_song.status == SongStatus.FAILURE.value
        assert mock_song.error_message == "Generation failed"


@pytest.mark.unit
class TestSongServiceDelete:
    """Test SongService delete operations"""

    def test_delete_song_by_id_success(self, mocker, mock_db_session):
        """Test successful song deletion"""
        mock_song = Song(
            task_id="test-task",
            lyrics="Test",
            prompt="Test",
        )
        mock_song.id = uuid.uuid4()

        def mock_get_db():
            yield mock_db_session

        mocker.patch("db.song_service.get_db", side_effect=mock_get_db)

        # Mock query
        mock_query = MagicMock()
        mock_filter = MagicMock()

        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = mock_song

        service = SongService()
        result = service.delete_song_by_id(str(mock_song.id))

        assert result is True
        assert mock_db_session.delete.called
        assert mock_db_session.commit.called

    def test_delete_song_by_id_not_found(self, mocker, mock_db_session):
        """Test deleting nonexistent song"""

        def mock_get_db():
            yield mock_db_session

        mocker.patch("db.song_service.get_db", side_effect=mock_get_db)

        # Mock query returning None
        mock_query = MagicMock()
        mock_filter = MagicMock()

        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = None

        service = SongService()
        result = service.delete_song_by_id(str(uuid.uuid4()))

        assert result is False


@pytest.mark.unit
class TestSongServiceRedisCleanup:
    """Test SongService Redis cleanup operations"""

    def test_cleanup_redis_data_success(self, mocker, mock_redis_client):
        """Test successful Redis cleanup"""
        mocker.patch("redis.from_url", return_value=mock_redis_client)
        mock_redis_client.delete.return_value = 1

        service = SongService()
        result = service.cleanup_redis_data("test-task-123")

        assert result is True
        mock_redis_client.delete.assert_called_once_with("celery-task-meta-test-task-123")

    def test_cleanup_redis_data_no_key(self, mocker, mock_redis_client):
        """Test Redis cleanup when key doesn't exist"""
        mocker.patch("redis.from_url", return_value=mock_redis_client)
        mock_redis_client.delete.return_value = 0  # No keys deleted

        service = SongService()
        result = service.cleanup_redis_data("test-task-123")

        assert result is True  # Still returns True, just logs differently

    def test_cleanup_redis_data_error(self, mocker, mock_redis_client):
        """Test Redis cleanup with connection error"""
        import redis

        mocker.patch("redis.from_url", return_value=mock_redis_client)
        mock_redis_client.delete.side_effect = redis.RedisError("Connection failed")

        service = SongService()
        result = service.cleanup_redis_data("test-task-123")

        assert result is False


@pytest.mark.unit
class TestSongServicePagination:
    """Test SongService pagination methods"""

    def test_get_songs_paginated(self, mocker, mock_db_session):
        """Test getting paginated songs"""
        mock_songs = [Song(task_id=f"task-{i}", lyrics="Test", prompt="Test") for i in range(3)]
        for song in mock_songs:
            song.choices = []

        def mock_get_db():
            yield mock_db_session

        mocker.patch("db.song_service.get_db", side_effect=mock_get_db)

        # Mock query chain
        mock_query = MagicMock()
        mock_options = MagicMock()
        mock_order = MagicMock()
        mock_limit = MagicMock()
        mock_offset = MagicMock()

        mock_db_session.query.return_value = mock_query
        mock_query.options.return_value = mock_options
        mock_options.order_by.return_value = mock_order
        mock_order.limit.return_value = mock_limit
        mock_limit.offset.return_value = mock_offset
        mock_offset.all.return_value = mock_songs

        service = SongService()
        result = service.get_songs_paginated(limit=10, offset=0)

        assert len(result) == 3
        assert all(isinstance(song, Song) for song in result)

    def test_get_total_songs_count(self, mocker, mock_db_session):
        """Test getting total songs count"""

        def mock_get_db():
            yield mock_db_session

        mocker.patch("db.song_service.get_db", side_effect=mock_get_db)

        # Mock query count
        mock_query = MagicMock()
        mock_db_session.query.return_value = mock_query
        mock_query.count.return_value = 42

        service = SongService()
        result = service.get_total_songs_count()

        assert result == 42
        assert mock_query.count.called
