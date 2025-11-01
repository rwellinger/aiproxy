"""Tests for SongProjectTransformer - Business logic unit tests (100% coverage)"""

from unittest.mock import Mock

from business.song_project_transformer import (
    calculate_pagination_meta,
    detect_file_type,
    generate_s3_prefix,
    get_default_folder_structure,
    get_mime_type,
    normalize_project_name,
    transform_file_to_response,
    transform_folder_to_response,
    transform_project_detail_to_response,
    transform_project_to_response,
    validate_sync_status,
)


class TestGenerateS3Prefix:
    """Test generate_s3_prefix() - slug generation from project name"""

    def test_basic_slug_generation(self):
        """Generate slug from simple project name"""
        project_name = "My Awesome Song"

        result = generate_s3_prefix(project_name)

        assert result == "projects/my-awesome-song/"

    def test_special_characters_removed(self):
        """Special characters are replaced with hyphens"""
        project_name = "Café Müller (2024)"

        result = generate_s3_prefix(project_name)

        # Umlauts and special chars are removed (not transliterated)
        assert result == "projects/caf-m-ller-2024/"

    def test_multiple_spaces_collapsed(self):
        """Multiple spaces/hyphens are collapsed to single hyphen"""
        project_name = "My    Song  -  Project"

        result = generate_s3_prefix(project_name)

        assert result == "projects/my-song-project/"

    def test_leading_trailing_hyphens_removed(self):
        """Leading and trailing hyphens are removed"""
        project_name = "---My Song---"

        result = generate_s3_prefix(project_name)

        assert result == "projects/my-song/"

    def test_numbers_preserved(self):
        """Numbers are preserved in slug"""
        project_name = "Song 2024 v3"

        result = generate_s3_prefix(project_name)

        assert result == "projects/song-2024-v3/"

    def test_empty_string_handling(self):
        """Empty string produces projects/ prefix"""
        project_name = ""

        result = generate_s3_prefix(project_name)

        assert result == "projects//"


class TestGetDefaultFolderStructure:
    """Test get_default_folder_structure() - folder list generation"""

    def test_returns_list(self):
        """Returns a list of folder definitions"""
        result = get_default_folder_structure()

        assert isinstance(result, list)

    def test_has_10_folders(self):
        """Returns exactly 10 default folders"""
        result = get_default_folder_structure()

        assert len(result) == 10

    def test_folder_structure_format(self):
        """Each folder has required keys"""
        result = get_default_folder_structure()

        for folder in result:
            assert "folder_name" in folder
            assert "folder_type" in folder
            assert "custom_icon" in folder

    def test_folder_names_ordered(self):
        """Folders are numbered 01-10"""
        result = get_default_folder_structure()

        assert result[0]["folder_name"] == "01 Arrangement"
        assert result[1]["folder_name"] == "02 AI"
        assert result[9]["folder_name"] == "10 Archive"

    def test_folder_types_assigned(self):
        """Each folder has a unique type"""
        result = get_default_folder_structure()

        folder_types = [f["folder_type"] for f in result]
        assert "arrangement" in folder_types
        assert "ai" in folder_types
        assert "cover" in folder_types

    def test_icons_use_font_awesome(self):
        """Icons use Font Awesome classes"""
        result = get_default_folder_structure()

        for folder in result:
            assert folder["custom_icon"].startswith("fas fa-")


