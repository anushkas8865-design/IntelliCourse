from shared.database.database import Base, engine

from shared.models.user import User
from shared.models.course import Course
from shared.models.lesson import Lesson
from shared.models.lesson_video import LessonVideo
from shared.models.quiz import Quiz
from shared.models.coding_challenge import CodingChallenge
from shared.models.user_progress import UserProgress
from shared.models.ai_chat_history import AIChatHistory
from shared.models.learner_digital_twin import LearnerDigitalTwin
from shared.models.knowledge_node import KnowledgeNode
from shared.models.knowledge_relationship import KnowledgeRelationship
from shared.models.concept_learning_history import ConceptLearningHistory
from shared.models.concept_retention_state import ConceptRetentionState


def initialize_database():
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")


if __name__ == "__main__":
    initialize_database()