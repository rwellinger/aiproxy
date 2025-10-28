"""Song Orchestrator - Coordinates song operations (no testable business logic)"""

from typing import Any

from business.song_mureka_transformer import SongMurekaTransformer
from business.song_transformer import SongTransformer
from db.song_service import song_service
from utils.logger import logger


class SongOrchestratorError(Exception):
    """Base exception for song orchestration errors"""

    pass


class SongOrchestrator:
    """Orchestrates song operations (calls transformers + repository)"""

    def get_songs_with_pagination(
        self,
        limit: int = 20,
        offset: int = 0,
        status: str = None,
        search: str = "",
        sort_by: str = "created_at",
        sort_direction: str = "desc",
        workflow: str = None,
    ) -> dict[str, Any]:
        """
        Get paginated list of songs with search and filtering

        Args:
            limit: Number of songs to return
            offset: Number of songs to skip
            status: Optional status filter
            search: Search term for filtering
            sort_by: Field to sort by
            sort_direction: Sort direction
            workflow: Optional workflow filter

        Returns:
            Dict containing songs and pagination info
        """
        try:
            songs = song_service.get_songs_paginated(
                limit=limit,
                offset=offset,
                status=status,
                search=search,
                sort_by=sort_by,
                sort_direction=sort_direction,
                workflow=workflow,
            )
            total_count = song_service.get_total_songs_count(status=status, search=search, workflow=workflow)

            # Transform to API response format
            songs_list = [SongTransformer.transform_song_to_list_format(song) for song in songs]

            return {
                "songs": songs_list,
                "pagination": {
                    "total": total_count,
                    "limit": limit,
                    "offset": offset,
                    "has_more": offset + limit < total_count,
                },
            }

        except Exception as e:
            logger.error(f"Error retrieving songs: {e}")
            raise SongOrchestratorError(f"Failed to retrieve songs: {e}") from e

    def get_song_details(self, song_id: str) -> dict[str, Any] | None:
        """
        Get detailed information for a single song with all choices

        Args:
            song_id: ID of the song

        Returns:
            Dict containing song details with choices or None if not found
        """
        try:
            song = song_service.get_song_by_id(song_id)
            if not song:
                return None

            return SongTransformer.transform_song_to_detail_format(song)

        except Exception as e:
            logger.error(f"Error retrieving song {song_id}: {e}")
            raise SongOrchestratorError(f"Failed to retrieve song: {e}") from e

    def update_song_metadata(self, song_id: str, update_data: dict[str, Any]) -> dict[str, Any] | None:
        """
        Update song metadata with validation

        Args:
            song_id: ID of the song to update
            update_data: Data to update

        Returns:
            Updated song data or None if not found
        """
        try:
            # Check if song exists
            song = song_service.get_song_by_id(song_id)
            if not song:
                return None

            # Validate and filter allowed fields
            allowed_fields = ["title", "tags", "workflow"]
            filtered_data = {k: v for k, v in update_data.items() if k in allowed_fields}

            if not filtered_data:
                raise SongOrchestratorError("No valid fields provided for update")

            # Update the song
            updated_song = song_service.update_song(song_id, filtered_data)
            if not updated_song:
                raise SongOrchestratorError("Failed to update song")

            logger.info(f"Song {song_id} updated successfully")
            return {
                "id": str(updated_song.id),
                "title": updated_song.title,
                "tags": updated_song.tags,
                "workflow": updated_song.workflow,
                "updated_at": updated_song.updated_at.isoformat() if updated_song.updated_at else None,
            }

        except Exception as e:
            logger.error(f"Error updating song {song_id}: {e}")
            raise SongOrchestratorError(f"Failed to update song: {e}") from e

    def delete_single_song(self, song_id: str) -> bool:
        """
        Delete a single song including all choices

        Args:
            song_id: ID of the song to delete

        Returns:
            True if successful, False if song not found
        """
        try:
            song = song_service.get_song_by_id(song_id)
            if not song:
                return False

            success = song_service.delete_song_by_id(song_id)
            if success:
                logger.info(f"Song {song_id} and its choices deleted successfully")
                return True
            else:
                raise SongOrchestratorError("Failed to delete song")

        except Exception as e:
            logger.error(f"Error deleting song {song_id}: {type(e).__name__}: {e}")
            raise SongOrchestratorError(f"Failed to delete song: {e}") from e

    def bulk_delete_songs(self, song_ids: list[str]) -> dict[str, Any]:
        """
        Delete multiple songs with detailed results

        Args:
            song_ids: List of song IDs to delete

        Returns:
            Dict containing deletion results and summary
        """
        if not song_ids:
            raise SongOrchestratorError("No song IDs provided")

        if len(song_ids) > 100:
            raise SongOrchestratorError("Too many songs (max 100 per request)")

        results = {"deleted": [], "not_found": [], "errors": []}

        for song_id in song_ids:
            try:
                song = song_service.get_song_by_id(song_id)
                if not song:
                    results["not_found"].append(song_id)
                    continue

                success = song_service.delete_song_by_id(song_id)
                if success:
                    results["deleted"].append(song_id)
                    logger.info(f"Song {song_id} and its choices deleted successfully")
                else:
                    results["errors"].append({"id": song_id, "error": "Failed to delete song"})

            except Exception as e:
                error_msg = f"{type(e).__name__}: {e}"
                results["errors"].append({"id": song_id, "error": error_msg})
                logger.error(f"Error deleting song {song_id}: {error_msg}")

        summary = {
            "total_requested": len(song_ids),
            "deleted": len(results["deleted"]),
            "not_found": len(results["not_found"]),
            "errors": len(results["errors"]),
        }

        logger.info(f"Bulk delete completed: {summary}")
        return {"summary": summary, "results": results}

    def update_choice_rating(self, choice_id: str, rating: int | None) -> dict[str, Any] | None:
        """
        Update rating for a song choice

        Args:
            choice_id: ID of the choice
            rating: Rating value (0, 1, or None)

        Returns:
            Updated choice data or None if not found
        """
        try:
            # Validate rating value
            if rating is not None and rating not in [0, 1]:
                raise SongOrchestratorError("Rating must be null, 0 (thumbs down), or 1 (thumbs up)")

            # Check if choice exists
            choice = song_service.get_choice_by_id(choice_id)
            if not choice:
                return None

            # Update rating
            success = song_service.update_choice_rating(choice_id, rating)
            if not success:
                raise SongOrchestratorError("Failed to update choice rating")

            logger.info(f"Choice {choice_id} rating updated to {rating}")
            return {"id": choice_id, "rating": rating, "message": "Rating updated successfully"}

        except Exception as e:
            logger.error(f"Error updating choice rating {choice_id}: {e}")
            raise SongOrchestratorError(f"Failed to update choice rating: {e}") from e

    def process_song_completion(self, task_id: str, result_data: dict[str, Any]) -> bool:
        """
        Process MUREKA song completion with business logic transformation

        This method orchestrates:
        1. Parse MUREKA API response (business layer)
        2. Update database with parsed data (repository layer)

        Args:
            task_id: Celery task ID
            result_data: Raw MUREKA API response dict

        Returns:
            True if successful, False otherwise

        Example result_data:
        {
            "status": "SUCCESS",
            "result": {
                "status": "succeeded",
                "model": "mureka-7.5",
                "choices": [...]
            },
            "completed_at": 1234567890
        }
        """
        try:
            # Business logic: Parse MUREKA response
            logger.info("Parsing MUREKA result", task_id=task_id)
            parsed = SongMurekaTransformer.parse_mureka_result(result_data)

            # Repository: Update song with parsed data
            success = song_service.update_song_result(task_id, parsed)

            if success:
                logger.info(
                    "Song completion processed",
                    task_id=task_id,
                    model=parsed.get("model"),
                    choices_count=parsed.get("choices_count", 0),
                )
            else:
                logger.warning("Failed to update song result", task_id=task_id)

            return success

        except Exception as e:
            logger.error(
                "Song completion processing failed", task_id=task_id, error=str(e), error_type=type(e).__name__
            )
            raise SongOrchestratorError(f"Failed to process song completion: {e}") from e
