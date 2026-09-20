from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from services.lesson_service.service import (
    generate_lesson,
    generate_quiz,
    generate_coding_challenge,
    get_lesson_by_id,
    get_videos_by_lesson_id,
)


lesson_routes = Blueprint("lesson_routes", __name__)


@lesson_routes.route("/api/lesson/generate", methods=["POST"])
@jwt_required()
def create_lesson():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"message": "Request body is required."}), 400

    course_id = data.get("course_id")
    title = data.get("title")
    sequence_number = data.get("sequence_number")

    if not course_id:
        return jsonify({"message": "Course ID is required."}), 400

    if not title:
        return jsonify({"message": "Lesson title is required."}), 400

    if sequence_number is None:
        return jsonify({"message": "Sequence number is required."}), 400

    user_id = get_jwt_identity()

    result = generate_lesson(
        user_id=user_id,
        course_id=course_id,
        title=title,
        sequence_number=sequence_number,
    )

    status_code = result.pop("status_code", 200)

    return jsonify(result), status_code


@lesson_routes.route("/api/lesson/<lesson_id>", methods=["GET"])
@jwt_required()
def get_lesson(lesson_id):
    result = get_lesson_by_id(lesson_id)

    if result is None:
        return jsonify({"message": "Lesson not found."}), 404

    return jsonify(result), 200


@lesson_routes.route("/api/video/<lesson_id>", methods=["GET"])
@jwt_required()
def get_videos(lesson_id):
    videos = get_videos_by_lesson_id(lesson_id)

    return jsonify({"videos": videos}), 200


@lesson_routes.route("/api/quiz/generate", methods=["POST"])
@jwt_required()
def create_quiz():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"message": "Request body is required."}), 400

    lesson_id = data.get("lesson_id")
    number_of_questions = data.get("number_of_questions")

    if not lesson_id:
        return jsonify({"message": "Lesson ID is required."}), 400

    if number_of_questions is None:
        return jsonify({
            "message": "Number of questions is required."
        }), 400

    if not isinstance(number_of_questions, int):
        return jsonify({
            "message": "Number of questions must be an integer."
        }), 400

    if number_of_questions <= 0:
        return jsonify({
            "message": "Number of questions must be greater than zero."
        }), 400

    user_id = get_jwt_identity()

    result = generate_quiz(
        user_id=user_id,
        lesson_id=lesson_id,
        number_of_questions=number_of_questions,
    )

    status_code = result.pop("status_code", 200)

    return jsonify(result), status_code

@lesson_routes.route("/api/challenge/generate", methods=["POST"])
@jwt_required()
def create_coding_challenge():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"message": "Request body is required."}), 400

    lesson_id = data.get("lesson_id")

    if not lesson_id:
        return jsonify({"message": "Lesson ID is required."}), 400

    user_id = get_jwt_identity()

    result = generate_coding_challenge(
        user_id=user_id,
        lesson_id=lesson_id
    )

    status_code = result.pop("status_code", 200)

    return jsonify(result), status_code