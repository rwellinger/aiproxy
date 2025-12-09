"""MUREKA Response Transformer - Pure functions for parsing MUREKA API responses"""

from typing import Any


class SongMurekaTransformer:
    """Parse and transform MUREKA API responses to database format (pure functions)"""

    @staticmethod
    def parse_mureka_result(result_data: dict[str, Any]) -> dict[str, Any]:
        """
        Parse complete MUREKA API response and extract fields for database storage

        Pure function - no DB, no file system, fully unit-testable

        Expected MUREKA structure:
        {
            "status": "SUCCESS",
            "result": {
                "status": "succeeded",
                "model": "mureka-7.5",
                "choices": [
                    {
                        "id": "...",
                        "index": 0,
                        "url": "https://...",
                        "flac_url": "https://...",
                        "video_url": "https://...",
                        "image_url": "https://...",
                        "duration": 30567.89,
                        "title": "Song Title",
                        "tags": ["pop", "upbeat"]
                    }
                ]
            },
            "completed_at": 1234567890
        }

        Args:
            result_data: Complete MUREKA API response dict

        Returns:
            Dict with parsed fields:
            {
                "mureka_result": {...},  # Full result object
                "mureka_status": "succeeded",
                "model": "mureka-7.5",
                "choices": [...],  # Parsed choices in DB format
                "completed_at": datetime,
                "choices_count": 2
            }
        """
        parsed = {
            "mureka_result": None,
            "mureka_status": None,
            "model": None,
            "choices": [],
            "completed_at": None,
            "choices_count": 0,
        }

        # Extract result object (check for None, not falsy - empty dict {} is valid!)
        if "result" in result_data and result_data["result"] is not None:
            mureka_result = result_data["result"]
            parsed["mureka_result"] = mureka_result

            # Extract status
            parsed["mureka_status"] = mureka_result.get("status")

            # Extract model (actual model used by MUREKA, not request model)
            parsed["model"] = mureka_result.get("model")

            # Parse choices array
            choices_data = mureka_result.get("choices", [])
            parsed["choices_count"] = len(choices_data)

            for choice_data in choices_data:
                choice_dict = SongMurekaTransformer.transform_choice_to_db_format(choice_data)
                parsed["choices"].append(choice_dict)

        # Extract completion timestamp
        if "completed_at" in result_data:
            parsed["completed_at"] = result_data["completed_at"]

        return parsed

    @staticmethod
    def transform_choice_to_db_format(choice_data: dict[str, Any]) -> dict[str, Any]:
        """
        Transform single MUREKA choice to database format

        Pure function - no DB, no dependencies

        Args:
            choice_data: Single choice from MUREKA response

        Returns:
            Dict ready for SongChoice model creation
        """
        return {
            "mureka_choice_id": choice_data.get("id"),
            "choice_index": choice_data.get("index"),
            "mp3_url": choice_data.get("url"),
            "flac_url": choice_data.get("flac_url"),
            "wav_url": choice_data.get("wav_url"),
            "video_url": choice_data.get("video_url"),
            "image_url": choice_data.get("image_url"),
            "duration": SongMurekaTransformer.parse_duration(choice_data.get("duration")),
            "title": choice_data.get("title"),
            "tags": SongMurekaTransformer.parse_tags_array(choice_data.get("tags")),
        }

    @staticmethod
    def parse_tags_array(tags: Any) -> str | None:
        """
        Convert tags list to comma-separated string

        Pure function - no dependencies

        Args:
            tags: Tags from MUREKA (should be list, but handle other types)

        Returns:
            Comma-separated string or None

        Examples:
            ["pop", "upbeat"] -> "pop,upbeat"
            [] -> None
            None -> None
            "rock" -> None (invalid type)
        """
        if tags and isinstance(tags, list) and len(tags) > 0:
            return ",".join(str(tag) for tag in tags)
        return None

    @staticmethod
    def parse_duration(duration: Any) -> float | None:
        """
        Parse duration value with type conversion and error handling

        Pure function - no dependencies

        Args:
            duration: Duration from MUREKA (float, int, or string)

        Returns:
            Float value or None if invalid

        Examples:
            30567.89 -> 30567.89
            30567 -> 30567.0
            "30567.89" -> 30567.89
            None -> None
            "invalid" -> None
        """
        if duration is None:
            return None

        try:
            return float(duration)
        except (ValueError, TypeError):
            return None