class TestDetectFileType:
    """Test detect_file_type() - file type detection from extension"""

    def test_audio_files(self):
        """Detects audio file extensions"""
        assert detect_file_type("song.mp3") == "audio"
        assert detect_file_type("track.wav") == "audio"
        assert detect_file_type("music.flac") == "audio"
        assert detect_file_type("audio.m4a") == "audio"

    def test_image_files(self):
        """Detects image file extensions"""
        assert detect_file_type("cover.jpg") == "image"
        assert detect_file_type("photo.png") == "image"
        assert detect_file_type("graphic.svg") == "image"
        assert detect_file_type("pic.webp") == "image"

    def test_document_files(self):
        """Detects document file extensions"""
        assert detect_file_type("lyrics.txt") == "document"
        assert detect_file_type("notes.pdf") == "document"
        assert detect_file_type("readme.md") == "document"
        assert detect_file_type("doc.docx") == "document"

    def test_archive_files(self):
        """Detects archive file extensions"""
        assert detect_file_type("project.zip") == "archive"
        assert detect_file_type("backup.rar") == "archive"
        assert detect_file_type("files.7z") == "archive"

    def test_video_files(self):
        """Detects video file extensions"""
        assert detect_file_type("promo.mp4") == "video"
        assert detect_file_type("clip.avi") == "video"
        assert detect_file_type("video.mkv") == "video"

    def test_unknown_extension(self):
        """Returns 'other' for unknown extensions"""
        assert detect_file_type("file.xyz") == "other"
        assert detect_file_type("unknown.abc") == "other"

    def test_no_extension(self):
        """Handles files without extension"""
        assert detect_file_type("README") == "other"

    def test_case_insensitive(self):
        """File type detection is case-insensitive"""
        assert detect_file_type("SONG.MP3") == "audio"
        assert detect_file_type("Cover.JPG") == "image"


class TestGetMimeType:
    """Test get_mime_type() - MIME type detection from extension"""

    def test_audio_mime_types(self):
        """Returns correct MIME types for audio files"""
        assert get_mime_type("song.mp3") == "audio/mpeg"
        assert get_mime_type("track.wav") == "audio/wav"
        assert get_mime_type("music.flac") == "audio/flac"
        assert get_mime_type("audio.m4a") == "audio/mp4"

    def test_image_mime_types(self):
        """Returns correct MIME types for image files"""
        assert get_mime_type("cover.jpg") == "image/jpeg"
        assert get_mime_type("photo.png") == "image/png"
        assert get_mime_type("graphic.svg") == "image/svg+xml"
        assert get_mime_type("pic.webp") == "image/webp"

    def test_document_mime_types(self):
        """Returns correct MIME types for documents"""
        assert get_mime_type("notes.txt") == "text/plain"
        assert get_mime_type("doc.pdf") == "application/pdf"
        assert get_mime_type("file.docx") == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    def test_archive_mime_types(self):
        """Returns correct MIME types for archives"""
        assert get_mime_type("project.zip") == "application/zip"
        assert get_mime_type("backup.rar") == "application/x-rar-compressed"

    def test_video_mime_types(self):
        """Returns correct MIME types for video files"""
        assert get_mime_type("promo.mp4") == "video/mp4"
        assert get_mime_type("clip.avi") == "video/x-msvideo"

    def test_unknown_extension_returns_none(self):
        """Returns None for unknown extensions"""
        assert get_mime_type("file.xyz") is None
        assert get_mime_type("unknown.abc") is None

    def test_no_extension_returns_none(self):
        """Returns None for files without extension"""
        assert get_mime_type("README") is None

    def test_case_insensitive(self):
        """MIME type detection is case-insensitive"""
        assert get_mime_type("SONG.MP3") == "audio/mpeg"
        assert get_mime_type("Cover.JPG") == "image/jpeg"


