"""Song Creation Controller - Handles song and stem generation logic"""

import time
from datetime import datetime
from typing import Any

import requests

from celery_app import generate_instrumental_task, generate_song_task
from config.settings import MUREKA_API_KEY, MUREKA_STATUS_ENDPOINT, MUREKA_STEM_GENERATE_ENDPOINT
from db.database import get_db
from db.models import SongChoice
from db.sketch_service import sketch_service
from db.song_service import song_service
from mureka.json_utils import prune_keys
from utils.logger import logger


class SongCreationController:
    """Controller for song and stem creation operations"""

    def generate_song(self, payload: dict[str, Any], host_url: str, check_balance_func) -> tuple[dict[str, Any], int]:
        """Start Song Generation"""
        if not payload.get("lyrics") or not payload.get("prompt") or not payload.get("model"):
            return {"error": "Missing required fields: 'lyrics', 'prompt' and model are required"}, 400

        if not check_balance_func():
            return {"error": "Insufficient MUREKA balance"}, 402  # Payment Required

        # Handle sketch_id if provided
        sketch_id = payload.get("sketch_id")
        if sketch_id:
            logger.info("Song generation requested with sketch_id", sketch_id=sketch_id)

            # Load and validate sketch
            db = next(get_db())
            try:
                sketch = sketch_service.get_sketch_by_id(db, sketch_id)
                if not sketch:
                    return {"error": f"Sketch not found with ID: {sketch_id}"}, 404

                # Validate sketch workflow state (must be draft or used)
                if sketch.workflow not in ["draft", "used"]:
                    return {"error": f"Sketch is archived and cannot be used (workflow: {sketch.workflow})"}, 400
            finally:
                db.close()

            logger.info("Using sketch for song generation", sketch_id=sketch_id, sketch_workflow=sketch.workflow)

        logger.info(
            "Starting song generation",
            lyrics_length=len(payload.get("lyrics", "")),
            prompt=payload.get("prompt", ""),
            model=payload.get("model", ""),
            sketch_id=sketch_id,
        )

        task = generate_song_task.delay(payload)

        # Create song record in database with sketch reference
        song = song_service.create_song(
            task_id=task.id,
            lyrics=payload.get("lyrics", ""),
            prompt=payload.get("prompt", ""),
            model=payload.get("model", "auto"),
            title=payload.get("title"),
            sketch_id=sketch_id,
        )

        if not song:
            logger.warning("Failed to create song record in database", task_id=task.id)
            # Continue anyway - fallback to Redis-only mode
            return {"task_id": task.id, "status_url": f"{host_url}api/v1/song/status/{task.id}"}, 202
        else:
            logger.info("Created song record in database", song_id=song.id, task_id=task.id, sketch_id=sketch_id)

        # Mark sketch as "used" if this is the first time it's being used
        if sketch_id:
            db = next(get_db())
            try:
                sketch = sketch_service.get_sketch_by_id(db, sketch_id)
                if sketch and sketch.workflow == "draft":
                    updated_sketch = sketch_service.mark_sketch_as_used(db, sketch_id)
                    if updated_sketch:
                        logger.info("Marked sketch as used", sketch_id=sketch_id)
                    else:
                        logger.warning("Failed to mark sketch as used", sketch_id=sketch_id)
            finally:
                db.close()

        return {
            "task_id": task.id,
            "song_id": str(song.id),
            "status_url": f"{host_url}api/v1/song/status/{task.id}",
        }, 202

    def generate_instrumental(
        self, payload: dict[str, Any], host_url: str, check_balance_func
    ) -> tuple[dict[str, Any], int]:
        """Start Instrumental Generation"""
        if not payload.get("prompt") or not payload.get("model"):
            return {"error": "Missing required field: 'prompt' and 'model' is required"}, 400

        if not check_balance_func():
            return {"error": "Insufficient MUREKA balance"}, 402  # Payment Required

        # Handle sketch_id if provided
        sketch_id = payload.get("sketch_id")
        if sketch_id:
            logger.info("Instrumental generation requested with sketch_id", sketch_id=sketch_id)

            # Load and validate sketch
            db = next(get_db())
            try:
                sketch = sketch_service.get_sketch_by_id(db, sketch_id)
                if not sketch:
                    return {"error": f"Sketch not found with ID: {sketch_id}"}, 404

                # Validate sketch workflow state (must be draft or used)
                if sketch.workflow not in ["draft", "used"]:
                    return {"error": f"Sketch is archived and cannot be used (workflow: {sketch.workflow})"}, 400
            finally:
                db.close()

            logger.info(
                "Using sketch for instrumental generation", sketch_id=sketch_id, sketch_workflow=sketch.workflow
            )

        logger.info(
            "Starting instrumental generation",
            prompt=payload.get("prompt", ""),
            model=payload.get("model", ""),
            sketch_id=sketch_id,
        )

        task = generate_instrumental_task.delay(payload)

        # Create song record in database with instrumental flag and sketch reference
        song = song_service.create_song(
            task_id=task.id,
            lyrics="",  # Empty for instrumental
            prompt=payload.get("prompt", ""),
            model=payload.get("model", "auto"),
            is_instrumental=True,
            title=payload.get("title"),
            sketch_id=sketch_id,
        )

        if not song:
            logger.warning("Failed to create instrumental song record in database", task_id=task.id)
            # Continue anyway - fallback to Redis-only mode
            return {"task_id": task.id, "status_url": f"{host_url}api/v1/instrumental/task/status/{task.id}"}, 202
        else:
            logger.info(
                "Created instrumental song record in database", song_id=song.id, task_id=task.id, sketch_id=sketch_id
            )

        # Mark sketch as "used" if this is the first time it's being used
        if sketch_id:
            db = next(get_db())
            try:
                sketch = sketch_service.get_sketch_by_id(db, sketch_id)
                if sketch and sketch.workflow == "draft":
                    updated_sketch = sketch_service.mark_sketch_as_used(db, sketch_id)
                    if updated_sketch:
                        logger.info("Marked sketch as used", sketch_id=sketch_id)
                    else:
                        logger.warning("Failed to mark sketch as used", sketch_id=sketch_id)
            finally:
                db.close()

        return {
            "task_id": task.id,
            "song_id": str(song.id),
            "status_url": f"{host_url}api/v1/instrumental/task/status/{task.id}",
        }, 202

    def generate_stems(self, payload: dict[str, Any], check_balance_func) -> tuple[dict[str, Any], int]:
        """Generate stems from MP3"""
        choice_id = payload.get("choice_id")
        if not choice_id:
            return {"error": "Missing required field: 'choice_id' is required"}, 400

        if not check_balance_func():
            return {"error": "Insufficient MUREKA balance"}, 402  # Payment Required

        # Query song_choices table to get mp3_url
        db = next(get_db())
        try:
            choice = db.query(SongChoice).filter(SongChoice.id == choice_id).first()
            if not choice:
                return {"error": f"Choice with ID {choice_id} not found"}, 404

            if not choice.mp3_url:
                return {"error": f"Choice {choice_id} has no MP3 URL"}, 400

            mp3_url = choice.mp3_url
            logger.info(
                "Starting stem generation", choice_id=choice_id, endpoint=MUREKA_STEM_GENERATE_ENDPOINT, mp3_url=mp3_url
            )

            # Prepare payload for MUREKA API
            mureka_payload = {"url": mp3_url}

            headers = {"Authorization": f"Bearer {MUREKA_API_KEY}"}

            # Creating stems can take a while. 5 minutes (300) timeout therefore
            response = requests.post(
                MUREKA_STEM_GENERATE_ENDPOINT, headers=headers, timeout=(10, 300), json=mureka_payload
            )
            response.raise_for_status()
            result = response.json()

            # Save stem URL to database if generation was successful
            if result and result.get("zip_url"):
                choice.stem_url = result["zip_url"]
                choice.stem_generated_at = datetime.utcnow()
                db.commit()
                logger.info("Saved stem URL to database", choice_id=choice_id, stem_url=result["zip_url"])

            return {"status": "SUCCESS", "result": result, "completed_at": time.time()}, 200

        except Exception as e:
            logger.error("Error on create stem", error=str(e))
            return {"error": str(e)}, 500
        finally:
            db.close()

    def get_song_info(self, job_id: str) -> tuple[dict[str, Any], int]:
        """Get Song structure direct from MUREKA again who was generated successfully"""
        try:
            headers = {"Authorization": f"Bearer {MUREKA_API_KEY}"}

            song_info_url = f"{MUREKA_STATUS_ENDPOINT}/{job_id}"
            logger.debug("Fetching song info from MUREKA", endpoint=MUREKA_STATUS_ENDPOINT, job_id=job_id)

            response = requests.get(song_info_url, headers=headers, timeout=10)
            response.raise_for_status()
            mureka_result = response.json()
            keys_to_remove = {"lyrics_sections"}
            cleaned_json = prune_keys(mureka_result, keys_to_remove)

            return {
                "status": "SUCCESS",
                "task_id": job_id,
                "job_id": job_id,
                "result": cleaned_json,
                "completed_at": time.time(),
            }, 200

        except Exception as e:
            logger.error("Error on get song", error=str(e))
            return {"error": str(e)}, 500
