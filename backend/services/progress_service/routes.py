from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from services.progress_service.service import update_progress


progress_routes = Blueprint(
    "progress_routes",
    __name__
)


@progress_routes.route("/api/progress/update", methods=["POST"])
@jwt_required()
def update_user_progress():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "message": "Request body is required."
        }), 400

    course_id = data.get("course_id")
    completed_lessons = data.get("completed_lessons")
    quiz_score = data.get("quiz_score")

    if not course_id:
        return jsonify({
            "message": "Course ID is required."
        }), 400

    if completed_lessons is None:
        return jsonify({
            "message": "Completed lessons is required."
        }), 400

    if quiz_score is None:
        return jsonify({
            "message": "Quiz score is required."
        }), 400

    user_id = get_jwt_identity()

    result = update_progress(
        user_id=user_id,
        course_id=course_id,
        completed_lessons=completed_lessons,
        quiz_score=quiz_score
    )

    status_code = result.pop("status_code", 200)

    return jsonify(result), status_code