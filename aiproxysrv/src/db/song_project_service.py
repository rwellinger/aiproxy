"""Song Project Service - Database operations for song project management"""

import traceback
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

from db.models import ProjectFile, ProjectFolder, SongProject
from utils.logger import logger


class SongProjectService:
    """Service for song project database operations (CRUD only, NO business logic)"""

    def create_project(
        self,
        db: Session,
        user_id: UUID,
        project_name: str,
        s3_prefix: str | None = None,
        tags: list[str] | None = None,
        description: str | None = None,
    ) -> SongProject | None:
        """
        Create a new song project record

        Args:
            db: Database session
            user_id: User ID (from JWT)
            project_name: Project name
            s3_prefix: S3 prefix for storage
            tags: List of tags
            description: Project description

        Returns:
            SongProject instance if successful, None otherwise
        """
        try:
            project = SongProject(
                user_id=user_id,
                project_name=project_name,
                s3_prefix=s3_prefix,
                tags=tags or [],
                description=description,
                sync_status="local",
            )

            db.add(project)
            db.commit()
            db.refresh(project)

            logger.info(
                "Song project created", project_id=str(project.id), project_name=project_name, user_id=str(user_id)
            )
            return project

        except SQLAlchemyError as e:
            db.rollback()
            logger.error("Project creation DB error", error=str(e), error_type=type(e).__name__)
            return None
        except Exception as e:
            logger.error("Project creation failed", error=str(e), error_type=type(e).__name__)
            return None

    def get_project_by_id(self, db: Session, project_id: UUID) -> SongProject | None:
        """
        Get project by ID (without relationships)

        Args:
            db: Database session
            project_id: Project UUID

        Returns:
            SongProject instance if found, None otherwise
        """
        try:
            project = db.query(SongProject).filter(SongProject.id == project_id).first()
            if project:
                logger.debug("Project retrieved", project_id=str(project_id))
            else:
                logger.debug("Project not found", project_id=str(project_id))
            return project
        except Exception as e:
            logger.error(
                "Error getting project by ID", project_id=str(project_id), error=str(e), error_type=type(e).__name__
            )
            return None

    def get_project_with_details(self, db: Session, project_id: UUID) -> SongProject | None:
        """
        Get project with all folders and files (eager loading)

        Args:
            db: Database session
            project_id: Project UUID

        Returns:
            SongProject instance with folders and files, None if not found
        """
        try:
            project = (
                db.query(SongProject)
                .options(
                    joinedload(SongProject.folders).joinedload(ProjectFolder.files),
                    joinedload(SongProject.files),
                )
                .filter(SongProject.id == project_id)
                .first()
            )
            if project:
                logger.debug(
                    "Project with details retrieved", project_id=str(project_id), folder_count=len(project.folders)
                )
            else:
                logger.debug("Project not found", project_id=str(project_id))
            return project
        except Exception as e:
            logger.error(
                "Error getting project with details",
                project_id=str(project_id),
                error=str(e),
                error_type=type(e).__name__,
            )
            return None

    def get_projects_paginated(
        self,
        db: Session,
        user_id: UUID,
        limit: int = 20,
        offset: int = 0,
        search: str = "",
        tags: str | None = None,
        sort_by: str = "created_at",
        sort_direction: str = "desc",
    ) -> dict[str, Any]:
        """
        Get paginated list of projects for a user

        Args:
            db: Database session
            user_id: User ID (from JWT)
            limit: Number of projects to return
            offset: Number of projects to skip
            search: Search term (project_name, description)
            tags: Comma-separated tags for filtering
            sort_by: Field to sort by (created_at, updated_at, project_name)
            sort_direction: Sort direction (asc, desc)

        Returns:
            Dictionary with 'items' (list of projects) and 'total' (count)
        """
        try:
            query = db.query(SongProject).filter(SongProject.user_id == user_id)

            # Apply search filter
            if search:
                search_term = f"%{search}%"
                query = query.filter(
                    or_(
                        SongProject.project_name.ilike(search_term),
                        SongProject.description.ilike(search_term),
                    )
                )

            # Apply tags filter (if provided)
            if tags:
                tag_list = [tag.strip() for tag in tags.split(",")]
                # PostgreSQL ARRAY overlap operator
                query = query.filter(SongProject.tags.overlap(tag_list))

            # Get total count before pagination
            total_count = query.count()

            # Apply sorting
            if sort_by == "project_name":
                if sort_direction == "desc":
                    query = query.order_by(SongProject.project_name.desc())
                else:
                    query = query.order_by(SongProject.project_name.asc())
            elif sort_by == "updated_at":
                if sort_direction == "desc":
                    query = query.order_by(SongProject.updated_at.desc().nullslast())
                else:
                    query = query.order_by(SongProject.updated_at.asc().nullsfirst())
            else:  # default to created_at
                if sort_direction == "desc":
                    query = query.order_by(SongProject.created_at.desc())
                else:
                    query = query.order_by(SongProject.created_at.asc())

            # Apply pagination
            projects = query.limit(limit).offset(offset).all()

            logger.debug(
                "Projects retrieved paginated",
                count=len(projects),
                total=total_count,
                limit=limit,
                offset=offset,
                user_id=str(user_id),
                search=search,
                tags=tags,
            )

            return {"items": projects, "total": total_count}
        except Exception as e:
            logger.error(
                "Error getting paginated projects",
                error=str(e),
                error_type=type(e).__name__,
                stacktrace=traceback.format_exc(),
            )
            return {"items": [], "total": 0}

    def update_project(
        self,
        db: Session,
        project_id: UUID,
        project_name: str | None = None,
        tags: list[str] | None = None,
        description: str | None = None,
        sync_status: str | None = None,
        last_sync_at: datetime | None = None,
        cover_image_id: UUID | None = None,
        total_files: int | None = None,
        total_size_bytes: int | None = None,
    ) -> SongProject | None:
        """
        Update an existing project

        Args:
            db: Database session
            project_id: Project UUID
            project_name: New project name (optional)
            tags: New tags list (optional)
            description: New description (optional)
            sync_status: New sync status (optional)
            last_sync_at: Last sync timestamp (optional)
            cover_image_id: Cover image UUID (optional)
            total_files: Total file count (optional)
            total_size_bytes: Total size in bytes (optional)

        Returns:
            Updated SongProject instance if successful, None otherwise
        """
        try:
            project = db.query(SongProject).filter(SongProject.id == project_id).first()
            if not project:
                logger.warning("Project not found for update", project_id=str(project_id))
                return None

            # Track which fields are being updated
            updated_fields = []

            # Update only provided fields
            if project_name is not None:
                project.project_name = project_name
                updated_fields.append("project_name")
            if tags is not None:
                project.tags = tags
                updated_fields.append("tags")
            if description is not None:
                project.description = description
                updated_fields.append("description")
            if sync_status is not None:
                project.sync_status = sync_status
                updated_fields.append("sync_status")
            if last_sync_at is not None:
                project.last_sync_at = last_sync_at
                updated_fields.append("last_sync_at")
            if cover_image_id is not None:
                project.cover_image_id = cover_image_id
                updated_fields.append("cover_image_id")
            if total_files is not None:
                project.total_files = total_files
                updated_fields.append("total_files")
            if total_size_bytes is not None:
                project.total_size_bytes = total_size_bytes
                updated_fields.append("total_size_bytes")

            # Update timestamp
            project.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(project)

            logger.info("Project updated", project_id=str(project_id), fields_updated=updated_fields)
            return project

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(
                "Project update DB error", project_id=str(project_id), error=str(e), error_type=type(e).__name__
            )
            return None
        except Exception as e:
            logger.error(
                "Project update failed",
                project_id=str(project_id),
                error=str(e),
                error_type=type(e).__name__,
                stacktrace=traceback.format_exc(),
            )
            return None

    def delete_project(self, db: Session, project_id: UUID) -> bool:
        """
        Delete a project by ID (cascade deletes folders, files)

        Args:
            db: Database session
            project_id: Project UUID

        Returns:
            True if successful, False otherwise
        """
        try:
            project = db.query(SongProject).filter(SongProject.id == project_id).first()
            if project:
                db.delete(project)
                db.commit()
                logger.info("Project deleted", project_id=str(project_id))
                return True
            logger.warning("Project not found for deletion", project_id=str(project_id))
            return False
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(
                "Project deletion DB error", project_id=str(project_id), error=str(e), error_type=type(e).__name__
            )
            return False
        except Exception as e:
            logger.error(
                "Project deletion failed",
                project_id=str(project_id),
                error=str(e),
                error_type=type(e).__name__,
                stacktrace=traceback.format_exc(),
            )
            return False

    def create_folder(
        self,
        db: Session,
        project_id: UUID,
        folder_name: str,
        folder_type: str | None = None,
        s3_prefix: str | None = None,
        custom_icon: str | None = None,
    ) -> ProjectFolder | None:
        """
        Create a project folder

        Args:
            db: Database session
            project_id: Parent project UUID
            folder_name: Folder name
            folder_type: Folder type (arrangement, ai, cover, etc.)
            s3_prefix: S3 prefix for this folder
            custom_icon: Custom icon name

        Returns:
            ProjectFolder instance if successful, None otherwise
        """
        try:
            folder = ProjectFolder(
                project_id=project_id,
                folder_name=folder_name,
                folder_type=folder_type,
                s3_prefix=s3_prefix,
                custom_icon=custom_icon,
            )

            db.add(folder)
            db.commit()
            db.refresh(folder)

            logger.info("Folder created", folder_id=str(folder.id), folder_name=folder_name, project_id=str(project_id))
            return folder

        except SQLAlchemyError as e:
            db.rollback()
            logger.error("Folder creation DB error", error=str(e), error_type=type(e).__name__)
            return None
        except Exception as e:
            logger.error("Folder creation failed", error=str(e), error_type=type(e).__name__)
            return None

    def create_file(
        self,
        db: Session,
        project_id: UUID,
        folder_id: UUID | None,
        filename: str,
        relative_path: str,
        s3_key: str | None = None,
        file_type: str | None = None,
        mime_type: str | None = None,
        file_size_bytes: int | None = None,
        file_hash: str | None = None,
        storage_backend: str = "s3",
    ) -> ProjectFile | None:
        """
        Create a project file record

        Args:
            db: Database session
            project_id: Parent project UUID
            folder_id: Parent folder UUID (optional)
            filename: File name
            relative_path: Relative path within project
            s3_key: S3 key for storage
            file_type: File type (audio, image, document, etc.)
            mime_type: MIME type
            file_size_bytes: File size in bytes
            file_hash: File hash (SHA256)
            storage_backend: Storage backend (s3, local)

        Returns:
            ProjectFile instance if successful, None otherwise
        """
        try:
            file = ProjectFile(
                project_id=project_id,
                folder_id=folder_id,
                filename=filename,
                relative_path=relative_path,
                s3_key=s3_key,
                file_type=file_type,
                mime_type=mime_type,
                file_size_bytes=file_size_bytes,
                file_hash=file_hash,
                storage_backend=storage_backend,
                is_synced=False,
            )

            db.add(file)
            db.commit()
            db.refresh(file)

            logger.info("File created", file_id=str(file.id), filename=filename, project_id=str(project_id))
            return file

        except SQLAlchemyError as e:
            db.rollback()
            logger.error("File creation DB error", error=str(e), error_type=type(e).__name__)
            return None
        except Exception as e:
            logger.error("File creation failed", error=str(e), error_type=type(e).__name__)
            return None


# Global service instance
song_project_service = SongProjectService()
