"""Song Project Transformer - Pure functions for transformations and business logic

IMPORTANT: This module contains ONLY pure functions (100% unit-testable).
NO database operations, NO file system operations, NO external dependencies.
"""

import re
from typing import Any


def generate_s3_prefix(project_name: str, user_id: str) -> str:
    """
    Generate S3 prefix from user_id and project name (slug-like)

    Args:
        project_name: Project name (e.g., "My Awesome Song")
        user_id: User UUID (for multi-tenant isolation)

    Returns:
        S3 prefix (e.g., "{user-id}/my-awesome-song/")

    Examples:
        >>> generate_s3_prefix("My Awesome Song", "abc-123")
        'abc-123/my-awesome-song/'
        >>> generate_s3_prefix("Café Müller (2024)", "def-456")
        'def-456/cafe-muller-2024/'
    """
    # Convert to lowercase
    slug = project_name.lower()
    # Replace special characters with hyphens
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    # Remove leading/trailing hyphens
    slug = slug.strip("-")
    # Collapse multiple hyphens
    slug = re.sub(r"-+", "-", slug)
    return f"{user_id}/{slug}/"


def get_default_folder_structure() -> list[dict[str, str]]:
    """
    Get default folder structure for new projects

    Returns:
        List of folder definitions with name, type, and icon

    Examples:
        >>> folders = get_default_folder_structure()
        >>> folders[0]['folder_name']
        '01 Arrangement'
    """
    return [
        {"folder_name": "01 Arrangement", "folder_type": "arrangement", "custom_icon": "fas fa-music"},
        {"folder_name": "02 AI", "folder_type": "ai", "custom_icon": "fas fa-robot"},
        {"folder_name": "03 Pictures", "folder_type": "pictures", "custom_icon": "fas fa-image"},
        {"folder_name": "04 Vocal", "folder_type": "vocal", "custom_icon": "fas fa-microphone"},
        {"folder_name": "05 Stems", "folder_type": "stems", "custom_icon": "fas fa-layer-group"},
        {"folder_name": "06 Mix", "folder_type": "mix", "custom_icon": "fas fa-sliders-h"},
        {"folder_name": "07 Master", "folder_type": "master", "custom_icon": "fas fa-certificate"},
        {"folder_name": "08 Promotion", "folder_type": "promotion", "custom_icon": "fas fa-bullhorn"},
        {"folder_name": "09 Release", "folder_type": "release", "custom_icon": "fas fa-compact-disc"},
        {"folder_name": "10 Archive", "folder_type": "archive", "custom_icon": "fas fa-archive"},
    ]


def detect_file_type(filename: str) -> str:
    """
    Detect file type from filename extension

    Args:
        filename: Filename with extension

    Returns:
        File type (audio, image, document, archive, other)

    Examples:
        >>> detect_file_type("song.mp3")
        'audio'
        >>> detect_file_type("cover.jpg")
        'image'
        >>> detect_file_type("lyrics.txt")
        'document'
    """
    extension = filename.lower().split(".")[-1] if "." in filename else ""

    audio_extensions = {"mp3", "wav", "flac", "aac", "m4a", "ogg", "wma", "aiff", "alac"}
    image_extensions = {"jpg", "jpeg", "png", "gif", "bmp", "webp", "svg", "tiff"}
    document_extensions = {"txt", "doc", "docx", "pdf", "md", "rtf", "odt"}
    archive_extensions = {"zip", "rar", "7z", "tar", "gz", "bz2"}
    video_extensions = {"mp4", "avi", "mkv", "mov", "wmv", "flv", "webm"}

    if extension in audio_extensions:
        return "audio"
    elif extension in image_extensions:
        return "image"
    elif extension in document_extensions:
        return "document"
    elif extension in archive_extensions:
        return "archive"
    elif extension in video_extensions:
        return "video"
    else:
        return "other"


def get_mime_type(filename: str) -> str | None:
    """
    Get MIME type from filename extension

    Args:
        filename: Filename with extension

    Returns:
        MIME type or None if unknown

    Examples:
        >>> get_mime_type("song.mp3")
        'audio/mpeg'
        >>> get_mime_type("cover.jpg")
        'image/jpeg'
    """
    extension = filename.lower().split(".")[-1] if "." in filename else ""

    mime_map = {
        # Audio
        "mp3": "audio/mpeg",
        "wav": "audio/wav",
        "flac": "audio/flac",
        "aac": "audio/aac",
        "m4a": "audio/mp4",
        "ogg": "audio/ogg",
        # Image
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
        "webp": "image/webp",
        "svg": "image/svg+xml",
        # Document
        "txt": "text/plain",
        "pdf": "application/pdf",
        "doc": "application/msword",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        # Archive
        "zip": "application/zip",
        "rar": "application/x-rar-compressed",
        "7z": "application/x-7z-compressed",
        # Video
        "mp4": "video/mp4",
        "avi": "video/x-msvideo",
        "mkv": "video/x-matroska",
    }

    return mime_map.get(extension)


