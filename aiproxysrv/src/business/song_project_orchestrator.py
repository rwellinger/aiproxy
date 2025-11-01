"""Song Project Orchestrator - Coordinates services for song project operations

IMPORTANT: This orchestrator coordinates services but contains NO business logic.
Business logic is in song_project_transformer.py (100% testable).
This orchestrator is NOT unit-tested (orchestration only).
"""

import contextlib
from typing import TYPE_CHECKING, Any
from uuid import UUID

from infrastructure.storage.storage_factory import get_storage


if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from business.song_project_transformer import (
    calculate_pagination_meta,
    detect_file_type,
    generate_s3_prefix,
    get_default_folder_structure,
    get_mime_type,
    normalize_project_name,
    transform_project_detail_to_response,
    transform_project_to_response,
)
from db.song_project_service import song_project_service
from utils.logger import logger


class SongProjectOrchestrator:
    """Orchestrator for song project operations (coordinates services, NO business logic)"""

    def __init__(self):
        """Initialize orchestrator with services"""
        self.db_service = song_project_service
        self.storage = get_storage()

    def create_project_with_structure(
        self,
        db: Session,
        user_id: UUID,
        project_name: str,
        tags: list[str] | None = None,
        description: str | None = None,
    ) -> dict[str, Any] | None:
        """
        Create project with default folder structure and S3 setup

        Args:
            db: Database session
            user_id: User ID (from JWT)
            project_name: Project name
            tags: Optional tags list
            description: Optional description

        Returns:
            Project data dictionary or None if failed
        """
        try:
            # 1. Normalize project name (business logic in transformer)
            normalized_name = normalize_project_name(project_name)
            if not normalized_name:
                logger.warning("Project name is empty after normalization")
                return None

            # 2. Generate S3 prefix (business logic in transformer)
            s3_prefix = generate_s3_prefix(normalized_name)

            # 3. Create project in DB (CRUD in db_service)
            project = self.db_service.create_project(
                db=db,
                user_id=user_id,
                project_name=normalized_name,
                s3_prefix=s3_prefix,
                tags=tags,
                description=description,
            )

            if not project:
                logger.error("Failed to create project in DB")
                return None

            # 4. Get default folder structure (business logic in transformer)
            folder_defs = get_default_folder_structure()

            # 5. Create folders in DB and S3 (coordination)
            created_folders = []
            for folder_def in folder_defs:
                # Generate S3 prefix for folder
                folder_s3_prefix = f"{s3_prefix}{folder_def['folder_name']}/"

                # Create folder in DB
                folder = self.db_service.create_folder(
                    db=db,
                    project_id=project.id,
                    folder_name=folder_def["folder_name"],
                    folder_type=folder_def["folder_type"],
                    s3_prefix=folder_s3_prefix,
                    custom_icon=folder_def.get("custom_icon"),
                )

                if folder:
                    created_folders.append(folder)

                    # Create placeholder file in S3 (to ensure folder exists)
                    try:
                        placeholder_key = f"{folder_s3_prefix}.gitkeep"
                        self.storage.upload(b"", placeholder_key, content_type="text/plain")
                    except Exception as e:
                        logger.warning(
                            "Failed to create S3 placeholder", folder=folder_def["folder_name"], error=str(e)
                        )

            logger.info(
                "Project created with structure",
                project_id=str(project.id),
                project_name=normalized_name,
                folders_created=len(created_folders),
            )

            # 6. Transform to response (business logic in transformer)
            return transform_project_to_response(project)

        except Exception as e:
            logger.error("Project creation orchestration failed", error=str(e), error_type=type(e).__name__)
            return None

    def get_project_by_id(self, db: Session, project_id: UUID, user_id: UUID) -> dict[str, Any] | None:
        """
        Get project by ID (without details)

        Args:
            db: Database session
            project_id: Project UUID
            user_id: User ID (for ownership check)

        Returns:
            Project data dictionary or None if not found/unauthorized
        """
        try:
            # Get project from DB
            project = self.db_service.get_project_by_id(db, project_id)

            if not project:
                logger.debug("Project not found", project_id=str(project_id))
                return None

            # Check ownership
            if project.user_id != user_id:
                logger.warning("Unauthorized project access", project_id=str(project_id), user_id=str(user_id))
                return None

            # Transform to response
            return transform_project_to_response(project)

        except Exception as e:
            logger.error(
                "Get project by ID failed", project_id=str(project_id), error=str(e), error_type=type(e).__name__
            )
            return None

    def get_project_with_details(self, db: Session, project_id: UUID, user_id: UUID) -> dict[str, Any] | None:
        """
        Get project with all folders and files

        Args:
            db: Database session
            project_id: Project UUID
            user_id: User ID (for ownership check)

        Returns:
            Project data with folders and files, or None if not found/unauthorized
        """
        try:
            # Get project with details from DB
            project = self.db_service.get_project_with_details(db, project_id)

            if not project:
                logger.debug("Project not found", project_id=str(project_id))
                return None

            # Check ownership
            if project.user_id != user_id:
                logger.warning("Unauthorized project access", project_id=str(project_id), user_id=str(user_id))
                return None

            # Transform to response
            return transform_project_detail_to_response(project)

        except Exception as e:
            logger.error(
                "Get project details failed", project_id=str(project_id), error=str(e), error_type=type(e).__name__
            )
            return None

    def list_projects(
        self,
        db: Session,
        user_id: UUID,
        limit: int = 20,
        offset: int = 0,
        search: str = "",
        tags: str | None = None,
    ) -> dict[str, Any]:
        """
        List projects for user (paginated)

        Args:
            db: Database session
            user_id: User ID (from JWT)
            limit: Items per page
            offset: Offset for pagination
            search: Search term
            tags: Comma-separated tags

        Returns:
            Dictionary with projects and pagination meta
        """
        try:
            # Get paginated projects from DB
            result = self.db_service.get_projects_paginated(
                db=db,
                user_id=user_id,
                limit=limit,
                offset=offset,
                search=search,
                tags=tags,
            )

            # Transform projects to response
            projects_data = [transform_project_to_response(p) for p in result["items"]]

            # Calculate pagination metadata (business logic in transformer)
            pagination = calculate_pagination_meta(result["total"], limit, offset)

            return {
                "projects": projects_data,
                "pagination": pagination,
            }

        except Exception as e:
            logger.error("List projects failed", user_id=str(user_id), error=str(e), error_type=type(e).__name__)
            return {
                "projects": [],
                "pagination": {"total": 0, "limit": limit, "offset": offset, "has_more": False},
            }

    def update_project(
        self,
        db: Session,
        project_id: UUID,
        user_id: UUID,
        update_data: dict[str, Any],
    ) -> dict[str, Any] | None:
        """
        Update project

        Args:
            db: Database session
            project_id: Project UUID
            user_id: User ID (for ownership check)
            update_data: Data to update

        Returns:
            Updated project data or None if failed
        """
        try:
            # Get project for ownership check
            project = self.db_service.get_project_by_id(db, project_id)
            if not project:
                logger.debug("Project not found", project_id=str(project_id))
                return None

            # Check ownership
            if project.user_id != user_id:
                logger.warning("Unauthorized project update", project_id=str(project_id), user_id=str(user_id))
                return None

            # Normalize project name if provided (business logic in transformer)
            if "project_name" in update_data:
                update_data["project_name"] = normalize_project_name(update_data["project_name"])

            # Update project in DB
            updated_project = self.db_service.update_project(db, project_id, **update_data)

            if not updated_project:
                logger.error("Failed to update project in DB", project_id=str(project_id))
                return None

            # Transform to response
            return transform_project_to_response(updated_project)

        except Exception as e:
            logger.error("Update project failed", project_id=str(project_id), error=str(e), error_type=type(e).__name__)
            return None

    def delete_project_with_cleanup(self, db: Session, project_id: UUID, user_id: UUID) -> bool:
        """
        Delete project with S3 cleanup

        Args:
            db: Database session
            project_id: Project UUID
            user_id: User ID (for ownership check)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get project for ownership check
            project = self.db_service.get_project_by_id(db, project_id)
            if not project:
                logger.debug("Project not found", project_id=str(project_id))
                return False

            # Check ownership
            if project.user_id != user_id:
                logger.warning("Unauthorized project deletion", project_id=str(project_id), user_id=str(user_id))
                return False

            # Delete S3 files if s3_prefix exists
            if project.s3_prefix:
                try:
                    # List all files with this prefix
                    files = self.storage.list_files(project.s3_prefix)
                    for file_key in files:
                        self.storage.delete(file_key)
                    logger.info("S3 files deleted", project_id=str(project_id), files_deleted=len(files))
                except Exception as e:
                    logger.warning("S3 cleanup failed", project_id=str(project_id), error=str(e))
                    # Continue with DB deletion even if S3 fails

            # Delete project from DB (cascade deletes folders and files)
            success = self.db_service.delete_project(db, project_id)

            if success:
                logger.info("Project deleted with cleanup", project_id=str(project_id))
            else:
                logger.error("Failed to delete project from DB", project_id=str(project_id))

            return success

        except Exception as e:
            logger.error(
                "Delete project with cleanup failed",
                project_id=str(project_id),
                error=str(e),
                error_type=type(e).__name__,
            )
            return False

    def upload_file_to_project(
        self,
        db: Session,
        project_id: UUID,
        user_id: UUID,
        folder_name: str,
        filename: str,
        file_data: bytes,
    ) -> dict[str, Any] | None:
        """
        Upload file to project folder (S3 + DB)

        Args:
            db: Database session
            project_id: Project UUID
            user_id: User ID (for ownership check)
            folder_name: Target folder name
            filename: File name
            file_data: File bytes

        Returns:
            File data dictionary or None if failed
        """
        try:
            # Get project for ownership check
            project = self.db_service.get_project_by_id(db, project_id)
            if not project or project.user_id != user_id:
                logger.warning("Unauthorized file upload", project_id=str(project_id), user_id=str(user_id))
                return None

            # Get project with details to find folder
            project_details = self.db_service.get_project_with_details(db, project_id)
            if not project_details:
                return None

            # Find folder by name
            folder = next((f for f in project_details.folders if f.folder_name == folder_name), None)
            if not folder:
                logger.warning("Folder not found", folder_name=folder_name, project_id=str(project_id))
                return None

            # Detect file type and MIME type (business logic in transformer)
            file_type = detect_file_type(filename)
            mime_type = get_mime_type(filename)

            # Generate S3 key
            s3_key = f"{folder.s3_prefix}{filename}"
            relative_path = f"{folder_name}/{filename}"

            # Upload to S3
            try:
                self.storage.upload(file_data, s3_key, content_type=mime_type)
            except Exception as e:
                logger.error("S3 upload failed", s3_key=s3_key, error=str(e))
                return None

            # Create file record in DB
            file_record = self.db_service.create_file(
                db=db,
                project_id=project_id,
                folder_id=folder.id,
                filename=filename,
                relative_path=relative_path,
                s3_key=s3_key,
                file_type=file_type,
                mime_type=mime_type,
                file_size_bytes=len(file_data),
                storage_backend="s3",
            )

            if not file_record:
                logger.error("Failed to create file record in DB", s3_key=s3_key)
                # Try to cleanup S3
                with contextlib.suppress(Exception):
                    self.storage.delete(s3_key)
                return None

            logger.info("File uploaded to project", project_id=str(project_id), filename=filename, folder=folder_name)

            # Generate download URL
            download_url = self.storage.get_url(s3_key, expires_in=3600)

            # Transform to response (business logic in transformer)
            from business.song_project_transformer import transform_file_to_response

            return transform_file_to_response(file_record, download_url=download_url)

        except Exception as e:
            logger.error(
                "Upload file to project failed", project_id=str(project_id), error=str(e), error_type=type(e).__name__
            )
            return None


# Global orchestrator instance
song_project_orchestrator = SongProjectOrchestrator()
