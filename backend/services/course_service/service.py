import json
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from shared.database.database import SessionLocal
from shared.models.user import User
from shared.models.course import Course
from shared.models.lesson import Lesson


AI_SERVICE_URL = "http://127.0.0.1:5003/api/ai/course"


def create_course(user_id, topic, difficulty, duration):
    db = SessionLocal()

    try:
        ai_result = call_ai_service(
            topic=topic,
            difficulty=difficulty,
            duration=duration,
        )

        if "status_code" in ai_result and ai_result["status_code"] != 200:
            return ai_result

        duration_value = parse_duration(duration)

        if duration_value is None:
            return {
                "message": "Duration must contain a numeric number of weeks.",
                "status_code": 400,
            }

        course = Course(
            user_id=user_id,
            title=ai_result["title"],
            description=ai_result["description"],
            difficulty=ai_result["difficulty"],
            duration=duration_value,
            learning_outcomes=ai_result["learning_outcomes"],
        )

        db.add(course)
        db.flush()

        lessons = []

        for lesson_data in ai_result["lessons"]:
            lesson = Lesson(
                course_id=course.course_id,
                title=lesson_data["title"],
                content=lesson_data["content"],
                summary=lesson_data["summary"],
                sequence_number=lesson_data["sequence_number"],
            )

            db.add(lesson)
            lessons.append(lesson)

        db.commit()

        return {
            "message": "Course generated and saved successfully.",
            "course_id": course.course_id,
            "user_id": course.user_id,
            "title": course.title,
            "description": course.description,
            "difficulty": course.difficulty,
            "duration": f"{course.duration} weeks",
            "learning_outcomes": course.learning_outcomes,
            "lessons": [
                {
                    "lesson_id": lesson.lesson_id,
                    "title": lesson.title,
                    "content": lesson.content,
                    "summary": lesson.summary,
                    "sequence_number": lesson.sequence_number,
                }
                for lesson in lessons
            ],
            "status_code": 201,
        }

    except Exception as error:
        db.rollback()

        return {
            "message": "Course generation failed.",
            "error": str(error),
            "status_code": 500,
        }

    finally:
        db.close()


def call_ai_service(topic, difficulty, duration):
    payload = json.dumps(
        {
            "topic": topic,
            "difficulty": difficulty,
            "duration": duration,
        }
    ).encode("utf-8")

    request = Request(
        AI_SERVICE_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=120) as response:
            response_body = response.read().decode("utf-8")
            return json.loads(response_body)

    except HTTPError as error:
        try:
            error_body = error.read().decode("utf-8")
            error_data = json.loads(error_body)
            return {
                "message": error_data.get(
                    "message",
                    "AI Service returned an error.",
                ),
                "status_code": 502,
            }
        except Exception:
            return {
                "message": "AI Service returned an error.",
                "status_code": 502,
            }

    except URLError:
        return {
            "message": "AI Service is unavailable.",
            "status_code": 503,
        }

    except json.JSONDecodeError:
        return {
            "message": "AI Service returned invalid JSON.",
            "status_code": 502,
        }


def parse_duration(duration):
    if not isinstance(duration, str):
        return None

    match = re.search(r"\d+", duration)

    if not match:
        return None

    return int(match.group())


def get_course_by_id(course_id, user_id):
    db = SessionLocal()

    try:
        course = (
            db.query(Course)
            .filter(
                Course.course_id == course_id,
                Course.user_id == user_id,
            )
            .first()
        )

        if course is None:
            return None

        lessons = (
            db.query(Lesson)
            .filter(Lesson.course_id == course.course_id)
            .order_by(Lesson.sequence_number)
            .all()
        )

        return {
            "course_id": course.course_id,
            "user_id": course.user_id,
            "title": course.title,
            "description": course.description,
            "difficulty": course.difficulty,
            "duration": f"{course.duration} weeks",
            "learning_outcomes": course.learning_outcomes,
            "lessons": [
                {
                    "lesson_id": lesson.lesson_id,
                    "title": lesson.title,
                    "content": lesson.content,
                    "summary": lesson.summary,
                    "sequence_number": lesson.sequence_number,
                }
                for lesson in lessons
            ],
        }

    finally:
        db.close()


def get_all_courses(user_id):
    db = SessionLocal()

    try:
        courses = (
            db.query(Course)
            .filter(Course.user_id == user_id)
            .all()
        )

        return [
            {
                "course_id": course.course_id,
                "user_id": course.user_id,
                "title": course.title,
                "description": course.description,
                "difficulty": course.difficulty,
                "duration": f"{course.duration} weeks",
                "learning_outcomes": course.learning_outcomes,
            }
            for course in courses
        ]

    finally:
        db.close()