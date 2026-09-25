from shared.database.database import SessionLocal
from shared.models.user import User
from shared.models.course import Course
from shared.models.lesson import Lesson
from shared.models.user_progress import UserProgress

from services.progress_service.ldt_service import (
    update_learner_digital_twin
)

from services.progress_service.amre_service import (
    record_learning_history
)


def update_progress(
    user_id,
    course_id,
    completed_lessons,
    quiz_score,
    concept_performance=None
):
    db = SessionLocal()

    try:
        # ---------------------------------------------------------
        # Validate input values
        # ---------------------------------------------------------

        if not isinstance(completed_lessons, int):
            return {
                "message": "Completed lessons must be an integer.",
                "status_code": 400
            }

        if completed_lessons < 0:
            return {
                "message": "Completed lessons cannot be negative.",
                "status_code": 400
            }

        if not isinstance(quiz_score, (int, float)):
            return {
                "message": "Quiz score must be a number.",
                "status_code": 400
            }

        if quiz_score < 0 or quiz_score > 100:
            return {
                "message": "Quiz score must be between 0 and 100.",
                "status_code": 400
            }

        if concept_performance is not None:
            if not isinstance(concept_performance, list):
                return {
                    "message": "Concept performance must be a list.",
                    "status_code": 400
                }

        # ---------------------------------------------------------
        # Verify that the course belongs to the logged-in user
        # ---------------------------------------------------------

        course = (
            db.query(Course)
            .filter(
                Course.course_id == course_id,
                Course.user_id == user_id
            )
            .first()
        )

        if course is None:
            return {
                "message": "Course not found.",
                "status_code": 404
            }

        # ---------------------------------------------------------
        # Count total lessons in the course
        # ---------------------------------------------------------

        total_lessons = (
            db.query(Lesson)
            .filter(
                Lesson.course_id == course_id
            )
            .count()
        )

        if total_lessons == 0:
            return {
                "message": "Course has no lessons.",
                "status_code": 400
            }

        # ---------------------------------------------------------
        # Validate completed lessons
        # ---------------------------------------------------------

        if completed_lessons > total_lessons:
            return {
                "message": (
                    "Completed lessons cannot be greater "
                    "than the total number of lessons."
                ),
                "status_code": 400
            }

        # ---------------------------------------------------------
        # Calculate progress percentage
        # ---------------------------------------------------------

        progress_percentage = (
            completed_lessons / total_lessons
        ) * 100

        # ---------------------------------------------------------
        # Find existing progress record
        # ---------------------------------------------------------

        progress = (
            db.query(UserProgress)
            .filter(
                UserProgress.user_id == user_id,
                UserProgress.course_id == course_id
            )
            .first()
        )

        # ---------------------------------------------------------
        # Create or update progress
        # ---------------------------------------------------------

        if progress is None:
            progress = UserProgress(
                user_id=user_id,
                course_id=course_id,
                completed_lessons=completed_lessons,
                quiz_score=quiz_score,
                progress_percentage=progress_percentage
            )

            db.add(progress)

        else:
            progress.completed_lessons = completed_lessons
            progress.quiz_score = quiz_score
            progress.progress_percentage = progress_percentage

        db.commit()
        db.refresh(progress)

        # ---------------------------------------------------------
        # Update Learner Digital Twin
        # ---------------------------------------------------------

        ldt_result = update_learner_digital_twin(
            user_id=user_id,
            concept_performance=concept_performance
        )

        # ---------------------------------------------------------
        # Update Adaptive Memory & Retention Engine
        # ---------------------------------------------------------

        amre_result = None

        if concept_performance:
            amre_result = record_learning_history(
                user_id=user_id,
                course_id=course_id,
                concept_performance=concept_performance,
                event_type="normal"
            )

        # ---------------------------------------------------------
        # Return updated progress
        # ---------------------------------------------------------

        return {
            "message": "Progress updated successfully.",
            "progress_id": progress.progress_id,
            "user_id": progress.user_id,
            "course_id": progress.course_id,
            "completed_lessons": progress.completed_lessons,
            "total_lessons": total_lessons,
            "quiz_score": progress.quiz_score,
            "progress_percentage": progress.progress_percentage,
            "ldt": {
                "message": ldt_result.get("message"),
                "difficulty_level": ldt_result.get(
                    "difficulty_level"
                ),
                "quiz_accuracy": ldt_result.get(
                    "quiz_accuracy"
                ),
            },
            "amre": amre_result,
            "status_code": 200
        }

    except Exception as error:
        db.rollback()

        return {
            "message": "Progress update failed.",
            "error": str(error),
            "status_code": 500
        }

    finally:
        db.close()


def get_user_progress(user_id):
    db = SessionLocal()

    try:
        # ---------------------------------------------------------
        # Get all progress records for the user
        # ---------------------------------------------------------

        progress_records = (
            db.query(UserProgress)
            .filter(
                UserProgress.user_id == user_id
            )
            .all()
        )

        progress_list = []

        for progress in progress_records:

            # -----------------------------------------------------
            # Get course information
            # -----------------------------------------------------

            course = (
                db.query(Course)
                .filter(
                    Course.course_id == progress.course_id
                )
                .first()
            )

            # -----------------------------------------------------
            # Count total lessons
            # -----------------------------------------------------

            total_lessons = (
                db.query(Lesson)
                .filter(
                    Lesson.course_id == progress.course_id
                )
                .count()
            )

            progress_list.append({
                "progress_id": progress.progress_id,
                "user_id": progress.user_id,
                "course_id": progress.course_id,
                "course_title": course.title if course else None,
                "completed_lessons": progress.completed_lessons,
                "total_lessons": total_lessons,
                "quiz_score": progress.quiz_score,
                "progress_percentage": progress.progress_percentage
            })

        return {
            "user_id": user_id,
            "progress": progress_list,
            "status_code": 200
        }

    except Exception as error:
        return {
            "message": "Failed to retrieve progress.",
            "error": str(error),
            "status_code": 500
        }

    finally:
        db.close()