def transform_project_to_response(project: Any) -> dict[str, Any]:
    """
    Transform SongProject DB model to API response format

    Args:
        project: SongProject DB model instance

    Returns:
        Dictionary with project data for API response
    """
    return {
        "id": str(project.id),
        "project_name": project.project_name,
        "s3_prefix": project.s3_prefix,
        "local_path": project.local_path,
        "sync_status": project.sync_status,
        "last_sync_at": project.last_sync_at.isoformat() if project.last_sync_at else None,
        "cover_image_id": str(project.cover_image_id) if project.cover_image_id else None,
        "tags": project.tags,
        "description": project.description,
        "total_files": project.total_files,
        "total_size_bytes": project.total_size_bytes,
        "created_at": project.created_at.isoformat() if project.created_at else None,
        "updated_at": project.updated_at.isoformat() if project.updated_at else None,
    }


def transform_folder_to_response(folder: Any) -> dict[str, Any]:
    """
    Transform ProjectFolder DB model to API response format

    Args:
        folder: ProjectFolder DB model instance

    Returns:
        Dictionary with folder data for API response
    """
    return {
        "id": str(folder.id),
        "folder_name": folder.folder_name,
        "folder_type": folder.folder_type,
        "s3_prefix": folder.s3_prefix,
        "custom_icon": folder.custom_icon,
        "created_at": folder.created_at.isoformat() if folder.created_at else None,
    }


def transform_file_to_response(file: Any, download_url: str | None = None) -> dict[str, Any]:
    """
    Transform ProjectFile DB model to API response format

    Args:
        file: ProjectFile DB model instance
        download_url: Pre-signed download URL (optional)

    Returns:
        Dictionary with file data for API response
    """
    return {
        "id": str(file.id),
        "filename": file.filename,
        "relative_path": file.relative_path,
        "file_type": file.file_type,
        "mime_type": file.mime_type,
        "file_size_bytes": file.file_size_bytes,
        "storage_backend": file.storage_backend,
        "is_synced": file.is_synced,
        "download_url": download_url,
        "created_at": file.created_at.isoformat() if file.created_at else None,
        "updated_at": file.updated_at.isoformat() if file.updated_at else None,
    }


def transform_project_detail_to_response(project: Any) -> dict[str, Any]:
    """
    Transform SongProject with folders and files to detailed API response

    Args:
        project: SongProject DB model with loaded folders and files

    Returns:
        Dictionary with complete project data including folders and files
    """
    response = transform_project_to_response(project)

    # Add folders with their files
    folders_data = []
    total_files_live = 0
    total_size_live = 0

    for folder in project.folders:
        folder_data = transform_folder_to_response(folder)
        folder_data["files"] = [transform_file_to_response(file) for file in folder.files]
        folders_data.append(folder_data)

        # Calculate LIVE stats from actual files (Single Source of Truth)
        total_files_live += len(folder.files)
        total_size_live += sum(file.file_size_bytes for file in folder.files)

    response["folders"] = folders_data

    # Override DB stats with LIVE calculated values (always correct!)
    response["total_files"] = total_files_live
    response["total_size_bytes"] = total_size_live

    return response


def calculate_pagination_meta(total: int, limit: int, offset: int) -> dict[str, Any]:
    """
    Calculate pagination metadata

    Args:
        total: Total number of items
        limit: Items per page
        offset: Current offset

    Returns:
        Dictionary with pagination metadata

    Examples:
        >>> calculate_pagination_meta(100, 20, 0)
        {'total': 100, 'limit': 20, 'offset': 0, 'has_more': True}
        >>> calculate_pagination_meta(15, 20, 0)
        {'total': 15, 'limit': 20, 'offset': 0, 'has_more': False}
    """
    has_more = (offset + limit) < total
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": has_more,
    }


def normalize_project_name(project_name: str) -> str:
    """
    Normalize project name (trim whitespace)

    Args:
        project_name: Raw project name

    Returns:
        Normalized project name

    Examples:
        >>> normalize_project_name("  My Project  ")
        'My Project'
        >>> normalize_project_name("")
        ''
    """
    return project_name.strip()


def validate_sync_status(status: str) -> bool:
    """
    Validate sync status value

    Args:
        status: Sync status to validate

    Returns:
        True if valid, False otherwise

    Examples:
        >>> validate_sync_status("local")
        True
        >>> validate_sync_status("invalid")
        False
    """
    valid_statuses = {"local", "cloud", "synced", "syncing"}
    return status in valid_statuses
