from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from services.course_service.service import (
    create_course,
    get_all_courses,
    get_course_by_id,
)


course_routes = Blueprint("course_routes", __name__)


@course_routes.route("/api/course/generate", methods=["POST"])
@jwt_required()
def generate_course():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"message": "Request body is required."}), 400

    topic = data.get("topic")
    difficulty = data.get("difficulty")
    duration = data.get("duration")

    if not topic:
        return jsonify({"message": "Topic is required."}), 400

    if not difficulty:
        return jsonify({"message": "Difficulty is required."}), 400

    if not duration:
        return jsonify({"message": "Duration is required."}), 400

    user_id = get_jwt_identity()

    result = create_course(
        user_id=user_id,
        topic=topic,
        difficulty=difficulty,
        duration=duration,
    )

    status_code = result.pop("status_code", 200)

    return jsonify(result), status_code


@course_routes.route("/api/course/<course_id>", methods=["GET"])
@jwt_required()
def get_course(course_id):
    user_id = get_jwt_identity()

    result = get_course_by_id(
        course_id=course_id,
        user_id=user_id,
    )

    if result is None:
        return jsonify({
            "message": "Course not found."
        }), 404

    return jsonify(result), 200


@course_routes.route("/api/course/all", methods=["GET"])
@jwt_required()
def get_courses():
    user_id = get_jwt_identity()

    courses = get_all_courses(user_id=user_id)

    return jsonify({
        "courses": courses
    }), 200