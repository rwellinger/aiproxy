"""Pydantic schemas for Song Project API validation"""

from pydantic import BaseModel, Field

from schemas.common_schemas import PaginationMeta


class ProjectCreateRequest(BaseModel):
    """Request schema for creating a new project"""

    project_name: str = Field(..., min_length=1, max_length=255, description="Project name")
    tags: list[str] | None = Field(default=None, description="Optional tags list")
    description: str | None = Field(default=None, max_length=5000, description="Optional project description")


class ProjectUpdateRequest(BaseModel):
    """Request schema for updating a project"""

    project_name: str | None = Field(default=None, min_length=1, max_length=255, description="New project name")
    tags: list[str] | None = Field(default=None, description="New tags list")
    description: str | None = Field(default=None, max_length=5000, description="New description")
    cover_image_id: str | None = Field(default=None, description="Cover image UUID")


class ProjectResponse(BaseModel):
    """Response schema for a song project"""

    id: str
    project_name: str
    s3_prefix: str | None
    local_path: str | None
    sync_status: str
    last_sync_at: str | None
    cover_image_id: str | None
    tags: list[str]
    description: str | None
    total_files: int
    total_size_bytes: int
    created_at: str | None
    updated_at: str | None

    class Config:
        from_attributes = True


class FolderResponse(BaseModel):
    """Response schema for a project folder"""

    id: str
    folder_name: str
    folder_type: str | None
    s3_prefix: str | None
    custom_icon: str | None
    created_at: str | None
    files: list["FileResponse"] | None = None

    class Config:
        from_attributes = True


class FileResponse(BaseModel):
    """Response schema for a project file"""

    id: str
    filename: str
    relative_path: str
    file_type: str | None
    mime_type: str | None
    file_size_bytes: int | None
    storage_backend: str
    is_synced: bool
    download_url: str | None
    created_at: str | None
    updated_at: str | None

    class Config:
        from_attributes = True


class ProjectDetailResponse(BaseModel):
    """Response schema for project with folders and files"""

    id: str
    project_name: str
    s3_prefix: str | None
    local_path: str | None
    sync_status: str
    last_sync_at: str | None
    cover_image_id: str | None
    tags: list[str]
    description: str | None
    total_files: int
    total_size_bytes: int
    created_at: str | None
    updated_at: str | None
    folders: list[FolderResponse]

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    """Response schema for list of projects with pagination"""

    data: list[ProjectResponse]
    pagination: PaginationMeta

    class Config:
        from_attributes = True


class FileUploadResponse(BaseModel):
    """Response schema for file upload"""

    file: FileResponse
    message: str

    class Config:
        from_attributes = True
