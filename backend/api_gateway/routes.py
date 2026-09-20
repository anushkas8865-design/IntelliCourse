from flask import Blueprint, jsonify


gateway_routes = Blueprint("gateway_routes", __name__)


@gateway_routes.route("/api/gateway/health", methods=["GET"])
def gateway_health():
    return jsonify({
        "message": "API Gateway is running successfully."
    }), 200