"""
Song Generation Routes mit MUREKA + Pydantic validation
"""

from uuid import UUID

from flask import Blueprint, jsonify, request
from flask_pydantic import validate
from sqlalchemy.orm import Session

from api.auth_middleware import get_current_user_id, jwt_required
from api.controllers.song_controller import SongController
from business.song_orchestrator import SongS3MigrationError
from db.database import get_db
from schemas.common_schemas import ErrorResponse
from schemas.project_asset_schemas import AssignToProjectRequest
from schemas.song_schemas import (
    SongGenerateRequest,
    SongUpdateRequest,
    StemGenerateRequest,
)
from utils.logger import logger


api_song_v1 = Blueprint("api_song_v1", __name__, url_prefix="/api/v1/song")

# Controller instance
song_controller = SongController()


@api_song_v1.route("/celery-health", methods=["GET"])
def celery_health():
    """Überprüft Celery Worker Status"""
    response_data, status_code = song_controller.get_celery_health()
    return jsonify(response_data), status_code


@api_song_v1.route("/mureka-account", methods=["GET"])
@jwt_required
def mureka_account():
    """Abfrage der MUREKA Account-Informationen"""
    response_data, status_code = song_controller.get_mureka_account()
    return jsonify(response_data), status_code


@api_song_v1.route("/generate", methods=["POST"])
@jwt_required
@validate()
def song_generate(body: SongGenerateRequest):
    """Startet Song-Generierung"""
    try:
        # Convert Pydantic model to dict for controller
        payload = body.dict()

        response_data, status_code = song_controller.generate_song(payload=payload, host_url=request.host_url)
        return jsonify(response_data), status_code
    except Exception as e:
        error_response = ErrorResponse(error=str(e))
        return jsonify(error_response.dict()), 500


@api_song_v1.route("/stem/generate", methods=["POST"])
@jwt_required
@validate()
def stems_generator(body: StemGenerateRequest):
    """Erstelle stems anhand einer MP3"""
    try:
        # Convert Pydantic model to dict for controller
        payload = body.dict()

        response_data, status_code = song_controller.generate_stems(payload)
        return jsonify(response_data), status_code
    except Exception as e:
        error_response = ErrorResponse(error=str(e))
        return jsonify(error_response.dict()), 500


@api_song_v1.route("/query/<job_id>", methods=["GET"])
@jwt_required
def song_info(job_id):
    """Get Song structure direct from MUREKA again who was generated successfully"""
    response_data, status_code = song_controller.get_song_info(job_id)

    return jsonify(response_data), status_code


@api_song_v1.route("/force-complete/<job_id>", methods=["POST"])
@jwt_required
def force_complete_task(job_id):
    """Erzwingt Completion eines Tasks"""
    response_data, status_code = song_controller.force_complete_task(job_id)

    return jsonify(response_data), status_code


@api_song_v1.route("/list", methods=["GET"])
@jwt_required
def list_songs():
    """Get list of songs with pagination, search and sorting"""
    # Parse query parameters
    try:
        limit = int(request.args.get("limit", 20))
        offset = int(request.args.get("offset", 0))

        # Validate parameters
        if limit <= 0 or limit > 100:
            return jsonify({"error": "Limit must be between 1 and 100"}), 400
        if offset < 0:
            return jsonify({"error": "Offset must be >= 0"}), 400

    except ValueError:
        return jsonify({"error": "Invalid limit or offset parameter"}), 400

    # Parse search and sort parameters
    status = request.args.get("status", None)  # Optional status filter
    search = request.args.get("search", "").strip()
    sort_by = request.args.get("sort_by", "created_at")
    sort_direction = request.args.get("sort_direction", "desc")
    workflow = request.args.get("workflow", None)  # Optional workflow filter

    # Validate sort parameters
    valid_sort_fields = ["created_at", "title", "lyrics"]
    if sort_by not in valid_sort_fields:
        return jsonify({"error": f"Invalid sort_by field. Must be one of: {valid_sort_fields}"}), 400

    if sort_direction not in ["asc", "desc"]:
        return jsonify({"error": "Invalid sort_direction. Must be 'asc' or 'desc'"}), 400

    response_data, status_code = song_controller.get_songs(
        limit=limit,
        offset=offset,
        status=status,
        search=search,
        sort_by=sort_by,
        sort_direction=sort_direction,
        workflow=workflow,
    )

    return jsonify(response_data), status_code


@api_song_v1.route("/<song_id>", methods=["GET"])
@jwt_required
def get_song(song_id):
    """Get single song by ID with all choices"""
    response_data, status_code = song_controller.get_song_by_id(song_id)

    return jsonify(response_data), status_code


@api_song_v1.route("/<song_id>", methods=["DELETE"])
@jwt_required
def delete_song(song_id):
    """Delete song by ID including all choices"""
    response_data, status_code = song_controller.delete_song(song_id)

    return jsonify(response_data), status_code


