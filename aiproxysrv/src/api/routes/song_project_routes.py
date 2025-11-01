"""
Song Project API Routes - HTTP endpoints for song project management.

CRITICAL:
- ALL endpoints require JWT authentication (@jwt_required)
- User ID from JWT token (get_current_user_id), NOT from URL params
- Input validation with Pydantic schemas
- Parameter validation (limit, offset)

Endpoints:
- POST   /api/v1/song-projects/projects              Create project
- GET    /api/v1/song-projects/projects              List projects (paginated)
- GET    /api/v1/song-projects/projects/{id}         Get project by ID (no details)
- GET    /api/v1/song-projects/projects/{id}/details Get project with folders and files
- PUT    /api/v1/song-projects/projects/{id}         Update project
- DELETE /api/v1/song-projects/projects/{id}         Delete project (with S3 cleanup)
"""

from uuid import UUID

from flask import Blueprint, jsonify, request
from pydantic import ValidationError
from sqlalchemy.orm import Session

from api.auth_middleware import get_current_user_id, jwt_required
from api.controllers.song_project_controller import song_project_controller
from db.database import get_db
from schemas.song_project_schemas import ProjectCreateRequest, ProjectUpdateRequest


# Blueprint definition
api_song_projects_v1 = Blueprint("api_song_projects_v1", __name__, url_prefix="/api/v1/song-projects")


@api_song_projects_v1.route("/projects", methods=["POST"])
@jwt_required
def create_project():
    """
    Create new project with default folder structure.

    Request Body:
        ProjectCreateRequest (JSON)

    Response:
        201: {'data': {'id': '...'}, 'message': 'Project created successfully'}
        401: {'error': 'Unauthorized'}
        500: {'error': 'Failed to create project: ...'}

    Example:
        POST /api/v1/song-projects/projects
        Headers: Authorization: Bearer <JWT_TOKEN>
        Body: {
            "project_name": "My Awesome Song",
            "tags": ["rock", "demo"],
            "description": "A new project for my rock song"
        }
    """
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        project_data = ProjectCreateRequest.model_validate(request.json)
    except ValidationError as e:
        return jsonify({"error": f"Validation error: {e}"}), 400

    db: Session = next(get_db())
    try:
        result, status_code = song_project_controller.create_project(db, UUID(user_id), project_data)
        return jsonify(result), status_code
    finally:
        db.close()


@api_song_projects_v1.route("/projects", methods=["GET"])
@jwt_required
def list_projects():
    """
    Get list of projects for user (paginated, searchable).

    Query Parameters:
        - limit (int): Items per page (1-100, default: 20)
        - offset (int): Offset for pagination (default: 0)
        - search (str): Search term (project_name, description)
        - tags (str): Comma-separated tags filter

    Response:
        200: {'data': [...], 'pagination': {...}}
        401: {'error': 'Unauthorized'}

    Example:
        GET /api/v1/song-projects/projects?limit=10&offset=0&search=rock&tags=demo,wip
    """
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

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

    # Parse search and filter parameters
    search = request.args.get("search", "").strip()
    tags = request.args.get("tags", None)

    db: Session = next(get_db())
    try:
        result, status_code = song_project_controller.get_projects(
            db=db,
            user_id=UUID(user_id),
            limit=limit,
            offset=offset,
            search=search,
            tags=tags,
        )
        return jsonify(result), status_code
    finally:
        db.close()


@api_song_projects_v1.route("/projects/<project_id>", methods=["GET"])
@jwt_required
def get_project(project_id: str):
    """
    Get a specific project by ID (without details).

    Path Parameters:
        - project_id (UUID): Project ID

    Response:
        200: {'data': {...}}
        404: {'error': 'Project not found with ID: ...'}
        401: {'error': 'Unauthorized'}

    Example:
        GET /api/v1/song-projects/projects/550e8400-e29b-41d4-a716-446655440000
    """
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    db: Session = next(get_db())
    try:
        result, status_code = song_project_controller.get_project_by_id(db, UUID(user_id), project_id)
        return jsonify(result), status_code
    finally:
        db.close()


@api_song_projects_v1.route("/projects/<project_id>/details", methods=["GET"])
@jwt_required
def get_project_details(project_id: str):
    """
    Get a specific project with all folders and files.

    Path Parameters:
        - project_id (UUID): Project ID

    Response:
        200: {'data': {'folders': [...], ...}}
        404: {'error': 'Project not found with ID: ...'}
        401: {'error': 'Unauthorized'}

    Example:
        GET /api/v1/song-projects/projects/550e8400-e29b-41d4-a716-446655440000/details
    """
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    db: Session = next(get_db())
    try:
        result, status_code = song_project_controller.get_project_with_details(db, UUID(user_id), project_id)
        return jsonify(result), status_code
    finally:
        db.close()


@api_song_projects_v1.route("/projects/<project_id>", methods=["PUT"])
@jwt_required
def update_project(project_id: str):
    """
    Update an existing project.

    Path Parameters:
        - project_id (UUID): Project ID

    Request Body:
        ProjectUpdateRequest (JSON)

    Response:
        200: {'data': {...}, 'message': 'Project updated successfully'}
        404: {'error': 'Project not found'}
        401: {'error': 'Unauthorized'}

    Example:
        PUT /api/v1/song-projects/projects/550e8400-e29b-41d4-a716-446655440000
        Body: {
            "project_name": "Updated Project Name",
            "tags": ["rock", "mastered"]
        }
    """
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        update_data = ProjectUpdateRequest.model_validate(request.json)
    except ValidationError as e:
        return jsonify({"error": f"Validation error: {e}"}), 400

    db: Session = next(get_db())
    try:
        result, status_code = song_project_controller.update_project(db, UUID(user_id), project_id, update_data)
        return jsonify(result), status_code
    finally:
        db.close()


@api_song_projects_v1.route("/projects/<project_id>", methods=["DELETE"])
@jwt_required
def delete_project(project_id: str):
    """
    Delete a project (with S3 cleanup).

    Path Parameters:
        - project_id (UUID): Project ID

    Response:
        200: {'message': 'Project deleted successfully'}
        404: {'error': 'Project not found'}
        401: {'error': 'Unauthorized'}

    Example:
        DELETE /api/v1/song-projects/projects/550e8400-e29b-41d4-a716-446655440000
    """
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    db: Session = next(get_db())
    try:
        result, status_code = song_project_controller.delete_project(db, UUID(user_id), project_id)
        return jsonify(result), status_code
    finally:
        db.close()