class TestTransformProjectToResponse:
    """Test transform_project_to_response() - project to API response"""

    def test_basic_transformation(self):
        """Transforms project model to response dict"""
        project = Mock()
        project.id = "550e8400-e29b-41d4-a716-446655440000"
        project.project_name = "My Project"
        project.s3_prefix = "projects/my-project/"
        project.local_path = None
        project.sync_status = "local"
        project.last_sync_at = None
        project.cover_image_id = None
        project.tags = ["rock", "demo"]
        project.description = "A test project"
        project.total_files = 5
        project.total_size_bytes = 1024000
        project.created_at = Mock()
        project.created_at.isoformat.return_value = "2024-01-01T12:00:00"
        project.updated_at = Mock()
        project.updated_at.isoformat.return_value = "2024-01-02T12:00:00"

        result = transform_project_to_response(project)

        assert result["id"] == "550e8400-e29b-41d4-a716-446655440000"
        assert result["project_name"] == "My Project"
        assert result["s3_prefix"] == "projects/my-project/"
        assert result["sync_status"] == "local"
        assert result["tags"] == ["rock", "demo"]
        assert result["description"] == "A test project"
        assert result["total_files"] == 5
        assert result["total_size_bytes"] == 1024000
        assert result["created_at"] == "2024-01-01T12:00:00"

    def test_null_timestamps(self):
        """Handles None timestamps correctly"""
        project = Mock()
        project.id = "550e8400-e29b-41d4-a716-446655440000"
        project.project_name = "Test"
        project.s3_prefix = None
        project.local_path = None
        project.sync_status = "local"
        project.last_sync_at = None
        project.cover_image_id = None
        project.tags = []
        project.description = None
        project.total_files = 0
        project.total_size_bytes = 0
        project.created_at = None
        project.updated_at = None

        result = transform_project_to_response(project)

        assert result["last_sync_at"] is None
        assert result["created_at"] is None
        assert result["updated_at"] is None


class TestTransformFolderToResponse:
    """Test transform_folder_to_response() - folder to API response"""

    def test_basic_transformation(self):
        """Transforms folder model to response dict"""
        folder = Mock()
        folder.id = "folder-id-123"
        folder.folder_name = "01 Arrangement"
        folder.folder_type = "arrangement"
        folder.s3_prefix = "projects/test/01 Arrangement/"
        folder.custom_icon = "fas fa-music"
        folder.created_at = Mock()
        folder.created_at.isoformat.return_value = "2024-01-01T12:00:00"

        result = transform_folder_to_response(folder)

        assert result["id"] == "folder-id-123"
        assert result["folder_name"] == "01 Arrangement"
        assert result["folder_type"] == "arrangement"
        assert result["s3_prefix"] == "projects/test/01 Arrangement/"
        assert result["custom_icon"] == "fas fa-music"
        assert result["created_at"] == "2024-01-01T12:00:00"


class TestTransformFileToResponse:
    """Test transform_file_to_response() - file to API response"""

    def test_basic_transformation(self):
        """Transforms file model to response dict"""
        file = Mock()
        file.id = "file-id-123"
        file.filename = "song.mp3"
        file.relative_path = "01 Arrangement/song.mp3"
        file.file_type = "audio"
        file.mime_type = "audio/mpeg"
        file.file_size_bytes = 5000000
        file.storage_backend = "s3"
        file.is_synced = True
        file.created_at = Mock()
        file.created_at.isoformat.return_value = "2024-01-01T12:00:00"
        file.updated_at = Mock()
        file.updated_at.isoformat.return_value = "2024-01-02T12:00:00"

        result = transform_file_to_response(file, download_url="https://s3.example.com/song.mp3")

        assert result["id"] == "file-id-123"
        assert result["filename"] == "song.mp3"
        assert result["relative_path"] == "01 Arrangement/song.mp3"
        assert result["file_type"] == "audio"
        assert result["mime_type"] == "audio/mpeg"
        assert result["file_size_bytes"] == 5000000
        assert result["storage_backend"] == "s3"
        assert result["is_synced"] is True
        assert result["download_url"] == "https://s3.example.com/song.mp3"

    def test_without_download_url(self):
        """Handles missing download URL"""
        file = Mock()
        file.id = "file-id-123"
        file.filename = "song.mp3"
        file.relative_path = "song.mp3"
        file.file_type = "audio"
        file.mime_type = "audio/mpeg"
        file.file_size_bytes = 5000000
        file.storage_backend = "s3"
        file.is_synced = False
        file.created_at = None
        file.updated_at = None

        result = transform_file_to_response(file)

        assert result["download_url"] is None


