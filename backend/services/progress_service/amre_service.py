from datetime import datetime, timedelta, timezone

from shared.database.database import SessionLocal
from shared.models.concept_learning_history import (
    ConceptLearningHistory
)
from shared.models.concept_retention_state import (
    ConceptRetentionState
)

# Import referenced models so SQLAlchemy registers
# the related tables when this service is imported directly.
from shared.models.user import User
from shared.models.course import Course
from shared.models.knowledge_node import KnowledgeNode


def record_learning_history(
    user_id,
    course_id,
    concept_performance,
    event_type="normal"
):
    db = SessionLocal()

    try:
        if not isinstance(concept_performance, list):
            return {
                "message": "Concept performance must be a list.",
                "status_code": 400
            }

        if event_type not in {"normal", "revision"}:
            return {
                "message": "Invalid AMRE event type.",
                "status_code": 400
            }

        saved_history = []
        retention_updates = []

        for concept in concept_performance:
            if not isinstance(concept, dict):
                continue

            knowledge_node_id = concept.get(
                "knowledge_node_id"
            )

            total_questions = concept.get(
                "total_questions"
            )

            correct_answers = concept.get(
                "correct_answers"
            )

            incorrect_answers = concept.get(
                "incorrect_answers"
            )

            accuracy = concept.get("accuracy")

            if not knowledge_node_id:
                continue

            if (
                total_questions is None
                or correct_answers is None
                or incorrect_answers is None
                or accuracy is None
            ):
                continue

            accuracy = float(accuracy)

            history = ConceptLearningHistory(
                user_id=user_id,
                course_id=course_id,
                knowledge_node_id=knowledge_node_id,
                event_type=event_type,
                total_questions=total_questions,
                correct_answers=correct_answers,
                incorrect_answers=incorrect_answers,
                accuracy=accuracy,
                event_timestamp=datetime.now(timezone.utc),
                created_at=datetime.now(timezone.utc)
            )

            db.add(history)
            saved_history.append(history)

            retention_result = update_retention_state(
                db=db,
                user_id=user_id,
                course_id=course_id,
                knowledge_node_id=knowledge_node_id,
                accuracy=accuracy
            )

            if retention_result is not None:
                retention_updates.append(
                    retention_result
                )

        if not saved_history:
            return {
                "message": "No valid concept performance data found.",
                "status_code": 400
            }

        db.commit()

        for history in saved_history:
            db.refresh(history)

        return {
            "message": "Concept learning history recorded successfully.",
            "records_created": len(saved_history),
            "history_ids": [
                history.history_id
                for history in saved_history
            ],
            "retention_updates": retention_updates,
            "status_code": 201
        }

    except Exception as error:
        db.rollback()

        return {
            "message": "Failed to record concept learning history.",
            "error": str(error),
            "status_code": 500
        }

    finally:
        db.close()


def update_retention_state(
    db,
    user_id,
    course_id,
    knowledge_node_id,
    accuracy
):
    """
    Create or update the current retention state
    for one learner, course, and knowledge concept.
    """

    retention_state = (
        db.query(ConceptRetentionState)
        .filter(
            ConceptRetentionState.user_id == user_id,
            ConceptRetentionState.course_id == course_id,
            ConceptRetentionState.knowledge_node_id
            == knowledge_node_id
        )
        .first()
    )

    if retention_state is None:
        stability = calculate_initial_stability(
            accuracy
        )

        retention_state = ConceptRetentionState(
            user_id=user_id,
            course_id=course_id,
            knowledge_node_id=knowledge_node_id,
            stability=stability,
            next_review_at=calculate_next_review(
                stability
            ),
            updated_at=datetime.now(timezone.utc)
        )

        db.add(retention_state)

        return {
            "knowledge_node_id": knowledge_node_id,
            "stability": stability,
            "action": "created"
        }

    old_stability = retention_state.stability

    new_stability = calculate_updated_stability(
        old_stability,
        accuracy
    )

    retention_state.stability = new_stability
    retention_state.next_review_at = calculate_next_review(
        new_stability
    )
    retention_state.updated_at = datetime.now(
        timezone.utc
    )

    return {
        "knowledge_node_id": knowledge_node_id,
        "previous_stability": old_stability,
        "stability": new_stability,
        "action": "updated"
    }


def calculate_initial_stability(accuracy):
    """
    Determine starting stability for a concept.

    Stability represents the number of days before
    the concept should be reviewed again.
    """

    if accuracy >= 80:
        return 3.0

    if accuracy >= 60:
        return 2.0

    return 1.0


def calculate_updated_stability(
    current_stability,
    accuracy
):
    """
    Update stability according to the learner's
    latest concept performance.
    """

    if accuracy >= 80:
        new_stability = current_stability * 1.5

    elif accuracy >= 60:
        new_stability = current_stability * 1.2

    else:
        new_stability = current_stability * 0.5

    # Keep stability within a reasonable range.
    new_stability = max(
        1.0,
        min(new_stability, 30.0)
    )

    return round(new_stability, 2)


def calculate_next_review(stability):
    """
    Calculate the next review time from stability.

    Stability is represented in days.
    """

    return (
        datetime.now(timezone.utc)
        + timedelta(days=stability)
    )