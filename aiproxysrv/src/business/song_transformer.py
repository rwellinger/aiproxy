"""Song Transformer - Pure functions for song data transformations"""

from typing import Any


class SongTransformer:
    """Transform song and choice data to various formats (pure functions)"""

    @staticmethod
    def transform_song_to_list_format(song) -> dict[str, Any]:
        """
        Transform song object to list display format

        Pure function - no DB, no file system, fully unit-testable

        Args:
            song: Song model object

        Returns:
            Dict with list format fields
        """
        # Extract project info if available (relationship may be lazy-loaded)
        project_id = None
        project_name = None
        if hasattr(song, "project_id") and song.project_id:
            project_id = str(song.project_id)
            # Try to get project name from relationship (if eager-loaded)
            if hasattr(song, "project") and song.project:
                project_name = song.project.project_name

        return {
            "id": str(song.id),
            "lyrics": song.lyrics,
            "title": song.title,
            "model": song.model,
            "tags": song.tags,
            "workflow": song.workflow,
            "is_instrumental": song.is_instrumental,
            "project_id": project_id,
            "project_name": project_name,
            "created_at": song.created_at.isoformat() if song.created_at else None,
        }

    @staticmethod
    def transform_song_to_detail_format(song) -> dict[str, Any]:
        """
        Transform song object to detailed format with all choices

        Pure function - no DB, no file system, fully unit-testable

        Args:
            song: Song model object with choices relationship loaded

        Returns:
            Dict with detailed format including all choices
        """
        # Format choices
        choices_list = []
        for choice in song.choices:
            choice_data = {
                "id": str(choice.id),
                "mureka_choice_id": choice.mureka_choice_id,
                "choice_index": choice.choice_index,
                "mp3_url": choice.mp3_url,
                "flac_url": choice.flac_url,
                "video_url": choice.video_url,
                "image_url": choice.image_url,
                "stem_url": choice.stem_url,
                "stem_generated_at": choice.stem_generated_at.isoformat() if choice.stem_generated_at else None,
                "duration": choice.duration,
                "title": choice.title,
                "tags": choice.tags,
                "rating": choice.rating,
                "formattedDuration": SongTransformer.format_duration_from_ms(choice.duration)
                if choice.duration
                else None,
                "created_at": choice.created_at.isoformat() if choice.created_at else None,
            }
            choices_list.append(choice_data)

        # Format song data
        return {
            "id": str(song.id),
            "task_id": song.task_id,
            "job_id": song.job_id,
            "lyrics": song.lyrics,
            "prompt": song.prompt,
            "model": song.model,
            "title": song.title,
            "tags": song.tags,
            "workflow": song.workflow,
            "is_instrumental": song.is_instrumental,
            "status": song.status,
            "progress_info": song.progress_info,
            "error_message": song.error_message,
            "mureka_response": song.mureka_response,
            "mureka_status": song.mureka_status,
            "choices_count": len(choices_list),
            "choices": choices_list,
            "created_at": song.created_at.isoformat() if song.created_at else None,
            "updated_at": song.updated_at.isoformat() if song.updated_at else None,
            "completed_at": song.completed_at.isoformat() if song.completed_at else None,
        }

    @staticmethod
    def format_duration_from_ms(duration_ms: float) -> str:
        """
        Format duration from milliseconds to MM:SS format

        Pure function - no dependencies, fully unit-testable

        Args:
            duration_ms: Duration in milliseconds

        Returns:
            Formatted string in MM:SS format
        """
        if not duration_ms:
            return "00:00"

        total_seconds = int(duration_ms / 1000)
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
