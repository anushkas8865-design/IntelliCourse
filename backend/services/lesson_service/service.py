import json
import os
from uuid import uuid4
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from dotenv import load_dotenv

from shared.database.database import SessionLocal
from shared.models.course import Course
from shared.models.lesson import Lesson
from shared.models.lesson_video import LessonVideo
from shared.models.quiz import Quiz
from shared.models.knowledge_node import KnowledgeNode
from shared.models.coding_challenge import CodingChallenge
from shared.models.revision_quiz_attempt import RevisionQuizAttempt
from shared.models.revision_quiz_answer import RevisionQuizAnswer
from shared.models.concept_learning_history import (
    ConceptLearningHistory
)
from shared.models.learner_digital_twin import LearnerDigitalTwin

load_dotenv()

AI_SERVICE_URL = (
    "http://127.0.0.1:5003/api/ai/lesson"
)

AI_QUIZ_SERVICE_URL = (
    "http://127.0.0.1:5003/api/ai/quiz"
)

AI_REVISION_QUIZ_SERVICE_URL = (
    "http://127.0.0.1:5003/api/ai/revision-quiz"
)

AI_CHALLENGE_SERVICE_URL = (
    "http://127.0.0.1:5003/api/ai/challenge"
)

YOUTUBE_API_URL = (
    "https://www.googleapis.com/youtube/v3/search"
)

YOUTUBE_MAX_RESULTS = 3


# ---------------------------------------------------------
# PROGRAMMING COURSE DETECTION
# ---------------------------------------------------------

PROGRAMMING_KEYWORDS = [
    "programming",
    "coding",
    "python",
    "java",
    "javascript",
    "typescript",
    "c++",
    "c#",
    "php",
    "ruby",
    "kotlin",
    "swift",
    "rust",
    "golang",
    "go programming",
    "web development",
    "software development",
    "data structures",
    "algorithms",
]


def is_programming_course(course_title, course_description):
    text = f"{course_title} {course_description}".lower()

    for keyword in PROGRAMMING_KEYWORDS:
        if keyword in text:
            return True

    return False


# ---------------------------------------------------------
# LESSON GENERATION
# ---------------------------------------------------------

def generate_lesson(
    user_id,
    course_id,
    title,
    sequence_number
):
    db = SessionLocal()

    try:
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

        ai_result = call_ai_service(
            course_id=course_id,
            title=title,
            sequence_number=sequence_number
        )

        if (
            "status_code" in ai_result
            and ai_result["status_code"] != 200
        ):
            return ai_result

        lesson = Lesson(
            course_id=course_id,
            title=ai_result["title"],
            content=build_lesson_content(ai_result),
            summary=ai_result["summary"],
            sequence_number=ai_result["sequence_number"]
        )

        db.add(lesson)
        db.flush()

        youtube_videos = search_youtube_videos(
            lesson.title
        )

        for video in youtube_videos:
            lesson_video = LessonVideo(
                lesson_id=lesson.lesson_id,
                title=video["title"],
                youtube_url=video["youtube_url"]
            )

            db.add(lesson_video)

        db.commit()
        db.refresh(lesson)

        return {
            "message": (
                "Lesson generated and saved successfully."
            ),
            "lesson_id": lesson.lesson_id,
            "course_id": lesson.course_id,
            "title": lesson.title,
            "content": lesson.content,
            "summary": lesson.summary,
            "sequence_number": lesson.sequence_number,
            "videos": youtube_videos,
            "status_code": 201
        }

    except Exception as error:
        db.rollback()

        return {
            "message": "Lesson generation failed.",
            "error": str(error),
            "status_code": 500
        }

    finally:
        db.close()


