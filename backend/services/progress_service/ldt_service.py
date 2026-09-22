from shared.database.database import SessionLocal
from shared.models.course import Course
from shared.models.user_progress import UserProgress
from shared.models.learner_digital_twin import LearnerDigitalTwin


def update_learner_digital_twin(
    user_id,
    concept_performance=None
):
    db = SessionLocal()

    try:
        progress_records = (
            db.query(UserProgress)
            .filter(
                UserProgress.user_id == user_id
            )
            .all()
        )

        if not progress_records:
            return {
                "message": "No progress records found for learner.",
                "status_code": 400
            }

        total_quiz_score = 0
        total_progress_percentage = 0

        strengths = []
        weaknesses = []

        if concept_performance is not None:
            for concept in concept_performance:
                if not isinstance(concept, dict):
                    continue

                concept_name = concept.get("concept_name")
                knowledge_node_id = concept.get(
                    "knowledge_node_id"
                )
                accuracy = concept.get("accuracy")

                if (
                    not concept_name
                    or not knowledge_node_id
                    or accuracy is None
                ):
                    continue

                concept_data = {
                    "knowledge_node_id": knowledge_node_id,
                    "concept_name": concept_name,
                    "accuracy": round(float(accuracy), 2)
                }

                if accuracy >= 80:
                    strengths.append(concept_data)

                elif accuracy < 60:
                    weaknesses.append(concept_data)

        else:
            twin = (
                db.query(LearnerDigitalTwin)
                .filter(
                    LearnerDigitalTwin.user_id == user_id
                )
                .first()
            )

            if twin is not None:
                strengths = twin.strengths or []
                weaknesses = twin.weaknesses or []

        for progress in progress_records:
            total_quiz_score += progress.quiz_score
            total_progress_percentage += (
                progress.progress_percentage
            )

        quiz_accuracy = (
            total_quiz_score / len(progress_records)
        )

        learning_speed = (
            total_progress_percentage / len(progress_records)
        )

        difficulty_level = determine_difficulty_level(
            quiz_accuracy
        )

        twin = (
            db.query(LearnerDigitalTwin)
            .filter(
                LearnerDigitalTwin.user_id == user_id
            )
            .first()
        )

        if twin is None:
            twin = LearnerDigitalTwin(
                user_id=user_id,
                strengths=strengths,
                weaknesses=weaknesses,
                learning_speed=learning_speed,
                quiz_accuracy=quiz_accuracy,
                difficulty_level=difficulty_level
            )

            db.add(twin)

        else:
            twin.strengths = strengths
            twin.weaknesses = weaknesses
            twin.learning_speed = learning_speed
            twin.quiz_accuracy = quiz_accuracy
            twin.difficulty_level = difficulty_level

        db.commit()
        db.refresh(twin)

        return {
            "message": "Learner digital twin updated successfully.",
            "twin_id": twin.twin_id,
            "user_id": twin.user_id,
            "strengths": twin.strengths,
            "weaknesses": twin.weaknesses,
            "learning_speed": twin.learning_speed,
            "quiz_accuracy": quiz_accuracy,
            "difficulty_level": twin.difficulty_level,
            "status_code": 200
        }

    except Exception as error:
        db.rollback()

        return {
            "message": "Learner digital twin update failed.",
            "error": str(error),
            "status_code": 500
        }

    finally:
        db.close()


def determine_difficulty_level(quiz_accuracy):
    if quiz_accuracy >= 80:
        return "Advanced"

    if quiz_accuracy >= 60:
        return "Intermediate"

    return "Beginner"