@api_song_v1.route("/bulk-delete", methods=["DELETE"])
@jwt_required
def bulk_delete_songs():
    """Delete multiple songs by IDs"""
    payload = request.get_json(force=True)

    if not payload:
        return jsonify({"error": "No JSON provided"}), 400

    song_ids = payload.get("ids", [])

    if not isinstance(song_ids, list):
        return jsonify({"error": "ids must be an array"}), 400

    response_data, status_code = song_controller.bulk_delete_songs(song_ids)

    return jsonify(response_data), status_code


@api_song_v1.route("/choice/<choice_id>/rating", methods=["PUT"])
@jwt_required
def update_choice_rating(choice_id):
    """Update rating for a specific song choice"""
    payload = request.get_json(force=True)

    if not payload:
        return jsonify({"error": "No data provided"}), 400

    response_data, status_code = song_controller.update_choice_rating(choice_id, payload)

    return jsonify(response_data), status_code


api_song_task_v1 = Blueprint("api_song_task_v1", __name__, url_prefix="/api/v1/song/task")


@api_song_task_v1.route("/status/<task_id>", methods=["GET"])
@jwt_required
def song_status(task_id):
    """Überprüft Status einer Song-Generierung"""
    response_data, status_code = song_controller.get_song_status(task_id)

    return jsonify(response_data), status_code


@api_song_task_v1.route("/cancel/<task_id>", methods=["POST"])
@jwt_required
def cancel_task(task_id):
    """Cancelt einen Task"""
    response_data, status_code = song_controller.cancel_task(task_id)

    return jsonify(response_data), status_code


@api_song_task_v1.route("/delete/<task_id>", methods=["DELETE"])
@jwt_required
def delete_task_result(task_id):
    """Löscht Task-Ergebnis"""
    response_data, status_code = song_controller.delete_task_result(task_id)

    return jsonify(response_data), status_code


@api_song_task_v1.route("/queue-status", methods=["GET"])
@jwt_required
def queue_status():
    """Gibt Queue-Status zurück"""
    response_data, status_code = song_controller.get_queue_status()

    return jsonify(response_data), status_code


@api_song_v1.route("/<song_id>", methods=["PUT"])
@jwt_required
@validate()
def update_song(song_id: str, body: SongUpdateRequest):
    """Update song metadata"""
    try:
        response_data, status_code = song_controller.update_song(song_id, body.dict(exclude_none=True))
        return jsonify(response_data), status_code
    except Exception as e:
        error_response = ErrorResponse(error=str(e))
        return jsonify(error_response.dict()), 500


@api_song_v1.route("/<string:song_id>/assign-to-project", methods=["POST"])
@jwt_required
@validate()
def assign_song_to_project(song_id: str, body: AssignToProjectRequest):
    """Assign song to project"""
    try:
        response_data, status_code = song_controller.assign_to_project(
            song_id, str(body.project_id), str(body.folder_id) if body.folder_id else None
        )
        return jsonify(response_data), status_code
    except Exception as e:
        error_response = ErrorResponse(error=str(e))
        return jsonify(error_response.dict()), 500


@api_song_v1.route("/<string:song_id>/unassign-from-project", methods=["DELETE"])
@jwt_required
def unassign_song_from_project(song_id: str):
    """Remove song from its assigned project (link only, song remains)"""
    try:
        response_data, status_code = song_controller.unassign_from_project(song_id)
        return jsonify(response_data), status_code
    except Exception as e:
        error_response = ErrorResponse(error=str(e))
        return jsonify(error_response.dict()), 500


# ============================================================
# S3 Proxy Endpoints (Lazy Migration from Mureka CDN)
# ============================================================


@api_song_v1.route("/choice/<choice_id>/mp3", methods=["GET"])
@jwt_required
def serve_choice_mp3(choice_id: str):
    """
    Serve song choice MP3 via backend proxy (lazy migration from Mureka to S3)

    CRITICAL: This endpoint implements lazy migration pattern:
    1. Check if file exists in S3 (mp3_s3_key)
    2. If not, download from Mureka URL and upload to S3
    3. Stream file from S3 to browser

    Path Parameters:
        - choice_id (UUID): Choice ID

    Response:
        200: Binary audio data (audio/mpeg)
        401: {'error': 'Unauthorized'}
        404: {'error': 'Choice not found' | 'MP3 not available'}
        500: {'error': 'Failed to load MP3'}

    Example:
        GET /api/v1/song/choice/550e8400-e29b-41d4-a716-446655440000/mp3
        Headers: Authorization: Bearer <JWT_TOKEN>
    """
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        from adapters.s3.s3_proxy_service import s3_proxy_service
        from business.song_orchestrator import song_orchestrator
        from config.settings import S3_SONGS_BUCKET

        choice_uuid = UUID(choice_id)

        logger.debug("Serving choice MP3", choice_id=choice_id, user_id=user_id)

        # Get DB session
        db: Session = next(get_db())
        try:
            # Lazy migration: Download from Mureka to S3 if needed
            s3_key = song_orchestrator.migrate_choice_to_s3(db, str(choice_uuid), "mp3")

            # Stream from S3 using generic proxy service
            return s3_proxy_service.serve_resource(bucket=S3_SONGS_BUCKET, s3_key=s3_key, filename="song.mp3")

        finally:
            db.close()

    except ValueError:
        return jsonify({"error": "Invalid choice ID format"}), 400
    except SongS3MigrationError as e:
        logger.warning("MP3 migration failed", choice_id=choice_id, error=str(e))
        return jsonify({"error": "MP3 not available"}), 404
    except Exception as e:
        logger.error("Error serving choice MP3", choice_id=choice_id, error=str(e), error_type=type(e).__name__)
        return jsonify({"error": "Failed to load MP3"}), 500


