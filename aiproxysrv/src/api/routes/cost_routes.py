"""
Cost API Routes - OpenAI Admin Cost Tracking
"""

from flask import Blueprint, jsonify

from api.auth_middleware import get_current_user_id, jwt_required
from api.controllers.openai_cost_controller import OpenAICostController
from api.controllers.song_account_controller import SongAccountController


api_cost_v1 = Blueprint("api_cost_v1", __name__, url_prefix="/api/v1/costs")

# Controller instances
cost_controller = OpenAICostController()
mureka_controller = SongAccountController()


@api_cost_v1.route("/openai/current", methods=["GET"])
@jwt_required
def get_openai_current_month():
    """Get OpenAI costs for current month (cached with TTL)"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    response_data, status_code = cost_controller.get_current_month_costs()
    return jsonify(response_data), status_code


@api_cost_v1.route("/openai/<int:year>/<int:month>", methods=["GET"])
@jwt_required
def get_openai_month(year: int, month: int):
    """Get OpenAI costs for specific month (cached forever for past months)"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    # Validate month
    if month < 1 or month > 12:
        return jsonify({"error": "Invalid month (must be 1-12)"}), 400

    response_data, status_code = cost_controller.get_month_costs(year, month)
    return jsonify(response_data), status_code


@api_cost_v1.route("/summary", methods=["GET"])
@jwt_required
def get_costs_summary():
    """Get combined OpenAI + Mureka costs (current month)"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    # Get OpenAI costs
    openai_data, openai_status = cost_controller.get_current_month_costs()

    # Get Mureka balance
    mureka_data, mureka_status = mureka_controller.get_mureka_account()

    return (
        jsonify(
            {
                "status": "success",
                "openai": openai_data.get("costs") if openai_status == 200 else None,
                "mureka": mureka_data.get("account_info") if mureka_status == 200 else None,
            }
        ),
        200,
    )