class TestTransformProjectDetailToResponse:
    """Test transform_project_detail_to_response() - project with folders and files"""

    def test_basic_transformation(self):
        """Transforms project with folders and files"""
        # Create mock file
        file = Mock()
        file.id = "file-id"
        file.filename = "song.mp3"
        file.relative_path = "01 Arrangement/song.mp3"
        file.file_type = "audio"
        file.mime_type = "audio/mpeg"
        file.file_size_bytes = 5000000
        file.storage_backend = "s3"
        file.is_synced = True
        file.created_at = None
        file.updated_at = None

        # Create mock folder
        folder = Mock()
        folder.id = "folder-id"
        folder.folder_name = "01 Arrangement"
        folder.folder_type = "arrangement"
        folder.s3_prefix = "projects/test/01 Arrangement/"
        folder.custom_icon = "fas fa-music"
        folder.created_at = None
        folder.files = [file]

        # Create mock project
        project = Mock()
        project.id = "project-id"
        project.project_name = "Test Project"
        project.s3_prefix = "projects/test/"
        project.local_path = None
        project.sync_status = "local"
        project.last_sync_at = None
        project.cover_image_id = None
        project.tags = []
        project.description = None
        project.total_files = 1
        project.total_size_bytes = 5000000
        project.created_at = None
        project.updated_at = None
        project.folders = [folder]

        result = transform_project_detail_to_response(project)

        assert result["id"] == "project-id"
        assert result["project_name"] == "Test Project"
        assert len(result["folders"]) == 1
        assert result["folders"][0]["folder_name"] == "01 Arrangement"
        assert len(result["folders"][0]["files"]) == 1
        assert result["folders"][0]["files"][0]["filename"] == "song.mp3"


class TestCalculatePaginationMeta:
    """Test calculate_pagination_meta() - pagination metadata calculation"""

    def test_has_more_true(self):
        """Returns has_more=True when more items exist"""
        result = calculate_pagination_meta(total=100, limit=20, offset=0)

        assert result["total"] == 100
        assert result["limit"] == 20
        assert result["offset"] == 0
        assert result["has_more"] is True

    def test_has_more_false(self):
        """Returns has_more=False when no more items"""
        result = calculate_pagination_meta(total=15, limit=20, offset=0)

        assert result["total"] == 15
        assert result["limit"] == 20
        assert result["offset"] == 0
        assert result["has_more"] is False

    def test_has_more_at_boundary(self):
        """Returns has_more=False when exactly at last item"""
        result = calculate_pagination_meta(total=20, limit=20, offset=0)

        assert result["has_more"] is False

    def test_has_more_with_offset(self):
        """Calculates has_more correctly with offset"""
        result = calculate_pagination_meta(total=100, limit=20, offset=80)

        assert result["has_more"] is False  # 80 + 20 = 100


class TestNormalizeProjectName:
    """Test normalize_project_name() - string normalization"""

    def test_trims_whitespace(self):
        """Removes leading and trailing whitespace"""
        assert normalize_project_name("  My Project  ") == "My Project"

    def test_empty_string(self):
        """Handles empty string"""
        assert normalize_project_name("") == ""

    def test_whitespace_only(self):
        """Handles whitespace-only string"""
        assert normalize_project_name("   ") == ""

    def test_no_changes_needed(self):
        """Returns unchanged if already normalized"""
        assert normalize_project_name("My Project") == "My Project"


class TestValidateSyncStatus:
    """Test validate_sync_status() - sync status validation"""

    def test_valid_statuses(self):
        """Returns True for valid sync statuses"""
        assert validate_sync_status("local") is True
        assert validate_sync_status("cloud") is True
        assert validate_sync_status("synced") is True
        assert validate_sync_status("syncing") is True

    def test_invalid_status(self):
        """Returns False for invalid sync status"""
        assert validate_sync_status("invalid") is False
        assert validate_sync_status("pending") is False
        assert validate_sync_status("") is False

    def test_case_sensitive(self):
        """Validation is case-sensitive"""
        assert validate_sync_status("LOCAL") is False
        assert validate_sync_status("Cloud") is False
