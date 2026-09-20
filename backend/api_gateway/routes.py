from flask import Blueprint, jsonify, request

from api_gateway.service import (
    forward_auth_request,
    forward_course_request,
    forward_lesson_request,
    forward_progress_request
)


gateway_routes = Blueprint("gateway_routes", __name__)


@gateway_routes.route("/api/gateway/health", methods=["GET"])
def gateway_health():
    return jsonify({
        "message": "API Gateway is running successfully."
    }), 200


@gateway_routes.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "message": "Request body is required."
        }), 400

    result, status_code = forward_auth_request(
        method="POST",
        path="/api/auth/register",
        data=data
    )

    return jsonify(result), status_code


@gateway_routes.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "message": "Request body is required."
        }), 400

    result, status_code = forward_auth_request(
        method="POST",
        path="/api/auth/login",
        data=data
    )

    return jsonify(result), status_code


@gateway_routes.route("/api/auth/profile", methods=["GET"])
def get_profile():
    authorization = request.headers.get("Authorization")

    if not authorization:
        return jsonify({
            "message": "Authorization header is required."
        }), 401

    result, status_code = forward_auth_request(
        method="GET",
        path="/api/auth/profile",
        authorization=authorization
    )

    return jsonify(result), status_code


@gateway_routes.route("/api/auth/profile", methods=["PUT"])
def update_profile():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "message": "Request body is required."
        }), 400

    authorization = request.headers.get("Authorization")

    if not authorization:
        return jsonify({
            "message": "Authorization header is required."
        }), 401

    result, status_code = forward_auth_request(
        method="PUT",
        path="/api/auth/profile",
        data=data,
        authorization=authorization
    )

    return jsonify(result), status_code

@gateway_routes.route("/api/course/generate", methods=["POST"])
def generate_course():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "message": "Request body is required."
        }), 400

    authorization = request.headers.get("Authorization")

    if not authorization:
        return jsonify({
            "message": "Authorization header is required."
        }), 401

    result, status_code = forward_course_request(
        method="POST",
        path="/api/course/generate",
        data=data,
        authorization=authorization
    )

    return jsonify(result), status_code


@gateway_routes.route("/api/course/<course_id>", methods=["GET"])
def get_course(course_id):
    result, status_code = forward_course_request(
        method="GET",
        path=f"/api/course/{course_id}"
    )

    return jsonify(result), status_code


@gateway_routes.route("/api/course/all", methods=["GET"])
def get_all_courses():
    result, status_code = forward_course_request(
        method="GET",
        path="/api/course/all"
    )

    return jsonify(result), status_code

@gateway_routes.route("/api/lesson/generate", methods=["POST"])
def generate_lesson():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "message": "Request body is required."
        }), 400

    authorization = request.headers.get("Authorization")

    if not authorization:
        return jsonify({
            "message": "Authorization header is required."
        }), 401

    result, status_code = forward_lesson_request(
        method="POST",
        path="/api/lesson/generate",
        data=data,
        authorization=authorization
    )

    return jsonify(result), status_code


@gateway_routes.route("/api/lesson/<lesson_id>", methods=["GET"])
def get_lesson(lesson_id):
    authorization = request.headers.get("Authorization")

    if not authorization:
        return jsonify({"message": "Authorization header is required."}), 401

    result, status_code = forward_lesson_request(
        method="GET",
        path=f"/api/lesson/{lesson_id}",
        authorization=authorization
    )

    return jsonify(result), status_code


@gateway_routes.route("/api/video/<lesson_id>", methods=["GET"])
def get_lesson_videos(lesson_id):
    authorization = request.headers.get("Authorization")

    if not authorization:
        return jsonify({"message": "Authorization header is required."}), 401

    result, status_code = forward_lesson_request(
        method="GET",
        path=f"/api/video/{lesson_id}",
        authorization=authorization
    )

    return jsonify(result), status_code

@gateway_routes.route("/api/progress/update", methods=["POST"])
def update_progress():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"message": "Request body is required."}), 400

    authorization = request.headers.get("Authorization")

    if not authorization:
        return jsonify({"message": "Authorization header is required."}), 401

    result, status_code = forward_progress_request(
        method="POST",
        path="/api/progress/update",
        data=data,
        authorization=authorization
    )

    return jsonify(result), status_code