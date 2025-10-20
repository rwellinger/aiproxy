"""Controller for sketch management"""

from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from db.sketch_service import sketch_service
from schemas.sketch_schemas import (
    SketchCreateRequest,
    SketchListResponse,
    SketchResponse,
    SketchUpdateRequest,
)
from utils.logger import logger


class SketchController:
    """Controller for sketch operations"""

    @staticmethod
    def create_sketch(db: Session, sketch_data: SketchCreateRequest) -> tuple[dict[str, Any], int]:
        """
        Create a new sketch

        Args:
            db: Database session
            sketch_data: Sketch creation data (Pydantic model)

        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            sketch = sketch_service.create_sketch(
                db=db,
                title=sketch_data.title,
                lyrics=sketch_data.lyrics,
                prompt=sketch_data.prompt,
                tags=sketch_data.tags,
            )

            if not sketch:
                return {"error": "Failed to create sketch"}, 500

            response = SketchResponse.model_validate(sketch)
            return {"data": response.model_dump(), "message": "Sketch created successfully"}, 201

        except Exception as e:
            logger.error("sketch_creation_error", error=str(e), error_type=type(e).__name__)
            return {"error": f"Failed to create sketch: {str(e)}"}, 500

    @staticmethod
    def get_sketches(
        db: Session,
        limit: int = 20,
        offset: int = 0,
        search: str = "",
        workflow: str | None = None,
        sort_by: str = "created_at",
        sort_direction: str = "desc",
    ) -> tuple[dict[str, Any], int]:
        """
        Get list of sketches with pagination, search and filtering

        Args:
            db: Database session
            limit: Number of sketches to return
            offset: Number of sketches to skip
            search: Search term to filter by title, lyrics, prompt, or tags
            workflow: Optional workflow filter (draft, used, archived)
            sort_by: Field to sort by (created_at, updated_at, title)
            sort_direction: Sort direction (asc, desc)

        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            result = sketch_service.get_sketches_paginated(
                db=db,
                limit=limit,
                offset=offset,
                search=search,
                workflow=workflow,
                sort_by=sort_by,
                sort_direction=sort_direction,
            )

            sketches = result.get("items", [])
            total = result.get("total", 0)

            # Convert sketches to Pydantic models
            sketch_responses = [SketchResponse.model_validate(sketch) for sketch in sketches]

            response = SketchListResponse(
                data=sketch_responses,
                total=total,
                limit=limit,
                offset=offset,
            )

            return response.model_dump(), 200

        except Exception as e:
            logger.error("sketch_list_error", error=str(e), error_type=type(e).__name__)
            return {"error": f"Failed to retrieve sketches: {str(e)}"}, 500

    @staticmethod
    def get_sketch_by_id(db: Session, sketch_id: str) -> tuple[dict[str, Any], int]:
        """
        Get a specific sketch by ID

        Args:
            db: Database session
            sketch_id: UUID of the sketch

        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Validate UUID format
            try:
                UUID(sketch_id)
            except ValueError:
                return {"error": "Invalid sketch ID format"}, 400

            sketch = sketch_service.get_sketch_by_id(db, sketch_id)

            if not sketch:
                return {"error": f"Sketch not found with ID: {sketch_id}"}, 404

            response = SketchResponse.model_validate(sketch)
            return {"data": response.model_dump()}, 200

        except Exception as e:
            logger.error("sketch_get_error", sketch_id=sketch_id, error=str(e), error_type=type(e).__name__)
            return {"error": f"Failed to retrieve sketch: {str(e)}"}, 500

    @staticmethod
    def update_sketch(db: Session, sketch_id: str, update_data: SketchUpdateRequest) -> tuple[dict[str, Any], int]:
        """
        Update an existing sketch

        Args:
            db: Database session
            sketch_id: UUID of the sketch
            update_data: Update data (Pydantic model)

        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Validate UUID format
            try:
                UUID(sketch_id)
            except ValueError:
                return {"error": "Invalid sketch ID format"}, 400

            # Get only the fields that were actually provided (exclude_unset=True)
            update_dict = update_data.model_dump(exclude_unset=True)

            if not update_dict:
                return {"error": "No fields to update"}, 400

            sketch = sketch_service.update_sketch(db=db, sketch_id=sketch_id, **update_dict)

            if not sketch:
                return {"error": f"Sketch not found with ID: {sketch_id}"}, 404

            response = SketchResponse.model_validate(sketch)
            return {"data": response.model_dump(), "message": "Sketch updated successfully"}, 200

        except Exception as e:
            logger.error("sketch_update_error", sketch_id=sketch_id, error=str(e), error_type=type(e).__name__)
            return {"error": f"Failed to update sketch: {str(e)}"}, 500

    @staticmethod
    def delete_sketch(db: Session, sketch_id: str) -> tuple[dict[str, Any], int]:
        """
        Delete a sketch

        Args:
            db: Database session
            sketch_id: UUID of the sketch

        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Validate UUID format
            try:
                UUID(sketch_id)
            except ValueError:
                return {"error": "Invalid sketch ID format"}, 400

            success = sketch_service.delete_sketch(db, sketch_id)

            if not success:
                return {"error": f"Sketch not found with ID: {sketch_id}"}, 404

            return {"message": "Sketch deleted successfully", "deleted": True}, 200

        except Exception as e:
            logger.error("sketch_delete_error", sketch_id=sketch_id, error=str(e), error_type=type(e).__name__)
            return {"error": f"Failed to delete sketch: {str(e)}"}, 500
