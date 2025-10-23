"""
DALL-E Image Generation Routes with Pydantic validation
"""

import traceback

from flask import Blueprint, jsonify, request, send_from_directory
from flask_pydantic import validate

from api.auth_middleware import get_current_user_id, jwt_required
from api.controllers.image_controller import ImageController
from config.settings import IMAGES_DIR
from schemas.common_schemas import ErrorResponse
from schemas.image_schemas import (
    ImageGenerateRequest,
    ImageListRequest,
    ImageUpdateRequest,
)
from utils.logger import logger


api_image_v1 = Blueprint("api_image_v1", __name__, url_prefix="/api/v1/image")

# Controller instance
image_controller = ImageController()


@api_image_v1.route("/generate", methods=["POST"])
@jwt_required
@validate()
def generate(body: ImageGenerateRequest):
    """Generate image with DALL-E"""
    try:
        response_data, status_code = image_controller.generate_image(
            prompt=body.prompt,
            size=body.size,
            title=body.title,
            user_prompt=body.user_prompt,
            artistic_style=body.artistic_style,
            composition=body.composition,
            lighting=body.lighting,
            color_palette=body.color_palette,
            detail_level=body.detail_level,
        )
        return jsonify(response_data), status_code
    except Exception as e:
        error_response = ErrorResponse(error=str(e))
        return jsonify(error_response.dict()), 500


@api_image_v1.route("/list", methods=["GET"])
@jwt_required
@validate()
def list_images(query: ImageListRequest):
    """Get list of generated images with pagination, search and sorting"""
    try:
        response_data, status_code = image_controller.get_images(
            limit=query.limit, offset=query.offset, search=query.search, sort_by=query.sort, sort_direction=query.order
        )
        return jsonify(response_data), status_code
    except Exception as e:
        error_response = ErrorResponse(error=str(e))
        return jsonify(error_response.dict()), 500


@api_image_v1.route("/<path:filename>")
@jwt_required
def serve_image(filename):
    """Serve stored images"""
    try:
        logger.debug("Serving image", filename=filename)
        return send_from_directory(IMAGES_DIR, filename)
    except Exception as e:
        logger.error(
            "Error serving image",
            filename=filename,
            error=str(e),
            error_type=type(e).__name__,
            stacktrace=traceback.format_exc(),
        )
        return jsonify({"error": "Image not found"}), 404


@api_image_v1.route("/id/<string:image_id>", methods=["GET"])
@jwt_required
def get_image(image_id):
    """Get single image by ID"""
    response_data, status_code = image_controller.get_image_by_id(image_id)

    return jsonify(response_data), status_code


@api_image_v1.route("/id/<string:image_id>", methods=["DELETE"])
@jwt_required
def delete_image(image_id):
    """Delete image by ID"""
    response_data, status_code = image_controller.delete_image(image_id)

    return jsonify(response_data), status_code


@api_image_v1.route("/bulk-delete", methods=["DELETE"])
@jwt_required
def bulk_delete_images():
    """Delete multiple images by IDs"""
    raw_json = request.get_json(silent=True)

    if not raw_json:
        return jsonify({"error": "No JSON provided"}), 400

    image_ids = raw_json.get("ids", [])

    if not isinstance(image_ids, list):
        return jsonify({"error": "ids must be an array"}), 400

    response_data, status_code = image_controller.bulk_delete_images(image_ids)

    return jsonify(response_data), status_code


@api_image_v1.route("/id/<string:image_id>", methods=["PUT"])
@jwt_required
@validate()
def update_image_metadata(image_id: str, body: ImageUpdateRequest):
    """Update image metadata (title and/or tags)"""
    try:
        response_data, status_code = image_controller.update_image_metadata(image_id, body.title, body.tags)
        return jsonify(response_data), status_code
    except Exception as e:
        error_response = ErrorResponse(error=str(e))
        return jsonify(error_response.dict()), 500


@api_image_v1.route("/add-text-overlay", methods=["POST"])
@jwt_required
def add_text_overlay():
    """Add text overlay to existing image"""
    user_id = get_current_user_id()

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    raw_json = request.get_json(silent=True)

    if not raw_json:
        return jsonify({"error": "No JSON provided"}), 400

    # Extract parameters
    image_id = raw_json.get("image_id")
    title = raw_json.get("title")
    artist = raw_json.get("artist")
    font_style = raw_json.get("font_style", "bold")
    position = raw_json.get("position", "top")
    text_color = raw_json.get("text_color", "#FFD700")
    outline_color = raw_json.get("outline_color", "#000000")

    # Validate required fields
    if not image_id or not title:
        return jsonify({"error": "image_id and title are required"}), 400

    # Call controller
    response_data, status_code = image_controller.add_text_overlay(
        image_id=image_id,
        user_id=str(user_id),
        title=title,
        artist=artist,
        font_style=font_style,
        position=position,
        text_color=text_color,
        outline_color=outline_color,
    )

    return jsonify(response_data), status_code