def call_ai_service(
    course_id,
    title,
    sequence_number
):
    payload = json.dumps(
        {
            "course_id": course_id,
            "title": title,
            "sequence_number": sequence_number
        }
    ).encode("utf-8")

    request = Request(
        AI_SERVICE_URL,
        data=payload,
        headers={
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:
        with urlopen(request, timeout=120) as response:
            return json.loads(
                response.read().decode("utf-8")
            )

    except HTTPError as error:
        try:
            error_body = error.read().decode("utf-8")
            error_data = json.loads(error_body)

            return {
                "message": error_data.get(
                    "message",
                    "AI Service returned an error."
                ),
                "status_code": 502
            }

        except Exception:
            return {
                "message": "AI Service returned an error.",
                "status_code": 502
            }

    except URLError:
        return {
            "message": "AI Service is unavailable.",
            "status_code": 503
        }

    except json.JSONDecodeError:
        return {
            "message": "AI Service returned invalid JSON.",
            "status_code": 502
        }


# ---------------------------------------------------------
# YOUTUBE VIDEO SEARCH
# ---------------------------------------------------------

def search_youtube_videos(lesson_title):
    api_key = os.getenv("YOUTUBE_API_KEY")

    if not api_key:
        return []

    # Remove common instructional/generic words so the search
    # focuses on the actual lesson topic.
    generic_words = {
        "a",
        "an",
        "and",
        "the",
        "of",
        "to",
        "for",
        "in",
        "on",
        "with",
        "using",
        "introduction",
        "understanding",
        "practical",
        "fundamentals",
        "fundamental",
        "basics",
        "basic",
        "advanced",
        "overview",
        "guide",
        "tutorial",
    }

    words = lesson_title.split()

    keywords = [
        word.strip(".,:;!?()[]{}").lower()
        for word in words
        if word.strip(".,:;!?()[]{}").lower() not in generic_words
    ]

    # Keep the original title if keyword processing produces
    # nothing useful.
    primary_query = " ".join(keywords).strip()

    if not primary_query:
        primary_query = lesson_title.strip()

    queries = [primary_query]

    # Create one broader fallback query from the first
    # meaningful keywords if the primary search is insufficient.
    if len(keywords) > 3:
        fallback_query = " ".join(keywords[:3]).strip()

        if fallback_query and fallback_query != primary_query:
            queries.append(fallback_query)

    videos = []
    seen_video_ids = set()

    for query in queries:
        params = urlencode(
            {
                "part": "snippet",
                "q": query,
                "type": "video",
                "maxResults": YOUTUBE_MAX_RESULTS,
                "key": api_key
            }
        )

        request = Request(
            f"{YOUTUBE_API_URL}?{params}",
            method="GET"
        )

        try:
            with urlopen(request, timeout=30) as response:
                data = json.loads(
                    response.read().decode("utf-8")
                )

            for item in data.get("items", []):
                video_id = item.get("id", {}).get("videoId")
                snippet = item.get("snippet", {})

                if not video_id:
                    continue

                if video_id in seen_video_ids:
                    continue

                seen_video_ids.add(video_id)

                videos.append(
                    {
                        "title": snippet.get("title", ""),
                        "youtube_url": (
                            f"https://www.youtube.com/watch?v={video_id}"
                        )
                    }
                )

                if len(videos) >= YOUTUBE_MAX_RESULTS:
                    return videos

        except (
            HTTPError,
            URLError,
            json.JSONDecodeError
        ):
            continue

    return videos

# ---------------------------------------------------------
# LESSON CONTENT
# ---------------------------------------------------------

def build_lesson_content(ai_result):
    objectives = "\n".join(
        f"- {objective}"
        for objective in ai_result["objectives"]
    )

    examples = "\n".join(
        f"- {example}"
        for example in ai_result["real_world_examples"]
    )

    return (
        f"Learning Objectives:\n"
        f"{objectives}\n\n"
        f"Explanation:\n"
        f"{ai_result['explanation']}\n\n"
        f"Real-World Examples:\n"
        f"{examples}"
    )


# ---------------------------------------------------------
# GET LESSON
# ---------------------------------------------------------

def get_lesson_by_id(lesson_id):
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
            return None

        return {
            "lesson_id": lesson.lesson_id,
            "course_id": lesson.course_id,
            "title": lesson.title,
            "content": lesson.content,
            "summary": lesson.summary,
            "sequence_number": lesson.sequence_number
        }

    finally:
        db.close()


# ---------------------------------------------------------
# GET YOUTUBE VIDEOS
# ---------------------------------------------------------

def get_videos_by_lesson_id(lesson_id):
    db = SessionLocal()

    try:
        videos = (
            db.query(LessonVideo)
            .filter(
                LessonVideo.lesson_id == lesson_id
            )
            .all()
        )

        # If videos already exist, keep the existing
        # database-first behavior.
        if videos:
            return [
                {
                    "video_id": video.video_id,
                    "lesson_id": video.lesson_id,
                    "title": video.title,
                    "youtube_url": video.youtube_url
                }
                for video in videos
            ]

        # No stored videos exist, so get the lesson title
        # and search YouTube as a fallback.
        lesson = (
            db.query(Lesson)
            .filter(
                Lesson.lesson_id == lesson_id
            )
            .first()
        )

        if lesson is None:
            return []

        youtube_videos = search_youtube_videos(
            lesson.title
        )

        # Store the newly found videos so that future requests
        # use the database instead of searching YouTube again.
        for video_data in youtube_videos:
            video = LessonVideo(
                lesson_id=lesson_id,
                title=video_data["title"],
                youtube_url=video_data["youtube_url"]
            )

            db.add(video)

        if youtube_videos:
            db.commit()

        # Return the same response structure used previously.
        return [
            {
                "video_id": video.video_id,
                "lesson_id": video.lesson_id,
                "title": video.title,
                "youtube_url": video.youtube_url
            }
            for video in (
                db.query(LessonVideo)
                .filter(
                    LessonVideo.lesson_id == lesson_id
                )
                .all()
            )
        ]

    finally:
        db.close()

# ---------------------------------------------------------
# QUIZ GENERATION
# ---------------------------------------------------------

def generate_quiz(
    user_id,
    lesson_id,
    number_of_questions
):
    db = SessionLocal()

    try:
        lesson = (
            db.query(Lesson)
            .join(
                Course,
                Lesson.course_id == Course.course_id
            )
            .filter(
                Lesson.lesson_id == lesson_id,
                Course.user_id == user_id
            )
            .first()
        )

        if lesson is None:
            return {
                "message": "Lesson not found.",
                "status_code": 404
            }

        knowledge_nodes = (
            db.query(KnowledgeNode)
            .filter(
                KnowledgeNode.lesson_id
                == lesson.lesson_id
            )
            .all()
        )

        if not knowledge_nodes:
            return {
                "message": (
                    "No knowledge concepts found "
                    "for this lesson."
                ),
                "status_code": 400
            }

        concepts = [
            {
                "node_id": node.node_id,
                "concept_name": node.concept_name,
                "description": node.description
            }
            for node in knowledge_nodes
        ]

        ai_result = call_quiz_ai_service(
            lesson_id=lesson.lesson_id,
            lesson_title=lesson.title,
            number_of_questions=number_of_questions,
            concepts=concepts
        )

        if (
            "status_code" in ai_result
            and ai_result["status_code"] != 200
        ):
            return ai_result

        questions = ai_result.get("questions")

        if not isinstance(questions, list):
            return {
                "message": (
                    "AI Service returned invalid "
                    "quiz data."
                ),
                "status_code": 502
            }

        concept_node_map = {
            node.concept_name.strip().lower(): node
            for node in knowledge_nodes
        }

        saved_quizzes = []

        for question_data in questions:
            concept_name = question_data.get(
                "concept_name"
            )

            if not isinstance(concept_name, str):
                db.rollback()

                return {
                    "message": (
                        "AI quiz question is missing "
                        "a valid concept."
                    ),
                    "status_code": 502
                }

            knowledge_node = concept_node_map.get(
                concept_name.strip().lower()
            )

            if knowledge_node is None:
                db.rollback()

                return {
                    "message": (
                        "AI quiz question references "
                        "an unknown concept."
                    ),
                    "status_code": 502
                }

            quiz = Quiz(
                lesson_id=lesson.lesson_id,
                knowledge_node_id=knowledge_node.node_id,
                quiz_type="normal",
                question=question_data["question"],
                option_a=question_data["option_a"],
                option_b=question_data["option_b"],
                option_c=question_data["option_c"],
                option_d=question_data["option_d"],
                correct_answer=question_data["correct_answer"],
                explanation=question_data["explanation"]
            )

            db.add(quiz)
            saved_quizzes.append(quiz)

        db.commit()

        return {
            "message": (
                "Quiz generated and saved successfully."
            ),
            "lesson_id": lesson.lesson_id,
            "lesson_title": lesson.title,
            "questions": [
                {
                    "quiz_id": quiz.quiz_id,
                    "lesson_id": quiz.lesson_id,
                    "question": quiz.question,
                    "option_a": quiz.option_a,
                    "option_b": quiz.option_b,
                    "option_c": quiz.option_c,
                    "option_d": quiz.option_d,
                    "correct_answer": quiz.correct_answer,
                    "explanation": quiz.explanation,
                    "knowledge_node_id": (
                        quiz.knowledge_node_id
                    ),
                    "quiz_type": quiz.quiz_type
                }
                for quiz in saved_quizzes
            ],
            "status_code": 201
        }

    except Exception as error:
        db.rollback()

        return {
            "message": "Quiz generation failed.",
            "error": str(error),
            "status_code": 500
        }

    finally:
        db.close()


def adjust_revision_difficulty(
    course_difficulty,
    concept_accuracy
):
    """
    Adjust revision difficulty using the learner's
    latest concept-specific performance.
    """

    difficulty_levels = [
        "Beginner",
        "Intermediate",
        "Advanced"
    ]

    normalized_course_difficulty = (
        str(course_difficulty).strip().title()
    )

    if normalized_course_difficulty not in difficulty_levels:
        normalized_course_difficulty = "Intermediate"

    current_index = difficulty_levels.index(
        normalized_course_difficulty
    )

    if concept_accuracy < 60:
        current_index -= 1

    elif concept_accuracy >= 80:
        current_index += 1

    current_index = max(
        0,
        min(current_index, len(difficulty_levels) - 1)
    )

    return difficulty_levels[current_index]


def get_revision_concept_difficulties(
    db,
    user_id,
    course_id,
    course_difficulty,
    knowledge_node_ids
):
    """
    Determine the adaptive revision difficulty for
    each due knowledge concept.

    Latest concept-specific performance is used when
    available. LDT difficulty is used as the fallback.
    """

    history_records = (
        db.query(ConceptLearningHistory)
        .filter(
            ConceptLearningHistory.user_id == user_id,
            ConceptLearningHistory.course_id == course_id,
            ConceptLearningHistory.knowledge_node_id.in_(
                knowledge_node_ids
            )
        )
        .order_by(
            ConceptLearningHistory.event_timestamp.desc(),
            ConceptLearningHistory.created_at.desc()
        )
        .all()
    )

    latest_history = {}

    for history in history_records:
        if history.knowledge_node_id not in latest_history:
            latest_history[
                history.knowledge_node_id
            ] = history

    learner_digital_twin = (
        db.query(LearnerDigitalTwin)
        .filter(
            LearnerDigitalTwin.user_id == user_id
        )
        .first()
    )

    fallback_difficulty = course_difficulty

    if (
        learner_digital_twin is not None
        and learner_digital_twin.difficulty_level
    ):
        fallback_difficulty = (
            learner_digital_twin.difficulty_level
        )

    concept_difficulties = {}

    for knowledge_node_id in knowledge_node_ids:
        history = latest_history.get(
            knowledge_node_id
        )

        if history is not None:
            difficulty = adjust_revision_difficulty(
                course_difficulty=course_difficulty,
                concept_accuracy=history.accuracy
            )

        else:
            difficulty = (
                str(fallback_difficulty).strip().title()
            )

            if difficulty not in {
                "Beginner",
                "Intermediate",
                "Advanced"
            }:
                difficulty = (
                    str(course_difficulty).strip().title()
                )

        concept_difficulties[
            knowledge_node_id
        ] = difficulty

    return concept_difficulties


# ---------------------------------------------------------
# REVISION QUIZ GENERATION
# ---------------------------------------------------------

def generate_revision_quiz(
    user_id,
    course_id,
    number_of_questions
):
    db = SessionLocal()

    try:
        if not isinstance(number_of_questions, int):
            return {
                "message": "Number of questions must be an integer.",
                "status_code": 400
            }

        if number_of_questions <= 0:
            return {
                "message": "Number of questions must be greater than zero.",
                "status_code": 400
            }

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

        from services.progress_service.amre_service import (
            get_due_revision_concepts
        )

        revision_result = get_due_revision_concepts(
            user_id=user_id
        )

        if (
            "status_code" in revision_result
            and revision_result["status_code"] != 200
        ):
            return revision_result

        due_concepts = [
            concept
            for concept in revision_result.get("concepts", [])
            if concept.get("course_id") == course_id
        ]

        if not due_concepts:
            return {
                "message": "No concepts are currently due for revision.",
                "concepts": [],
                "questions": [],
                "status_code": 200
            }

        number_of_questions = max(
            5,
            len(due_concepts)
        )

        knowledge_node_ids = [
            concept["knowledge_node_id"]
            for concept in due_concepts
            if concept.get("knowledge_node_id")
        ]

        knowledge_nodes = (
            db.query(KnowledgeNode)
            .filter(
                KnowledgeNode.node_id.in_(
                    knowledge_node_ids
                ),
                KnowledgeNode.course_id == course_id
            )
            .all()
        )

        if not knowledge_nodes:
            return {
                "message": "No knowledge concepts found for revision.",
                "status_code": 400
            }

        concept_difficulties = (
            get_revision_concept_difficulties(
                db=db,
                user_id=user_id,
                course_id=course_id,
                course_difficulty=course.difficulty,
                knowledge_node_ids=knowledge_node_ids
            )
        )

        knowledge_node_map = {
            node.node_id: node
            for node in knowledge_nodes
        }

        concepts = []

        for concept in due_concepts:
            knowledge_node = knowledge_node_map.get(
                concept["knowledge_node_id"]
            )

            if knowledge_node is None:
                continue

            concepts.append({
                "node_id": knowledge_node.node_id,
                "concept_name": knowledge_node.concept_name,
                "description": knowledge_node.description,
                "difficulty": concept_difficulties.get(
                    knowledge_node.node_id,
                    course.difficulty
                )
            })

        if not concepts:
            return {
                "message": "No valid knowledge concepts found for revision.",
                "status_code": 400
            }

        ai_result = call_revision_quiz_ai_service(
            course_id=course_id,
            course_title=course.title,
            number_of_questions=number_of_questions,
            concepts=concepts
        )

        if (
            "status_code" in ai_result
            and ai_result["status_code"] != 200
        ):
            return ai_result

        questions = ai_result.get("questions")

        if not isinstance(questions, list):
            return {
                "message": "AI Service returned invalid revision quiz data.",
                "status_code": 502
            }

        concept_node_map = {
            node.concept_name.strip().lower(): node
            for node in knowledge_nodes
        }

        revision_quiz_id = str(uuid4())

        saved_quizzes = []

        for question_data in questions:
            concept_name = question_data.get(
                "concept_name"
            )

            if not isinstance(concept_name, str):
                db.rollback()

                return {
                    "message": (
                        "AI revision quiz question is missing "
                        "a valid concept."
                    ),
                    "status_code": 502
                }

            knowledge_node = concept_node_map.get(
                concept_name.strip().lower()
            )

            if knowledge_node is None:
                db.rollback()

                return {
                    "message": (
                        "AI revision quiz question references "
                        "an unknown concept."
                    ),
                    "status_code": 502
                }

            quiz = Quiz(
                lesson_id=knowledge_node.lesson_id,
                knowledge_node_id=knowledge_node.node_id,
                revision_quiz_id=revision_quiz_id,
                quiz_type="revision",
                question=question_data["question"],
                option_a=question_data["option_a"],
                option_b=question_data["option_b"],
                option_c=question_data["option_c"],
                option_d=question_data["option_d"],
                correct_answer=question_data["correct_answer"],
                explanation=question_data["explanation"]
            )

            db.add(quiz)
            saved_quizzes.append(quiz)

        db.commit()

        for quiz in saved_quizzes:
            db.refresh(quiz)

        return {
            "message": "Revision quiz generated and saved successfully.",
            "course_id": course_id,
            "course_title": course.title,
            "quiz_type": "revision",
            "revision_quiz_id": revision_quiz_id,
            "questions": [
                {
                    "quiz_id": quiz.quiz_id,
                    "revision_quiz_id": quiz.revision_quiz_id,
                    "lesson_id": quiz.lesson_id,
                    "question": quiz.question,
                    "option_a": quiz.option_a,
                    "option_b": quiz.option_b,
                    "option_c": quiz.option_c,
                    "option_d": quiz.option_d,
                    "correct_answer": quiz.correct_answer,
                    "explanation": quiz.explanation,
                    "knowledge_node_id": quiz.knowledge_node_id,
                    "quiz_type": quiz.quiz_type
                }
                for quiz in saved_quizzes
            ],
            "status_code": 201
        }

    except Exception as error:
        db.rollback()

        return {
            "message": "Revision quiz generation failed.",
            "error": str(error),
            "status_code": 500
        }

    finally:
        db.close()


# ---------------------------------------------------------
# QUIZ ANSWER EVALUATION
# ---------------------------------------------------------

def evaluate_quiz(
    user_id,
    lesson_id,
    answers,
    quiz_type="normal"
):
    db = SessionLocal()

    try:
        if not isinstance(answers, list) or not answers:
            return {
                "message": "Quiz answers are required.",
                "status_code": 400
            }

        quiz_ids = []

        for answer_data in answers:
            if not isinstance(answer_data, dict):
                return {
                    "message": "Invalid quiz answer format.",
                    "status_code": 400
                }

            quiz_id = answer_data.get("quiz_id")
            selected_answer = answer_data.get("answer")

            if not quiz_id or not selected_answer:
                return {
                    "message": (
                        "Each answer must contain "
                        "quiz_id and answer."
                    ),
                    "status_code": 400
                }

            if not isinstance(selected_answer, str):
                return {
                    "message": (
                        "Quiz answer must be a string."
                    ),
                    "status_code": 400
                }

            selected_answer = (
                selected_answer.strip().upper()
            )

            if selected_answer not in {
                "A",
                "B",
                "C",
                "D"
            }:
                return {
                    "message": (
                        "Quiz answer must be A, B, C, or D."
                    ),
                    "status_code": 400
                }

            quiz_ids.append(quiz_id)

        # -----------------------------------------------------
        # NORMAL QUIZ
        # -----------------------------------------------------

        if quiz_type == "normal":

            lesson = (
                db.query(Lesson)
                .join(
                    Course,
                    Lesson.course_id == Course.course_id
                )
                .filter(
                    Lesson.lesson_id == lesson_id,
                    Course.user_id == user_id
                )
                .first()
            )

            if lesson is None:
                return {
                    "message": "Lesson not found.",
                    "status_code": 404
                }

            quizzes = (
                db.query(Quiz)
                .filter(
                    Quiz.lesson_id == lesson_id,
                    Quiz.quiz_id.in_(quiz_ids),
                    Quiz.quiz_type == "normal"
                )
                .all()
            )

            quiz_map = {
                quiz.quiz_id: quiz
                for quiz in quizzes
            }

            if len(quiz_map) != len(set(quiz_ids)):
                return {
                    "message": (
                        "One or more quiz questions do not "
                        "belong to this lesson."
                    ),
                    "status_code": 400
                }

            course_id = lesson.course_id
            lesson_title = lesson.title
            result_lesson_id = lesson.lesson_id

        # -----------------------------------------------------
        # REVISION QUIZ
        # -----------------------------------------------------

        elif quiz_type == "revision":

            quizzes = (
                db.query(Quiz)
                .join(
                    Lesson,
                    Quiz.lesson_id == Lesson.lesson_id
                )
                .join(
                    Course,
                    Lesson.course_id == Course.course_id
                )
                .filter(
                    Quiz.quiz_id.in_(quiz_ids),
                    Quiz.quiz_type == "revision",
                    Course.user_id == user_id
                )
                .all()
            )

            quiz_map = {
                quiz.quiz_id: quiz
                for quiz in quizzes
            }

            if len(quiz_map) != len(set(quiz_ids)):
                return {
                    "message": (
                        "One or more revision quiz questions "
                        "are invalid."
                    ),
                    "status_code": 400
                }

            # -------------------------------------------------
            # CHECK REVISION QUIZ GROUP
            # -------------------------------------------------

            revision_quiz_ids = {
                quiz.revision_quiz_id
                for quiz in quizzes
            }

            if None in revision_quiz_ids:
                return {
                    "message": (
                        "One or more revision quiz questions "
                        "are not linked to a revision quiz."
                    ),
                    "status_code": 400
                }

            if len(revision_quiz_ids) != 1:
                return {
                    "message": (
                        "All revision quiz questions must "
                        "belong to the same generated revision quiz."
                    ),
                    "status_code": 400
                }

            revision_quiz_id = next(
                iter(revision_quiz_ids)
            )

            # -------------------------------------------------
            # GET ALL QUESTIONS FROM THIS GENERATED QUIZ
            # -------------------------------------------------

            generated_quizzes = (
                db.query(Quiz)
                .filter(
                    Quiz.revision_quiz_id == revision_quiz_id,
                    Quiz.quiz_type == "revision"
                )
                .all()
            )

            generated_quiz_ids = {
                quiz.quiz_id
                for quiz in generated_quizzes
            }

            submitted_quiz_ids = set(quiz_ids)

            if submitted_quiz_ids != generated_quiz_ids:
                return {
                    "message": (
                        "All questions from the generated "
                        "revision quiz must be answered."
                    ),
                    "status_code": 400
                }

            course_ids = set()

            for quiz in quizzes:
                lesson = (
                    db.query(Lesson)
                    .filter(
                        Lesson.lesson_id == quiz.lesson_id
                    )
                    .first()
                )

                if lesson is None:
                    return {
                        "message": (
                            "Lesson for a revision quiz "
                            "question was not found."
                        ),
                        "status_code": 500
                    }

                course_ids.add(lesson.course_id)

            if len(course_ids) != 1:
                return {
                    "message": (
                        "Revision quiz questions must belong "
                        "to the same course."
                    ),
                    "status_code": 400
                }

            course_id = next(iter(course_ids))

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

            lesson_title = course.title
            result_lesson_id = None

        else:
            return {
                "message": "Invalid quiz type.",
                "status_code": 400
            }

        # -----------------------------------------------------
        # GET KNOWLEDGE NODES
        # -----------------------------------------------------

        knowledge_node_ids = {
            quiz.knowledge_node_id
            for quiz in quizzes
        }

        if None in knowledge_node_ids:
            return {
                "message": (
                    "One or more quiz questions are not "
                    "linked to a knowledge concept."
                ),
                "status_code": 500
            }

        knowledge_nodes = (
            db.query(KnowledgeNode)
            .filter(
                KnowledgeNode.node_id.in_(
                    knowledge_node_ids
                )
            )
            .all()
        )

        knowledge_node_map = {
            node.node_id: node
            for node in knowledge_nodes
        }

        results = []

        concept_performance = {}

        # -----------------------------------------------------
        # EVALUATE ANSWERS
        # -----------------------------------------------------

        for answer_data in answers:
            quiz_id = answer_data["quiz_id"]

            selected_answer = (
                answer_data["answer"]
                .strip()
                .upper()
            )

            quiz = quiz_map[quiz_id]

            correct = (
                selected_answer
                == quiz.correct_answer.upper()
            )

            knowledge_node = knowledge_node_map.get(
                quiz.knowledge_node_id
            )

            if knowledge_node is None:
                return {
                    "message": (
                        "Knowledge concept for quiz "
                        "question was not found."
                    ),
                    "status_code": 500
                }

            node_id = knowledge_node.node_id

            if node_id not in concept_performance:
                concept_performance[node_id] = {
                    "knowledge_node_id": node_id,
                    "concept_name": (
                        knowledge_node.concept_name
                    ),
                    "total_questions": 0,
                    "correct_answers": 0,
                    "incorrect_answers": 0
                }

            concept_performance[node_id][
                "total_questions"
            ] += 1

            if correct:
                concept_performance[node_id][
                    "correct_answers"
                ] += 1
            else:
                concept_performance[node_id][
                    "incorrect_answers"
                ] += 1

            results.append(
                {
                    "quiz_id": quiz.quiz_id,
                    "knowledge_node_id": node_id,
                    "concept_name": (
                        knowledge_node.concept_name
                    ),
                    "selected_answer": selected_answer,
                    "correct": correct,
                    "correct_answer": (
                        quiz.correct_answer
                    ),
                    "explanation": quiz.explanation,
                    "quiz_type": quiz.quiz_type
                }
            )

        total_questions = len(results)

        correct_answers = sum(
            1
            for result in results
            if result["correct"]
        )

        score = (
            (correct_answers / total_questions) * 100
            if total_questions > 0
            else 0
        )

        for performance in concept_performance.values():
            performance["accuracy"] = (
                performance["correct_answers"]
                / performance["total_questions"]
            ) * 100

        # -----------------------------------------------------
        # SAVE REVISION QUIZ ATTEMPT
        # -----------------------------------------------------

        if quiz_type == "revision":

            revision_attempt = RevisionQuizAttempt(
                revision_quiz_id=revision_quiz_id,
                user_id=user_id
            )

            db.add(revision_attempt)
            db.flush()

            for answer_data in answers:
                revision_answer = RevisionQuizAnswer(
                    attempt_id=revision_attempt.attempt_id,
                    quiz_id=answer_data["quiz_id"],
                    selected_answer=(
                        answer_data["answer"]
                        .strip()
                        .upper()
                    )
                )

                db.add(revision_answer)

            db.commit()

        return {
            "message": "Quiz evaluated successfully.",
            "lesson_id": result_lesson_id,
            "course_id": course_id,
            "lesson_title": lesson_title,
            "quiz_type": quiz_type,
            "total_questions": total_questions,
            "correct_answers": correct_answers,
            "incorrect_answers": (
                total_questions - correct_answers
            ),
            "score": round(score, 2),
            "results": results,
            "concept_performance": list(
                concept_performance.values()
            ),
            "status_code": 200
        }

    except Exception as error:
        db.rollback()

        return {
            "message": "Quiz evaluation failed.",
            "error": str(error),
            "status_code": 500
        }

    finally:
        db.close()


# ---------------------------------------------------------
# REVISION QUIZ HISTORY
# ---------------------------------------------------------

def get_revision_quiz_history(user_id):
    db = SessionLocal()

    try:
        attempts = (
            db.query(RevisionQuizAttempt)
            .filter(
                RevisionQuizAttempt.user_id == user_id
            )
            .order_by(
                RevisionQuizAttempt.attempted_at.desc()
            )
            .all()
        )

        history = []

        for attempt in attempts:
            quiz_rows = (
                db.query(Quiz, Lesson, Course)
                .join(
                    Lesson,
                    Quiz.lesson_id == Lesson.lesson_id
                )
                .join(
                    Course,
                    Lesson.course_id == Course.course_id
                )
                .filter(
                    Quiz.revision_quiz_id
                    == attempt.revision_quiz_id,
                    Quiz.quiz_type == "revision",
                    Course.user_id == user_id
                )
                .all()
            )

            if not quiz_rows:
                continue

            answers = (
                db.query(RevisionQuizAnswer)
                .filter(
                    RevisionQuizAnswer.attempt_id
                    == attempt.attempt_id
                )
                .all()
            )

            answer_map = {
                answer.quiz_id: answer.selected_answer
                for answer in answers
            }

            total_questions = 0
            correct_answers = 0

            for quiz, lesson, course in quiz_rows:
                selected_answer = answer_map.get(
                    quiz.quiz_id
                )

                if selected_answer is None:
                    continue

                total_questions += 1

                if (
                    selected_answer.strip().upper()
                    == quiz.correct_answer.strip().upper()
                ):
                    correct_answers += 1

            score = (
                (correct_answers / total_questions) * 100
                if total_questions > 0
                else 0
            )

            course = quiz_rows[0][2]

            history.append({
                "attempt_id": attempt.attempt_id,
                "revision_quiz_id": (
                    attempt.revision_quiz_id
                ),
                "course_id": course.course_id,
                "course_title": course.title,
                "attempted_at": (
                    attempt.attempted_at.isoformat()
                    if attempt.attempted_at
                    else None
                ),
                "total_questions": total_questions,
                "correct_answers": correct_answers,
                "incorrect_answers": (
                    total_questions - correct_answers
                ),
                "score": round(score, 2)
            })

        return {
            "history": history,
            "status_code": 200
        }

    except Exception as error:
        return {
            "message": "Unable to load revision quiz history.",
            "error": str(error),
            "status_code": 500
        }

    finally:
        db.close()


def get_revision_quiz_attempt(
    user_id,
    attempt_id
):
    db = SessionLocal()

    try:
        attempt = (
            db.query(RevisionQuizAttempt)
            .filter(
                RevisionQuizAttempt.attempt_id
                == attempt_id,
                RevisionQuizAttempt.user_id
                == user_id
            )
            .first()
        )

        if attempt is None:
            return {
                "message": "Revision quiz attempt not found.",
                "status_code": 404
            }

        rows = (
            db.query(
                RevisionQuizAnswer,
                Quiz,
                KnowledgeNode,
                Lesson,
                Course
            )
            .join(
                Quiz,
                RevisionQuizAnswer.quiz_id
                == Quiz.quiz_id
            )
            .join(
                KnowledgeNode,
                Quiz.knowledge_node_id
                == KnowledgeNode.node_id
            )
            .join(
                Lesson,
                Quiz.lesson_id
                == Lesson.lesson_id
            )
            .join(
                Course,
                Lesson.course_id
                == Course.course_id
            )
            .filter(
                RevisionQuizAnswer.attempt_id
                == attempt_id,
                Quiz.revision_quiz_id
                == attempt.revision_quiz_id,
                Quiz.quiz_type == "revision",
                Course.user_id == user_id
            )
            .order_by(
                RevisionQuizAnswer.answer_id
            )
            .all()
        )

        if not rows:
            return {
                "message": "Revision quiz attempt details not found.",
                "status_code": 404
            }

        course = rows[0][4]

        results = []

        for answer, quiz, knowledge_node, lesson, course in rows:
            selected_answer = (
                answer.selected_answer.strip().upper()
            )

            correct_answer = (
                quiz.correct_answer.strip().upper()
            )

            correct = (
                selected_answer == correct_answer
            )

            results.append({
                "quiz_id": quiz.quiz_id,
                "question": quiz.question,
                "concept_name": (
                    knowledge_node.concept_name
                ),
                "selected_answer": selected_answer,
                "correct_answer": correct_answer,
                "correct": correct,
                "explanation": quiz.explanation
            })

        total_questions = len(results)

        correct_answers = sum(
            1
            for result in results
            if result["correct"]
        )

        score = (
            (correct_answers / total_questions) * 100
            if total_questions > 0
            else 0
        )

        return {
            "attempt_id": attempt.attempt_id,
            "revision_quiz_id": (
                attempt.revision_quiz_id
            ),
            "course_id": course.course_id,
            "course_title": course.title,
            "attempted_at": (
                attempt.attempted_at.isoformat()
                if attempt.attempted_at
                else None
            ),
            "total_questions": total_questions,
            "correct_answers": correct_answers,
            "incorrect_answers": (
                total_questions - correct_answers
            ),
            "score": round(score, 2),
            "results": results,
            "status_code": 200
        }

    except Exception as error:
        return {
            "message": (
                "Unable to load revision quiz attempt."
            ),
            "error": str(error),
            "status_code": 500
        }

    finally:
        db.close()

# ---------------------------------------------------------
# CODING CHALLENGE GENERATION
# ---------------------------------------------------------

def generate_coding_challenge(
    user_id,
    lesson_id
):
    db = SessionLocal()

    try:
        lesson = (
            db.query(Lesson)
            .join(
                Course,
                Lesson.course_id == Course.course_id
            )
            .filter(
                Lesson.lesson_id == lesson_id,
                Course.user_id == user_id
            )
            .first()
        )

        if lesson is None:
            return {
                "message": "Lesson not found.",
                "status_code": 404
            }

        course = (
            db.query(Course)
            .filter(
                Course.course_id == lesson.course_id
            )
            .first()
        )

        if course is None:
            return {
                "message": "Course not found.",
                "status_code": 404
            }

        if not is_programming_course(
            course.title,
            course.description
        ):
            return {
                "message": (
                    "Coding challenges are only available "
                    "for programming courses."
                ),
                "status_code": 400
            }

        ai_result = call_coding_challenge_ai_service(
            course_title=course.title,
            lesson_title=lesson.title,
            difficulty=course.difficulty
        )

        if (
            "status_code" in ai_result
            and ai_result["status_code"] != 200
        ):
            return ai_result

        challenge = CodingChallenge(
            lesson_id=lesson.lesson_id,
            title=ai_result["title"],
            description=ai_result["description"],
            difficulty=ai_result["difficulty"]
        )

        db.add(challenge)
        db.commit()
        db.refresh(challenge)

        return {
            "message": (
                "Coding challenge generated and "
                "saved successfully."
            ),
            "challenge_id": challenge.challenge_id,
            "lesson_id": challenge.lesson_id,
            "title": challenge.title,
            "description": challenge.description,
            "difficulty": challenge.difficulty,
            "status_code": 201
        }

    except Exception as error:
        db.rollback()

        return {
            "message": (
                "Coding challenge generation failed."
            ),
            "error": str(error),
            "status_code": 500
        }

    finally:
        db.close()


def call_coding_challenge_ai_service(
    course_title,
    lesson_title,
    difficulty
):
    payload = json.dumps(
        {
            "course_title": course_title,
            "lesson_title": lesson_title,
            "difficulty": difficulty
        }
    ).encode("utf-8")

    request = Request(
        AI_CHALLENGE_SERVICE_URL,
        data=payload,
        headers={
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:
        with urlopen(request, timeout=120) as response:
            return json.loads(
                response.read().decode("utf-8")
            )

    except HTTPError as error:
        try:
            error_body = error.read().decode("utf-8")
            error_data = json.loads(error_body)

            return {
                "message": error_data.get(
                    "message",
                    "AI Service returned an error."
                ),
                "status_code": 502
            }

        except Exception:
            return {
                "message": "AI Service returned an error.",
                "status_code": 502
            }

    except URLError:
        return {
            "message": "AI Service is unavailable.",
            "status_code": 503
        }

    except json.JSONDecodeError:
        return {
            "message": "AI Service returned invalid JSON.",
            "status_code": 502
        }


# ---------------------------------------------------------
# NORMAL QUIZ AI SERVICE
# ---------------------------------------------------------

def call_quiz_ai_service(
    lesson_id,
    lesson_title,
    number_of_questions,
    concepts
):
    payload = json.dumps(
        {
            "lesson_id": lesson_id,
            "lesson_title": lesson_title,
            "number_of_questions": number_of_questions,
            "concepts": concepts
        }
    ).encode("utf-8")

    request = Request(
        AI_QUIZ_SERVICE_URL,
        data=payload,
        headers={
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:
        with urlopen(request, timeout=120) as response:
            return json.loads(
                response.read().decode("utf-8")
            )

    except HTTPError as error:
        try:
            error_body = error.read().decode("utf-8")
            error_data = json.loads(error_body)

            return {
                "message": error_data.get(
                    "message",
                    "AI Service returned an error."
                ),
                "status_code": 502
            }

        except Exception:
            return {
                "message": "AI Service returned an error.",
                "status_code": 502
            }

    except URLError:
        return {
            "message": "AI Service is unavailable.",
            "status_code": 503
        }

    except json.JSONDecodeError:
        return {
            "message": "AI Service returned invalid JSON.",
            "status_code": 502
        }


# ---------------------------------------------------------
# REVISION QUIZ AI SERVICE
# ---------------------------------------------------------

def call_revision_quiz_ai_service(
    course_id,
    course_title,
    number_of_questions,
    concepts
):
    payload = json.dumps(
        {
            "course_id": course_id,
            "course_title": course_title,
            "number_of_questions": number_of_questions,
            "concepts": concepts
        }
    ).encode("utf-8")

    request = Request(
        AI_REVISION_QUIZ_SERVICE_URL,
        data=payload,
        headers={
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:
        with urlopen(request, timeout=120) as response:
            return json.loads(
                response.read().decode("utf-8")
            )

    except HTTPError as error:
        try:
            error_body = error.read().decode("utf-8")
            error_data = json.loads(error_body)

            return {
                "message": error_data.get(
                    "message",
                    "AI Service returned an error."
                ),
                "status_code": 502
            }

        except Exception:
            return {
                "message": "AI Service returned an error.",
                "status_code": 502
            }

    except URLError:
        return {
            "message": "AI Service is unavailable.",
            "status_code": 503
        }

    except json.JSONDecodeError:
        return {
            "message": (
                "AI Service returned invalid JSON."
            ),
            "status_code": 502
        }