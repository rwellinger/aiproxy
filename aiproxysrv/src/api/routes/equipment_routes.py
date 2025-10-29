"""
Equipment API Routes - HTTP endpoints for equipment management.

CRITICAL:
- ALL endpoints require JWT authentication (@jwt_required)
- User ID from JWT token (get_current_user_id), NOT from URL params
- Input validation with Pydantic schemas
- Parameter validation (limit, offset)

Endpoints:
- POST   /api/v1/equipment              Create equipment
- GET    /api/v1/equipment              List equipment (paginated, filterable)
- GET    /api/v1/equipment/{id}         Get equipment by ID
- PUT    /api/v1/equipment/{id}         Update equipment
- DELETE /api/v1/equipment/{id}         Delete equipment
"""

from db.session import get_db
from flask import Blueprint, jsonify, request
from sqlalchemy.orm import Session

from api.controllers.equipment_controller import (
    EquipmentController,
    EquipmentCreateRequest,
    EquipmentUpdateRequest,
)
from api.middleware.auth import get_current_user_id, jwt_required


# Blueprint definition
api_equipment_v1 = Blueprint("api_equipment_v1", __name__, url_prefix="/api/v1/equipment")


@api_equipment_v1.route("", methods=["POST"])
@jwt_required
def create_equipment():
    """
    Create new equipment.

    Request Body:
        EquipmentCreateRequest (JSON)

    Response:
        201: {'data': {'id': '...'}, 'message': 'Equipment created successfully'}
        401: {'error': 'Unauthorized'}
        500: {'error': 'Failed to create equipment: ...'}

    Example:
        POST /api/v1/equipment
        Headers: Authorization: Bearer <JWT_TOKEN>
        Body: {
            "type": "Software",
            "name": "Logic Pro X",
            "manufacturer": "Apple",
            "password": "my-secret",
            "price": "299.99 EUR",
            "status": "active"
        }
    """
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        equipment_data = EquipmentCreateRequest.model_validate(request.json)
    except Exception as e:
        return jsonify({"error": f"Invalid request data: {str(e)}"}), 400

    db: Session = next(get_db())
    try:
        result, status_code = EquipmentController.create_equipment(db, str(user_id), equipment_data)
        return jsonify(result), status_code
    finally:
        db.close()


@api_equipment_v1.route("", methods=["GET"])
@jwt_required
def list_equipment():
    """
    List equipment with pagination and filters.

    Query Parameters:
        - limit (int, optional): Items per page (1-100, default 20)
        - offset (int, optional): Pagination offset (default 0)
        - type (str, optional): Filter by type ('Software' | 'Plugin')
        - status (str, optional): Filter by status ('active' | 'trial' | 'expired' | 'archived')
        - search (str, optional): Search in name, manufacturer, tags

    Response:
        200: {
            'data': [...],
            'pagination': {
                'total': 42,
                'limit': 20,
                'offset': 0,
                'has_more': true
            }
        }
        401: {'error': 'Unauthorized'}
        500: {'error': 'Internal server error'}

    Example:
        GET /api/v1/equipment?limit=20&offset=0&type=Software&search=Logic
    """
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    # Parameter validation
    try:
        limit = min(int(request.args.get("limit", 20)), 100)  # Max 100
        limit = max(limit, 1)  # Min 1
        offset = max(int(request.args.get("offset", 0)), 0)  # Min 0
    except ValueError:
        return jsonify({"error": "Invalid limit or offset parameter"}), 400

    type_filter = request.args.get("type")
    status_filter = request.args.get("status")
    search = request.args.get("search")

    db: Session = next(get_db())
    try:
        result, status_code = EquipmentController.list_equipment(
            db, str(user_id), limit, offset, type_filter, status_filter, search
        )
        return jsonify(result), status_code
    finally:
        db.close()


@api_equipment_v1.route("/<equipment_id>", methods=["GET"])
@jwt_required
def get_equipment(equipment_id: str):
    """
    Get equipment by ID (with decrypted sensitive fields).

    Path Parameters:
        equipment_id (str): Equipment UUID

    Response:
        200: {'data': {...}}  # Full equipment data with decrypted password, license_key, price
        401: {'error': 'Unauthorized'}
        404: {'error': 'Equipment not found'}
        500: {'error': 'Internal server error'}

    Example:
        GET /api/v1/equipment/123e4567-e89b-12d3-a456-426614174000
        Headers: Authorization: Bearer <JWT_TOKEN>
    """
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    db: Session = next(get_db())
    try:
        result, status_code = EquipmentController.get_equipment(db, equipment_id, str(user_id))
        return jsonify(result), status_code
    finally:
        db.close()


@api_equipment_v1.route("/<equipment_id>", methods=["PUT"])
@jwt_required
def update_equipment(equipment_id: str):
    """
    Update equipment.

    Path Parameters:
        equipment_id (str): Equipment UUID

    Request Body:
        EquipmentUpdateRequest (JSON, all fields optional)

    Response:
        200: {'data': {'id': '...'}, 'message': 'Equipment updated successfully'}
        401: {'error': 'Unauthorized'}
        400: {'error': 'Invalid request data: ...'}
        500: {'error': 'Failed to update equipment: ...'}

    Example:
        PUT /api/v1/equipment/123e4567-e89b-12d3-a456-426614174000
        Headers: Authorization: Bearer <JWT_TOKEN>
        Body: {
            "status": "archived",
            "price": "349.99 EUR"
        }
    """
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        update_data = EquipmentUpdateRequest.model_validate(request.json)
    except Exception as e:
        return jsonify({"error": f"Invalid request data: {str(e)}"}), 400

    db: Session = next(get_db())
    try:
        result, status_code = EquipmentController.update_equipment(db, equipment_id, str(user_id), update_data)
        return jsonify(result), status_code
    finally:
        db.close()


@api_equipment_v1.route("/<equipment_id>", methods=["DELETE"])
@jwt_required
def delete_equipment(equipment_id: str):
    """
    Delete equipment.

    Path Parameters:
        equipment_id (str): Equipment UUID

    Response:
        200: {'message': 'Equipment deleted successfully'}
        401: {'error': 'Unauthorized'}
        404: {'error': 'Equipment not found'}
        500: {'error': 'Internal server error'}

    Example:
        DELETE /api/v1/equipment/123e4567-e89b-12d3-a456-426614174000
        Headers: Authorization: Bearer <JWT_TOKEN>
    """
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    db: Session = next(get_db())
    try:
        result, status_code = EquipmentController.delete_equipment(db, equipment_id, str(user_id))
        return jsonify(result), status_code
    finally:
        db.close()
