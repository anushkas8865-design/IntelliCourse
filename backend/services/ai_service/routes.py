from flask import Blueprint, jsonify, request

from services.ai_service.service import (
    generate_course_with_ai,
    generate_lesson_with_ai,
    generate_quiz_with_ai,
    generate_coding_challenge_with_ai,
)


ai_routes = Blueprint("ai_routes", __name__)


@ai_routes.route("/api/ai/course", methods=["POST"])
def generate_course():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "message": "Request body is required."
        }), 400

    topic = data.get("topic")
    difficulty = data.get("difficulty")
    duration = data.get("duration")

    if not topic:
        return jsonify({
            "message": "Topic is required."
        }), 400

    if not difficulty:
        return jsonify({
            "message": "Difficulty is required."
        }), 400

    if not duration:
        return jsonify({
            "message": "Duration is required."
        }), 400

    result = generate_course_with_ai(
        topic=topic,
        difficulty=difficulty,
        duration=duration,
    )

    status_code = result.pop("status_code", 200)

    return jsonify(result), status_code


@ai_routes.route("/api/ai/lesson", methods=["POST"])
def generate_lesson():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "message": "Request body is required."
        }), 400

    course_id = data.get("course_id")
    title = data.get("title")
    sequence_number = data.get("sequence_number")

    if not course_id:
        return jsonify({
            "message": "Course ID is required."
        }), 400

    if not title:
        return jsonify({
            "message": "Lesson title is required."
        }), 400

    if sequence_number is None:
        return jsonify({
            "message": "Sequence number is required."
        }), 400

    result = generate_lesson_with_ai(
        course_id=course_id,
        title=title,
        sequence_number=sequence_number,
    )

    status_code = result.pop("status_code", 200)

    return jsonify(result), status_code


@ai_routes.route("/api/ai/quiz", methods=["POST"])
def generate_quiz():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "message": "Request body is required."
        }), 400

    lesson_id = data.get("lesson_id")
    lesson_title = data.get("lesson_title")
    number_of_questions = data.get("number_of_questions")

    if not lesson_id:
        return jsonify({
            "message": "Lesson ID is required."
        }), 400

    if not lesson_title:
        return jsonify({
            "message": "Lesson title is required."
        }), 400

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

    result = generate_quiz_with_ai(
        lesson_id=lesson_id,
        lesson_title=lesson_title,
        number_of_questions=number_of_questions,
    )

    status_code = result.pop("status_code", 200)

    return jsonify(result), status_code

@ai_routes.route("/api/ai/challenge", methods=["POST"])
def generate_challenge():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "message": "Request body is required."
        }), 400

    course_title = data.get("course_title")
    lesson_title = data.get("lesson_title")
    difficulty = data.get("difficulty")

    if not course_title:
        return jsonify({
            "message": "Course title is required."
        }), 400

    if not lesson_title:
        return jsonify({
            "message": "Lesson title is required."
        }), 400

    if not difficulty:
        return jsonify({
            "message": "Difficulty is required."
        }), 400

    result = generate_coding_challenge_with_ai(
        course_title=course_title,
        lesson_title=lesson_title,
        difficulty=difficulty,
    )

    status_code = result.pop("status_code", 200)

    return jsonify(result), status_code