from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
import requests

from shared.database.database import SessionLocal
from shared.models.course import Course
from shared.models.lesson import Lesson
from shared.models.user_progress import UserProgress

from services.lesson_service.service import (
    generate_lesson,
    generate_quiz,
    evaluate_quiz,
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


@lesson_routes.route("/api/quiz/evaluate", methods=["POST"])
@jwt_required()
def submit_quiz():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"message": "Request body is required."}), 400

    lesson_id = data.get("lesson_id")
    answers = data.get("answers")

    if not lesson_id:
        return jsonify({"message": "Lesson ID is required."}), 400

    if not isinstance(answers, list) or not answers:
        return jsonify({
            "message": "Quiz answers are required."
        }), 400

    user_id = get_jwt_identity()

    result = evaluate_quiz(
        user_id=user_id,
        lesson_id=lesson_id,
        answers=answers
    )

    status_code = result.pop("status_code", 200)

    if status_code != 200:
        return jsonify(result), status_code

    # ---------------------------------------------------------
    # Get course and existing progress information
    # ---------------------------------------------------------

    db = SessionLocal()

    try:
        lesson = (
            db.query(Lesson)
            .filter(
                Lesson.lesson_id == lesson_id
            )
            .first()
        )

        if lesson is None:
            return jsonify({
                "message": "Lesson not found."
            }), 404

        course = (
            db.query(Course)
            .filter(
                Course.course_id == lesson.course_id,
                Course.user_id == user_id
            )
            .first()
        )

        if course is None:
            return jsonify({
                "message": "Course not found."
            }), 404

        progress = (
            db.query(UserProgress)
            .filter(
                UserProgress.user_id == user_id,
                UserProgress.course_id == course.course_id
            )
            .first()
        )

        completed_lessons = (
            progress.completed_lessons
            if progress is not None
            else 0
        )

    finally:
        db.close()

    # ---------------------------------------------------------
    # Update Progress Service with concept performance
    # ---------------------------------------------------------

    progress_payload = {
        "course_id": course.course_id,
        "completed_lessons": completed_lessons,
        "quiz_score": result.get("score", 0),
        "concept_performance": result.get(
            "concept_performance",
            []
        )
    }

    try:
        progress_response = requests.post(
            "http://127.0.0.1:5005/api/progress/update",
            json=progress_payload,
            headers={
                "Authorization": request.headers.get(
                    "Authorization"
                )
            },
            timeout=10
        )

        if progress_response.status_code >= 400:
            return jsonify({
                "message": "Quiz evaluated, but progress update failed.",
                "quiz_result": result,
                "progress_error": progress_response.json()
                if progress_response.content
                else None
            }), 500

    except requests.RequestException as error:
        return jsonify({
            "message": "Quiz evaluated, but progress service is unavailable.",
            "quiz_result": result,
            "error": str(error)
        }), 500

    return jsonify(result), 200


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