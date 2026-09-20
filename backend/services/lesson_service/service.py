import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from dotenv import load_dotenv

from shared.database.database import SessionLocal
from shared.models.course import Course
from shared.models.lesson import Lesson
from shared.models.lesson_video import LessonVideo
from shared.models.quiz import Quiz
from shared.models.quiz import Quiz
from shared.models.coding_challenge import CodingChallenge

load_dotenv()

AI_SERVICE_URL = "http://127.0.0.1:5003/api/ai/lesson"
AI_QUIZ_SERVICE_URL = "http://127.0.0.1:5003/api/ai/quiz"
AI_CHALLENGE_SERVICE_URL = "http://127.0.0.1:5003/api/ai/challenge"

YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3/search"
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

def generate_lesson(user_id, course_id, title, sequence_number):
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

        if "status_code" in ai_result and ai_result["status_code"] != 200:
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

        youtube_videos = search_youtube_videos(lesson.title)

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
            "message": "Lesson generated and saved successfully.",
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


def call_ai_service(course_id, title, sequence_number):
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

    params = urlencode(
        {
            "part": "snippet",
            "q": lesson_title,
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

        videos = []

        for item in data.get("items", []):
            video_id = item.get("id", {}).get("videoId")
            snippet = item.get("snippet", {})

            if not video_id:
                continue

            videos.append(
                {
                    "title": snippet.get("title", ""),
                    "youtube_url": (
                        f"https://www.youtube.com/watch?v={video_id}"
                    )
                }
            )

        return videos

    except (HTTPError, URLError, json.JSONDecodeError):
        return []


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
            .filter(Lesson.lesson_id == lesson_id)
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
            .filter(LessonVideo.lesson_id == lesson_id)
            .all()
        )

        return [
            {
                "video_id": video.video_id,
                "lesson_id": video.lesson_id,
                "title": video.title,
                "youtube_url": video.youtube_url
            }
            for video in videos
        ]

    finally:
        db.close()


# ---------------------------------------------------------
# QUIZ GENERATION
# ---------------------------------------------------------

def generate_quiz(user_id, lesson_id, number_of_questions):
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

        ai_result = call_quiz_ai_service(
            lesson_id=lesson.lesson_id,
            lesson_title=lesson.title,
            number_of_questions=number_of_questions
        )

        if "status_code" in ai_result and ai_result["status_code"] != 200:
            return ai_result

        questions = ai_result.get("questions")

        if not isinstance(questions, list):
            return {
                "message": "AI Service returned invalid quiz data.",
                "status_code": 502
            }

        saved_quizzes = []

        for question_data in questions:
            quiz = Quiz(
                lesson_id=lesson.lesson_id,
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
            "message": "Quiz generated and saved successfully.",
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
                    "explanation": quiz.explanation
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


# ---------------------------------------------------------
# CODING CHALLENGE GENERATION
# ---------------------------------------------------------

def generate_coding_challenge(user_id, lesson_id):
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
            .filter(Course.course_id == lesson.course_id)
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

        if "status_code" in ai_result and ai_result["status_code"] != 200:
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
                "Coding challenge generated and saved successfully."
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
            "message": "Coding challenge generation failed.",
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


def call_quiz_ai_service(
    lesson_id,
    lesson_title,
    number_of_questions
):
    payload = json.dumps(
        {
            "lesson_id": lesson_id,
            "lesson_title": lesson_title,
            "number_of_questions": number_of_questions
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