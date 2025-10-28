"""Sketch Service - Database operations for sketch management"""

import traceback
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from db.models import SongSketch
from utils.logger import logger


class SketchService:
    """Service for sketch database operations"""

    def create_sketch(
        self,
        db: Session,
        title: str | None,
        lyrics: str | None,
        prompt: str,
        tags: str | None = None,
        workflow: str = "draft",
        description_long: str | None = None,
        description_short: str | None = None,
        description_tags: str | None = None,
        info: str | None = None,
    ) -> SongSketch | None:
        """
        Create a new sketch record in the database

        Args:
            db: Database session
            title: Sketch title (optional)
            lyrics: Song lyrics (optional)
            prompt: Music style prompt (required)
            tags: Comma-separated tags (optional)
            workflow: Workflow status (default: draft)
            description_long: Long description for release (optional)
            description_short: Short description for release (optional)
            description_tags: Release tags (optional)
            info: Working notes (optional)

        Returns:
            SongSketch instance if successful, None otherwise
        """
        try:
            sketch = SongSketch(
                title=title,
                lyrics=lyrics,
                prompt=prompt,
                tags=tags,
                workflow=workflow,
                description_long=description_long,
                description_short=description_short,
                description_tags=description_tags,
                info=info,
            )

            db.add(sketch)
            db.commit()
            db.refresh(sketch)

            logger.info(
                "sketch_created",
                sketch_id=str(sketch.id),
                title=title,
                workflow=workflow,
                has_lyrics=bool(lyrics),
            )
            return sketch

        except SQLAlchemyError as e:
            db.rollback()
            logger.error("sketch_creation_db_error", error=str(e), error_type=type(e).__name__)
            return None
        except Exception as e:
            logger.error("sketch_creation_failed", error=str(e), error_type=type(e).__name__)
            return None

    def get_sketch_by_id(self, db: Session, sketch_id: str | UUID) -> SongSketch | None:
        """
        Get sketch by ID

        Args:
            db: Database session
            sketch_id: UUID of the sketch

        Returns:
            SongSketch instance if found, None otherwise
        """
        try:
            sketch = db.query(SongSketch).filter(SongSketch.id == sketch_id).first()
            if sketch:
                logger.debug("Sketch retrieved", sketch_id=str(sketch_id), workflow=sketch.workflow)
            else:
                logger.debug("Sketch not found", sketch_id=str(sketch_id))
            return sketch
        except Exception as e:
            logger.error(
                "error_getting_sketch_by_id", sketch_id=str(sketch_id), error=str(e), error_type=type(e).__name__
            )
            return None

    def get_sketches_paginated(
        self,
        db: Session,
        limit: int = 20,
        offset: int = 0,
        search: str = "",
        workflow: str | None = None,
        sort_by: str = "created_at",
        sort_direction: str = "desc",
    ) -> dict[str, Any]:
        """
        Get paginated list of sketches with search and filtering

        Args:
            db: Database session
            limit: Number of sketches to return (default 20)
            offset: Number of sketches to skip (default 0)
            search: Search term to filter by title, lyrics, prompt, or tags
            workflow: Optional workflow filter (draft, used, archived)
            sort_by: Field to sort by (created_at, updated_at, title)
            sort_direction: Sort direction (asc, desc)

        Returns:
            Dictionary with 'items' (list of sketches) and 'total' (count)
        """
        try:
            query = db.query(SongSketch)

            # Apply workflow filter
            if workflow:
                # Explicit workflow filter (draft, used, archived)
                query = query.filter(SongSketch.workflow == workflow)
            else:
                # When no workflow is specified, exclude archived sketches
                query = query.filter(SongSketch.workflow != "archived")

            # Apply search filter if provided
            if search:
                search_term = f"%{search}%"
                query = query.filter(
                    or_(
                        SongSketch.title.ilike(search_term),
                        SongSketch.lyrics.ilike(search_term),
                        SongSketch.prompt.ilike(search_term),
                        SongSketch.tags.ilike(search_term),
                    )
                )

            # Get total count before pagination
            total_count = query.count()

            # Apply sorting
            if sort_by == "title":
                # Handle null titles by treating them as empty strings for sorting
                if sort_direction == "desc":
                    query = query.order_by(SongSketch.title.desc().nullslast())
                else:
                    query = query.order_by(SongSketch.title.asc().nullsfirst())
            elif sort_by == "updated_at":
                if sort_direction == "desc":
                    query = query.order_by(SongSketch.updated_at.desc().nullslast())
                else:
                    query = query.order_by(SongSketch.updated_at.asc().nullsfirst())
            else:  # default to created_at
                if sort_direction == "desc":
                    query = query.order_by(SongSketch.created_at.desc())
                else:
                    query = query.order_by(SongSketch.created_at.asc())

            # Apply pagination
            sketches = query.limit(limit).offset(offset).all()

            logger.debug(
                "sketches_retrieved_paginated",
                count=len(sketches),
                total=total_count,
                limit=limit,
                offset=offset,
                workflow=workflow,
                search=search,
                sort_by=sort_by,
                sort_direction=sort_direction,
            )

            return {"items": sketches, "total": total_count}
        except Exception as e:
            logger.error(
                "error_getting_paginated_sketches",
                error=str(e),
                error_type=type(e).__name__,
                stacktrace=traceback.format_exc(),
            )
            return {"items": [], "total": 0}

    def update_sketch(
        self,
        db: Session,
        sketch_id: str | UUID,
        title: str | None = None,
        lyrics: str | None = None,
        prompt: str | None = None,
        tags: str | None = None,
        workflow: str | None = None,
        description_long: str | None = None,
        description_short: str | None = None,
        description_tags: str | None = None,
        info: str | None = None,
    ) -> SongSketch | None:
        """
        Update an existing sketch

        Args:
            db: Database session
            sketch_id: UUID of the sketch
            title: New title (optional)
            lyrics: New lyrics (optional)
            prompt: New music style prompt (optional)
            tags: New tags (optional)
            workflow: New workflow status (optional)
            description_long: Long description for release (optional)
            description_short: Short description for release (optional)
            description_tags: Release tags (optional)
            info: Working notes (optional)

        Returns:
            Updated SongSketch instance if successful, None otherwise
        """
        try:
            sketch = db.query(SongSketch).filter(SongSketch.id == sketch_id).first()
            if not sketch:
                logger.warning("Sketch not found for update", sketch_id=str(sketch_id))
                return None

            # Track which fields are being updated
            updated_fields = []

            # Update only provided fields
            # IMPORTANT: String normalization (trim, empty->None) is handled by business layer
            if title is not None:
                sketch.title = title
                updated_fields.append("title")
            if lyrics is not None:
                sketch.lyrics = lyrics
                updated_fields.append("lyrics")
            if prompt is not None:
                sketch.prompt = prompt
                updated_fields.append("prompt")
            if tags is not None:
                sketch.tags = tags
                updated_fields.append("tags")
            if workflow is not None:
                sketch.workflow = workflow
                updated_fields.append("workflow")
            if description_long is not None:
                sketch.description_long = description_long
                updated_fields.append("description_long")
            if description_short is not None:
                sketch.description_short = description_short
                updated_fields.append("description_short")
            if description_tags is not None:
                sketch.description_tags = description_tags
                updated_fields.append("description_tags")
            if info is not None:
                sketch.info = info
                updated_fields.append("info")

            # Update timestamp
            sketch.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(sketch)

            logger.info("Sketch updated", sketch_id=str(sketch_id), fields_updated=updated_fields)
            return sketch

        except SQLAlchemyError as e:
            db.rollback()
            logger.error("sketch_update_db_error", sketch_id=str(sketch_id), error=str(e), error_type=type(e).__name__)
            return None
        except Exception as e:
            logger.error(
                "sketch_update_failed",
                sketch_id=str(sketch_id),
                error=str(e),
                error_type=type(e).__name__,
                stacktrace=traceback.format_exc(),
            )
            return None

    def delete_sketch(self, db: Session, sketch_id: str | UUID) -> bool:
        """
        Delete a sketch by ID

        Args:
            db: Database session
            sketch_id: UUID of the sketch

        Returns:
            True if successful, False otherwise
        """
        try:
            sketch = db.query(SongSketch).filter(SongSketch.id == sketch_id).first()
            if sketch:
                db.delete(sketch)
                db.commit()
                logger.info("Sketch deleted", sketch_id=str(sketch_id))
                return True
            logger.warning("Sketch not found for deletion", sketch_id=str(sketch_id))
            return False
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(
                "sketch_deletion_db_error", sketch_id=str(sketch_id), error=str(e), error_type=type(e).__name__
            )
            return False
        except Exception as e:
            logger.error(
                "sketch_deletion_failed",
                sketch_id=str(sketch_id),
                error=str(e),
                error_type=type(e).__name__,
                stacktrace=traceback.format_exc(),
            )
            return False

    def mark_sketch_as_used(self, db: Session, sketch_id: str | UUID) -> SongSketch | None:
        """
        Mark sketch as used (after song generation)

        Args:
            db: Database session
            sketch_id: UUID of the sketch

        Returns:
            Updated SongSketch instance if successful, None otherwise
        """
        try:
            sketch = db.query(SongSketch).filter(SongSketch.id == sketch_id).first()
            if not sketch:
                logger.warning("Sketch not found for mark as used", sketch_id=str(sketch_id))
                return None

            sketch.workflow = "used"
            sketch.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(sketch)

            logger.info("Sketch marked as used", sketch_id=str(sketch_id))
            return sketch

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(
                "sketch_mark_as_used_db_error", sketch_id=str(sketch_id), error=str(e), error_type=type(e).__name__
            )
            return None
        except Exception as e:
            logger.error(
                "sketch_mark_as_used_failed",
                sketch_id=str(sketch_id),
                error=str(e),
                error_type=type(e).__name__,
                stacktrace=traceback.format_exc(),
            )
            return None


# Global service instance
sketch_service = SketchService()
