import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from shared.database.database import SessionLocal
from shared.models.course import Course
from shared.models.lesson import Lesson
from shared.models.knowledge_node import KnowledgeNode
from shared.models.knowledge_relationship import KnowledgeRelationship


AI_SERVICE_URL = "http://127.0.0.1:5003/api/ai/knowledge-graph"


ALLOWED_RELATIONSHIP_TYPES = {
    "prerequisite",
    "builds_on",
    "related_to",
}


def generate_and_save_knowledge_graph(course_id):
    db = SessionLocal()

    try:
        course = (
            db.query(Course)
            .filter(Course.course_id == course_id)
            .first()
        )

        if course is None:
            return {
                "message": "Course not found.",
                "status_code": 404,
            }

        lessons = (
            db.query(Lesson)
            .filter(Lesson.course_id == course_id)
            .order_by(Lesson.sequence_number)
            .all()
        )

        if not lessons:
            return {
                "message": "No lessons found for the course.",
                "status_code": 400,
            }

        lessons_data = [
            {
                "lesson_id": lesson.lesson_id,
                "title": lesson.title,
                "content": lesson.content,
                "summary": lesson.summary,
                "sequence_number": lesson.sequence_number,
            }
            for lesson in lessons
        ]

        ai_result = call_ai_service(
            course_title=course.title,
            course_description=course.description,
            lessons=lessons_data,
        )

        if "status_code" in ai_result and ai_result["status_code"] != 200:
            return ai_result

        validation_error = validate_ai_knowledge_graph(
            ai_result=ai_result,
            lessons=lessons,
        )

        if validation_error is not None:
            return validation_error

        nodes = ai_result["nodes"]
        relationships = ai_result["relationships"]

        lesson_by_sequence = {
            lesson.sequence_number: lesson
            for lesson in lessons
        }

        node_by_concept = {}

        for node_data in nodes:
            concept_name = node_data["concept_name"].strip()

            lesson = lesson_by_sequence[
                node_data["lesson_sequence_number"]
            ]

            node = KnowledgeNode(
                course_id=course_id,
                lesson_id=lesson.lesson_id,
                concept_name=concept_name,
                description=node_data["description"].strip(),
            )

            db.add(node)

            node_by_concept[
                normalize_concept_name(concept_name)
            ] = node

        db.flush()

        for relationship_data in relationships:
            source_concept = normalize_concept_name(
                relationship_data["source_concept"]
            )

            target_concept = normalize_concept_name(
                relationship_data["target_concept"]
            )

            source_node = node_by_concept[source_concept]
            target_node = node_by_concept[target_concept]

            relationship = KnowledgeRelationship(
                course_id=course_id,
                source_node_id=source_node.node_id,
                target_node_id=target_node.node_id,
                relationship_type=relationship_data[
                    "relationship_type"
                ],
            )

            db.add(relationship)

        db.commit()

        return {
            "message": "Knowledge graph generated and saved successfully.",
            "course_id": course_id,
            "node_count": len(nodes),
            "relationship_count": len(relationships),
            "status_code": 201,
        }

    except Exception as error:
        db.rollback()

        return {
            "message": "Knowledge graph generation failed.",
            "error": str(error),
            "status_code": 500,
        }

    finally:
        db.close()


def call_ai_service(
    course_title,
    course_description,
    lessons,
):
    payload = json.dumps(
        {
            "course_title": course_title,
            "course_description": course_description,
            "lessons": lessons,
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


def validate_ai_knowledge_graph(
    ai_result,
    lessons,
):
    if not isinstance(ai_result, dict):
        return {
            "message": "AI knowledge graph response must be an object.",
            "status_code": 502,
        }

    nodes = ai_result.get("nodes")
    relationships = ai_result.get("relationships")

    if not isinstance(nodes, list):
        return {
            "message": "AI knowledge graph nodes must be a list.",
            "status_code": 502,
        }

    if not isinstance(relationships, list):
        return {
            "message": (
                "AI knowledge graph relationships must be a list."
            ),
            "status_code": 502,
        }

    valid_sequences = {
        lesson.sequence_number
        for lesson in lessons
    }

    concept_names = set()

    for node in nodes:
        if not isinstance(node, dict):
            return {
                "message": "Each knowledge graph node must be an object.",
                "status_code": 502,
            }

        required_fields = {
            "concept_name",
            "description",
            "lesson_sequence_number",
        }

        if not required_fields.issubset(node.keys()):
            return {
                "message": (
                    "Knowledge graph node is missing "
                    "required fields."
                ),
                "status_code": 502,
            }

        concept_name = node["concept_name"]
        description = node["description"]
        sequence_number = node["lesson_sequence_number"]

        if not isinstance(concept_name, str) or not concept_name.strip():
            return {
                "message": (
                    "Knowledge graph concept name "
                    "must be a non-empty string."
                ),
                "status_code": 502,
            }

        if not isinstance(description, str):
            return {
                "message": (
                    "Knowledge graph concept description "
                    "must be a string."
                ),
                "status_code": 502,
            }

        if not isinstance(sequence_number, int):
            return {
                "message": (
                    "Knowledge graph lesson sequence number "
                    "must be an integer."
                ),
                "status_code": 502,
            }

        if sequence_number not in valid_sequences:
            return {
                "message": (
                    "Knowledge graph contains an invalid "
                    "lesson sequence number."
                ),
                "status_code": 502,
            }

        normalized_name = normalize_concept_name(
            concept_name
        )

        if normalized_name in concept_names:
            return {
                "message": (
                    "Knowledge graph contains duplicate concepts."
                ),
                "status_code": 502,
            }

        concept_names.add(normalized_name)

    for relationship in relationships:
        if not isinstance(relationship, dict):
            return {
                "message": (
                    "Each knowledge graph relationship "
                    "must be an object."
                ),
                "status_code": 502,
            }

        required_fields = {
            "source_concept",
            "target_concept",
            "relationship_type",
        }

        if not required_fields.issubset(relationship.keys()):
            return {
                "message": (
                    "Knowledge graph relationship "
                    "is missing required fields."
                ),
                "status_code": 502,
            }

        source_concept = relationship["source_concept"]
        target_concept = relationship["target_concept"]
        relationship_type = relationship["relationship_type"]

        if not isinstance(source_concept, str):
            return {
                "message": "Source concept must be a string.",
                "status_code": 502,
            }

        if not isinstance(target_concept, str):
            return {
                "message": "Target concept must be a string.",
                "status_code": 502,
            }

        if relationship_type not in ALLOWED_RELATIONSHIP_TYPES:
            return {
                "message": (
                    "Knowledge graph contains an invalid "
                    "relationship type."
                ),
                "status_code": 502,
            }

        normalized_source = normalize_concept_name(
            source_concept
        )

        normalized_target = normalize_concept_name(
            target_concept
        )

        if not normalized_source or not normalized_target:
            return {
                "message": (
                    "Relationship concepts cannot be empty."
                ),
                "status_code": 502,
            }

        if normalized_source == normalized_target:
            return {
                "message": (
                    "Knowledge graph cannot contain "
                    "self-relationships."
                ),
                "status_code": 502,
            }

        if normalized_source not in concept_names:
            return {
                "message": (
                    "Knowledge graph relationship references "
                    "an unknown source concept."
                ),
                "status_code": 502,
            }

        if normalized_target not in concept_names:
            return {
                "message": (
                    "Knowledge graph relationship references "
                    "an unknown target concept."
                ),
                "status_code": 502,
            }

    return None


def normalize_concept_name(concept_name):
    return " ".join(
        concept_name.strip().lower().split()
    )