@api_song_v1.route("/choice/<choice_id>/flac", methods=["GET"])
@jwt_required
def serve_choice_flac(choice_id: str):
    """
    Serve song choice FLAC via backend proxy (lazy migration from Mureka to S3)

    CRITICAL: This endpoint implements lazy migration pattern:
    1. Check if file exists in S3 (flac_s3_key)
    2. If not, download from Mureka URL and upload to S3
    3. Stream file from S3 to browser

    Path Parameters:
        - choice_id (UUID): Choice ID

    Response:
        200: Binary audio data (audio/flac)
        401: {'error': 'Unauthorized'}
        404: {'error': 'Choice not found' | 'FLAC not available'}
        500: {'error': 'Failed to load FLAC'}

    Example:
        GET /api/v1/song/choice/550e8400-e29b-41d4-a716-446655440000/flac
        Headers: Authorization: Bearer <JWT_TOKEN>
    """
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        from adapters.s3.s3_proxy_service import s3_proxy_service
        from business.song_orchestrator import song_orchestrator
        from config.settings import S3_SONGS_BUCKET

        choice_uuid = UUID(choice_id)

        logger.debug("Serving choice FLAC", choice_id=choice_id, user_id=user_id)

        # Get DB session
        db: Session = next(get_db())
        try:
            # Lazy migration: Download from Mureka to S3 if needed
            s3_key = song_orchestrator.migrate_choice_to_s3(db, str(choice_uuid), "flac")

            # Stream from S3 using generic proxy service
            return s3_proxy_service.serve_resource(bucket=S3_SONGS_BUCKET, s3_key=s3_key, filename="song.flac")

        finally:
            db.close()

    except ValueError:
        return jsonify({"error": "Invalid choice ID format"}), 400
    except SongS3MigrationError as e:
        logger.warning("FLAC migration failed", choice_id=choice_id, error=str(e))
        return jsonify({"error": "FLAC not available"}), 404
    except Exception as e:
        logger.error("Error serving choice FLAC", choice_id=choice_id, error=str(e), error_type=type(e).__name__)
        return jsonify({"error": "Failed to load FLAC"}), 500


@api_song_v1.route("/choice/<choice_id>/stems", methods=["GET"])
@jwt_required
def serve_choice_stems(choice_id: str):
    """
    Serve song choice stems ZIP via backend proxy (lazy migration from Mureka to S3)

    CRITICAL: This endpoint implements lazy migration pattern:
    1. Check if file exists in S3 (stem_s3_key)
    2. If not, download from Mureka URL and upload to S3
    3. Stream file from S3 to browser

    Path Parameters:
        - choice_id (UUID): Choice ID

    Response:
        200: Binary ZIP data (application/zip)
        401: {'error': 'Unauthorized'}
        404: {'error': 'Choice not found' | 'Stems not available'}
        500: {'error': 'Failed to load stems'}

    Example:
        GET /api/v1/song/choice/550e8400-e29b-41d4-a716-446655440000/stems
        Headers: Authorization: Bearer <JWT_TOKEN>
    """
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        from adapters.s3.s3_proxy_service import s3_proxy_service
        from business.song_orchestrator import song_orchestrator
        from config.settings import S3_SONGS_BUCKET

        choice_uuid = UUID(choice_id)

        logger.debug("Serving choice stems", choice_id=choice_id, user_id=user_id)

        # Get DB session
        db: Session = next(get_db())
        try:
            # Lazy migration: Download from Mureka to S3 if needed
            s3_key = song_orchestrator.migrate_choice_to_s3(db, str(choice_uuid), "stems")

            # Stream from S3 using generic proxy service
            return s3_proxy_service.serve_resource(bucket=S3_SONGS_BUCKET, s3_key=s3_key, filename="stems.zip")

        finally:
            db.close()

    except ValueError:
        return jsonify({"error": "Invalid choice ID format"}), 400
    except SongS3MigrationError as e:
        logger.warning("Stems migration failed", choice_id=choice_id, error=str(e))
        return jsonify({"error": "Stems not available"}), 404
    except Exception as e:
        logger.error("Error serving choice stems", choice_id=choice_id, error=str(e), error_type=type(e).__name__)
        return jsonify({"error": "Failed to load stems"}), 500
