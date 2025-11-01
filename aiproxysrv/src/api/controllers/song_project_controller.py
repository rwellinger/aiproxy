"""Controller for song project management"""

from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from business.song_project_orchestrator import song_project_orchestrator
from schemas.common_schemas import PaginationMeta
from schemas.song_project_schemas import (
    ProjectCreateRequest,
    ProjectDetailResponse,
    ProjectListResponse,
    ProjectResponse,
    ProjectUpdateRequest,
)
from utils.logger import logger


class SongProjectController:
    """Controller for song project operations (HTTP handling only)"""

    @staticmethod
    def create_project(db: Session, user_id: UUID, project_data: ProjectCreateRequest) -> tuple[dict[str, Any], int]:
        """
        Create a new project with default folder structure

        Args:
            db: Database session
            user_id: User ID (from JWT)
            project_data: Project creation data (Pydantic model)

        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            result = song_project_orchestrator.create_project_with_structure(
                db=db,
                user_id=user_id,
                project_name=project_data.project_name,
                tags=project_data.tags,
                description=project_data.description,
            )

            if not result:
                return {"error": "Failed to create project"}, 500

            response = ProjectResponse(**result)
            return {"data": response.model_dump(), "message": "Project created successfully"}, 201

        except Exception as e:
            logger.error("Project creation error", error=str(e), error_type=type(e).__name__)
            return {"error": f"Failed to create project: {str(e)}"}, 500

    @staticmethod
    def get_projects(
        db: Session,
        user_id: UUID,
        limit: int = 20,
        offset: int = 0,
        search: str = "",
        tags: str | None = None,
    ) -> tuple[dict[str, Any], int]:
        """
        Get list of projects for user (paginated)

        Args:
            db: Database session
            user_id: User ID (from JWT)
            limit: Items per page
            offset: Offset for pagination
            search: Search term
            tags: Comma-separated tags

        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            result = song_project_orchestrator.list_projects(
                db=db,
                user_id=user_id,
                limit=limit,
                offset=offset,
                search=search,
                tags=tags,
            )

            projects = result.get("projects", [])
            pagination_data = result.get("pagination", {})

            # Convert to Pydantic models
            project_responses = [ProjectResponse(**p) for p in projects]

            # Create pagination metadata
            pagination = PaginationMeta(
                total=pagination_data.get("total", 0),
                offset=pagination_data.get("offset", 0),
                limit=pagination_data.get("limit", limit),
                has_more=pagination_data.get("has_more", False),
            )

            response = ProjectListResponse(
                data=project_responses,
                pagination=pagination,
            )

            return response.model_dump(), 200

        except Exception as e:
            logger.error("Project list error", error=str(e), error_type=type(e).__name__)
            return {"error": f"Failed to retrieve projects: {str(e)}"}, 500

    @staticmethod
    def get_project_by_id(db: Session, user_id: UUID, project_id: str) -> tuple[dict[str, Any], int]:
        """
        Get a specific project by ID (without details)

        Args:
            db: Database session
            user_id: User ID (from JWT)
            project_id: Project UUID

        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Validate UUID format
            try:
                project_uuid = UUID(project_id)
            except ValueError:
                return {"error": "Invalid project ID format"}, 400

            result = song_project_orchestrator.get_project_by_id(
                db=db,
                project_id=project_uuid,
                user_id=user_id,
            )

            if not result:
                return {"error": f"Project not found with ID: {project_id}"}, 404

            response = ProjectResponse(**result)
            return {"data": response.model_dump()}, 200

        except Exception as e:
            logger.error("Project get error", project_id=project_id, error=str(e), error_type=type(e).__name__)
            return {"error": f"Failed to retrieve project: {str(e)}"}, 500

    @staticmethod
    def get_project_with_details(db: Session, user_id: UUID, project_id: str) -> tuple[dict[str, Any], int]:
        """
        Get a specific project with all folders and files

        Args:
            db: Database session
            user_id: User ID (from JWT)
            project_id: Project UUID

        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Validate UUID format
            try:
                project_uuid = UUID(project_id)
            except ValueError:
                return {"error": "Invalid project ID format"}, 400

            result = song_project_orchestrator.get_project_with_details(
                db=db,
                project_id=project_uuid,
                user_id=user_id,
            )

            if not result:
                return {"error": f"Project not found with ID: {project_id}"}, 404

            response = ProjectDetailResponse(**result)
            return {"data": response.model_dump()}, 200

        except Exception as e:
            logger.error("Project detail error", project_id=project_id, error=str(e), error_type=type(e).__name__)
            return {"error": f"Failed to retrieve project details: {str(e)}"}, 500

    @staticmethod
    def update_project(
        db: Session,
        user_id: UUID,
        project_id: str,
        update_data: ProjectUpdateRequest,
    ) -> tuple[dict[str, Any], int]:
        """
        Update an existing project

        Args:
            db: Database session
            user_id: User ID (from JWT)
            project_id: Project UUID
            update_data: Update data (Pydantic model)

        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Validate UUID format
            try:
                project_uuid = UUID(project_id)
            except ValueError:
                return {"error": "Invalid project ID format"}, 400

            # Convert Pydantic model to dict (exclude None values)
            update_dict = update_data.model_dump(exclude_none=True)

            if not update_dict:
                return {"error": "No fields to update"}, 400

            result = song_project_orchestrator.update_project(
                db=db,
                project_id=project_uuid,
                user_id=user_id,
                update_data=update_dict,
            )

            if not result:
                return {"error": "Failed to update project"}, 500

            response = ProjectResponse(**result)
            return {"data": response.model_dump(), "message": "Project updated successfully"}, 200

        except Exception as e:
            logger.error("Project update error", project_id=project_id, error=str(e), error_type=type(e).__name__)
            return {"error": f"Failed to update project: {str(e)}"}, 500

    @staticmethod
    def delete_project(db: Session, user_id: UUID, project_id: str) -> tuple[dict[str, Any], int]:
        """
        Delete a project (with S3 cleanup)

        Args:
            db: Database session
            user_id: User ID (from JWT)
            project_id: Project UUID

        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Validate UUID format
            try:
                project_uuid = UUID(project_id)
            except ValueError:
                return {"error": "Invalid project ID format"}, 400

            success = song_project_orchestrator.delete_project_with_cleanup(
                db=db,
                project_id=project_uuid,
                user_id=user_id,
            )

            if not success:
                return {"error": "Failed to delete project"}, 500

            return {"message": "Project deleted successfully"}, 200

        except Exception as e:
            logger.error("Project deletion error", project_id=project_id, error=str(e), error_type=type(e).__name__)
            return {"error": f"Failed to delete project: {str(e)}"}, 500


# Global controller instance
song_project_controller = SongProjectController()
