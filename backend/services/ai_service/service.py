import json
import os

from dotenv import load_dotenv
from google import genai

load_dotenv()


def build_course_prompt(topic, difficulty, duration):
    return f"""
You are an AI course-generation assistant.

Generate a structured educational course based on the following requirements:

Topic: {topic}
Difficulty: {difficulty}
Duration: {duration}

Return ONLY valid JSON.

The JSON must contain exactly these top-level fields:

{{
    "title": "string",
    "description": "string",
    "difficulty": "string",
    "duration": "string",
    "learning_outcomes": [
        "string"
    ],
    "lessons": [
        {{
            "title": "string",
            "content": "string",
            "summary": "string",
            "sequence_number": 1
        }}
    ]
}}

Requirements:

1. The course must be appropriate for the requested topic.
2. The difficulty must match the requested difficulty.
3. The duration must match the requested duration.
4. Learning outcomes must be clear and educational.
5. Generate lessons that cover the requested topic in a logical learning sequence.
6. Start with foundational concepts before advanced concepts.
7. Each lesson must have a unique sequence_number starting from 1.
8. Each lesson must contain meaningful educational content.
9. Each lesson must contain a concise summary of that lesson.
10. The lesson content should be suitable for the requested difficulty level.
11. Do not include fields outside the requested JSON structure.
12. Do not calculate or invent unrelated information.
13. Do not include markdown or code fences.
"""


def generate_course_with_ai(topic, difficulty, duration):
    ai_mode = os.getenv("AI_MODE", "development").lower()

    if ai_mode == "development":
        return generate_development_course(
            topic=topic,
            difficulty=difficulty,
            duration=duration,
        )

    if ai_mode != "gemini":
        return {
            "message": "Invalid AI_MODE configuration.",
            "status_code": 500,
        }

    return generate_gemini_course(
        topic=topic,
        difficulty=difficulty,
        duration=duration,
    )


def generate_development_course(topic, difficulty, duration):
    return {
        "title": f"{topic} Fundamentals",
        "description": (
            f"A structured {difficulty.lower()} course "
            f"covering the essential concepts of {topic}."
        ),
        "difficulty": difficulty,
        "duration": duration,
        "learning_outcomes": [
            f"Understand the fundamentals of {topic}.",
            f"Explain important concepts related to {topic}.",
            f"Apply {topic} concepts to practical problems.",
        ],
        "lessons": [
            {
                "title": f"Introduction to {topic}",
                "content": (
                    f"This lesson introduces the fundamental concepts "
                    f"of {topic}."
                ),
                "summary": (
                    f"An introduction to the basic concepts and purpose "
                    f"of {topic}."
                ),
                "sequence_number": 1,
            },
            {
                "title": f"Core Concepts of {topic}",
                "content": (
                    f"This lesson explains the important core concepts "
                    f"and principles of {topic}."
                ),
                "summary": (
                    f"A review of the major concepts and principles "
                    f"used in {topic}."
                ),
                "sequence_number": 2,
            },
            {
                "title": f"Practical Applications of {topic}",
                "content": (
                    f"This lesson explores practical applications of "
                    f"{topic} and how its concepts can be applied "
                    f"to real-world problems."
                ),
                "summary": (
                    f"An overview of practical applications of {topic}."
                ),
                "sequence_number": 3,
            },
        ],
    }


def generate_gemini_course(topic, difficulty, duration):
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return {
            "message": "GEMINI_API_KEY is not configured.",
            "status_code": 500,
        }

    try:
        client = genai.Client(api_key=api_key)

        prompt = build_course_prompt(
            topic=topic,
            difficulty=difficulty,
            duration=duration,
        )

        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt,
        )

        if not response.text:
            return {
                "message": "Gemini returned an empty response.",
                "status_code": 502,
            }

        course_data = json.loads(response.text)

        validation_error = validate_course_response(course_data)

        if validation_error:
            return {
                "message": validation_error,
                "status_code": 502,
            }

        return course_data

    except json.JSONDecodeError:
        return {
            "message": "Gemini returned an invalid JSON response.",
            "status_code": 502,
        }

    except Exception as error:
        return {
            "message": "Gemini course generation failed.",
            "error": str(error),
            "status_code": 502,
        }


def validate_course_response(course_data):
    if not isinstance(course_data, dict):
        return "AI response must be a JSON object."

    required_fields = [
        "title",
        "description",
        "difficulty",
        "duration",
        "learning_outcomes",
        "lessons",
    ]

    for field in required_fields:
        if field not in course_data:
            return f"AI response is missing required field: {field}."

    if not isinstance(course_data["learning_outcomes"], list):
        return "learning_outcomes must be a list."

    if not isinstance(course_data["lessons"], list):
        return "lessons must be a list."

    for lesson in course_data["lessons"]:
        if not isinstance(lesson, dict):
            return "Each lesson must be an object."

        required_lesson_fields = [
            "title",
            "content",
            "summary",
            "sequence_number",
        ]

        for field in required_lesson_fields:
            if field not in lesson:
                return f"Each lesson must contain {field}."

    return None


# ---------------------------------------------------------
# LESSON GENERATION
# ---------------------------------------------------------

def build_lesson_prompt(course_id, title, sequence_number):
    return f"""
You are an AI lesson-generation assistant.

Generate a detailed educational lesson for an existing course.

Course ID: {course_id}
Lesson Title: {title}
Lesson Sequence Number: {sequence_number}

Return ONLY valid JSON.

The JSON must contain exactly these fields:

{{
    "title": "string",
    "objectives": [
        "string"
    ],
    "explanation": "string",
    "real_world_examples": [
        "string"
    ],
    "summary": "string",
    "sequence_number": {sequence_number}
}}

Requirements:

1. The lesson must be directly related to the provided lesson title.
2. The lesson must be suitable for an educational course.
3. Provide clear and measurable learning objectives.
4. Provide a detailed but understandable explanation of the lesson topic.
5. Include relevant real-world examples.
6. Provide a concise summary of the lesson.
7. Preserve the provided sequence number.
8. Do not invent unrelated course information.
9. Do not include markdown or code fences.
10. Do not include fields outside the requested JSON structure.
"""


def generate_lesson_with_ai(course_id, title, sequence_number):
    ai_mode = os.getenv("AI_MODE", "development").lower()

    if ai_mode == "development":
        return generate_development_lesson(
            course_id=course_id,
            title=title,
            sequence_number=sequence_number,
        )

    if ai_mode != "gemini":
        return {
            "message": "Invalid AI_MODE configuration.",
            "status_code": 500,
        }

    return generate_gemini_lesson(
        course_id=course_id,
        title=title,
        sequence_number=sequence_number,
    )


def generate_development_lesson(course_id, title, sequence_number):
    return {
        "title": title,
        "objectives": [
            f"Understand the fundamental concepts of {title}.",
            f"Explain the important principles related to {title}.",
            f"Apply the concepts of {title} to practical situations.",
        ],
        "explanation": (
            f"This lesson provides a structured explanation of {title}. "
            f"It introduces the key concepts, explains how they work, "
            f"and connects them with practical learning situations."
        ),
        "real_world_examples": [
            f"A practical example of {title} in an educational or professional context.",
            f"A real-world situation where the concepts of {title} can be applied.",
        ],
        "summary": (
            f"This lesson covered the key concepts, principles, "
            f"and practical applications of {title}."
        ),
        "sequence_number": sequence_number,
    }


def generate_gemini_lesson(course_id, title, sequence_number):
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return {
            "message": "GEMINI_API_KEY is not configured.",
            "status_code": 500,
        }

    try:
        client = genai.Client(api_key=api_key)

        prompt = build_lesson_prompt(
            course_id=course_id,
            title=title,
            sequence_number=sequence_number,
        )

        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt,
        )

        if not response.text:
            return {
                "message": "Gemini returned an empty response.",
                "status_code": 502,
            }

        lesson_data = json.loads(response.text)

        validation_error = validate_lesson_response(
            lesson_data,
            sequence_number,
        )

        if validation_error:
            return {
                "message": validation_error,
                "status_code": 502,
            }

        return lesson_data

    except json.JSONDecodeError:
        return {
            "message": "Gemini returned an invalid JSON response.",
            "status_code": 502,
        }

    except Exception as error:
        return {
            "message": "Gemini lesson generation failed.",
            "error": str(error),
            "status_code": 502,
        }


def validate_lesson_response(lesson_data, sequence_number):
    if not isinstance(lesson_data, dict):
        return "AI lesson response must be a JSON object."

    required_fields = [
        "title",
        "objectives",
        "explanation",
        "real_world_examples",
        "summary",
        "sequence_number",
    ]

    for field in required_fields:
        if field not in lesson_data:
            return f"AI lesson response is missing required field: {field}."

    if not isinstance(lesson_data["objectives"], list):
        return "objectives must be a list."

    if not isinstance(lesson_data["real_world_examples"], list):
        return "real_world_examples must be a list."

    if not isinstance(lesson_data["explanation"], str):
        return "explanation must be a string."

    if not isinstance(lesson_data["summary"], str):
        return "summary must be a string."

    if lesson_data["sequence_number"] != sequence_number:
        return "AI lesson response has an incorrect sequence number."

    return None


# ---------------------------------------------------------
# QUIZ GENERATION
# ---------------------------------------------------------

def build_quiz_prompt(
    lesson_id,
    lesson_title,
    number_of_questions,
    concepts,
):
    concept_information = []

    for concept in concepts:
        concept_information.append(
            {
                "concept_name": concept["concept_name"],
                "description": concept["description"],
            }
        )

    return f"""
You are an AI quiz-generation assistant.

Generate multiple-choice quiz questions for an educational lesson.

Lesson ID: {lesson_id}
Lesson Title: {lesson_title}
Number of Questions: {number_of_questions}

Concepts taught in this lesson:
{json.dumps(concept_information, indent=2)}

Return ONLY valid JSON.

The JSON must contain exactly these top-level fields:

{{
    "questions": [
        {{
            "question": "string",
            "option_a": "string",
            "option_b": "string",
            "option_c": "string",
            "option_d": "string",
            "correct_answer": "A",
            "explanation": "string",
            "concept_name": "string"
        }}
    ]
}}

Requirements:

1. Generate exactly {number_of_questions} questions.
2. Every question must be directly related to the lesson.
3. Every question must test one of the provided concepts.
4. Each question must be associated with exactly one concept.
5. The concept_name must exactly match one of the provided concept names.
6. Multiple questions may test the same concept.
7. Questions should cover the provided concepts appropriately.
8. Questions must test understanding rather than unrelated knowledge.
9. Each question must have exactly four options.
10. The options must be represented using option_a, option_b, option_c, and option_d.
11. The correct_answer must contain only one of: A, B, C, or D.
12. The correct answer must actually match one of the four options.
13. Provide a clear explanation for why the correct answer is correct.
14. Avoid ambiguous questions.
15. Avoid duplicate questions.
16. Use a difficulty appropriate for an educational learner.
17. Do not include markdown or code fences.
18. Do not include fields outside the requested JSON structure.
19. Do not calculate or invent unrelated information.
"""


def generate_quiz_with_ai(
    lesson_id,
    lesson_title,
    number_of_questions,
    concepts,
):
    ai_mode = os.getenv("AI_MODE", "development").lower()

    if ai_mode == "development":
        return generate_development_quiz(
            lesson_id=lesson_id,
            lesson_title=lesson_title,
            number_of_questions=number_of_questions,
            concepts=concepts,
        )

    if ai_mode != "gemini":
        return {
            "message": "Invalid AI_MODE configuration.",
            "status_code": 500,
        }

    return generate_gemini_quiz(
        lesson_id=lesson_id,
        lesson_title=lesson_title,
        number_of_questions=number_of_questions,
        concepts=concepts,
    )


def generate_development_quiz(
    lesson_id,
    lesson_title,
    number_of_questions,
    concepts,
):
    if not concepts:
        return {
            "message": "No concepts found for this lesson.",
            "status_code": 400,
        }

    questions = []

    for question_number in range(number_of_questions):
        concept = concepts[
            question_number % len(concepts)
        ]

        concept_name = concept["concept_name"]

        questions.append(
            {
                "question": (
                    f"Which statement best describes "
                    f"{concept_name}?"
                ),
                "option_a": (
                    f"It is a concept related to "
                    f"{concept_name}."
                ),
                "option_b": (
                    "It is completely unrelated to the lesson."
                ),
                "option_c": (
                    "It is only used for entertainment."
                ),
                "option_d": (
                    "It does not have any practical application."
                ),
                "correct_answer": "A",
                "explanation": (
                    f"The correct answer is A because "
                    f"{concept_name} is a concept taught "
                    f"in this lesson."
                ),
                "concept_name": concept_name,
            }
        )

    validation_error = validate_quiz_response(
        {
            "questions": questions
        },
        number_of_questions,
        concepts,
    )

    if validation_error:
        return {
            "message": validation_error,
            "status_code": 502,
        }

    return {
        "questions": questions
    }


def generate_gemini_quiz(
    lesson_id,
    lesson_title,
    number_of_questions,
    concepts,
):
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return {
            "message": "GEMINI_API_KEY is not configured.",
            "status_code": 500,
        }

    try:
        client = genai.Client(api_key=api_key)

        prompt = build_quiz_prompt(
            lesson_id=lesson_id,
            lesson_title=lesson_title,
            number_of_questions=number_of_questions,
            concepts=concepts,
        )

        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt,
        )

        if not response.text:
            return {
                "message": "Gemini returned an empty response.",
                "status_code": 502,
            }

        quiz_data = json.loads(response.text)

        validation_error = validate_quiz_response(
            quiz_data,
            number_of_questions,
            concepts,
        )

        if validation_error:
            return {
                "message": validation_error,
                "status_code": 502,
            }

        return quiz_data

    except json.JSONDecodeError:
        return {
            "message": "Gemini returned an invalid JSON response.",
            "status_code": 502,
        }

    except Exception as error:
        return {
            "message": "Gemini quiz generation failed.",
            "error": str(error),
            "status_code": 502,
        }


def validate_quiz_response(
    quiz_data,
    number_of_questions,
    concepts,
):
    if not isinstance(quiz_data, dict):
        return "AI quiz response must be a JSON object."

    if "questions" not in quiz_data:
        return "AI quiz response is missing required field: questions."

    questions = quiz_data["questions"]

    if not isinstance(questions, list):
        return "questions must be a list."

    if len(questions) != number_of_questions:
        return (
            f"AI quiz response must contain exactly "
            f"{number_of_questions} questions."
        )

    if not isinstance(concepts, list) or not concepts:
        return "Quiz concepts must be a non-empty list."

    valid_concepts = {
        concept["concept_name"].strip().lower()
        for concept in concepts
        if isinstance(concept, dict)
        and isinstance(concept.get("concept_name"), str)
    }

    required_fields = [
        "question",
        "option_a",
        "option_b",
        "option_c",
        "option_d",
        "correct_answer",
        "explanation",
        "concept_name",
    ]

    valid_answers = {"A", "B", "C", "D"}

    for question in questions:
        if not isinstance(question, dict):
            return "Each quiz question must be an object."

        for field in required_fields:
            if field not in question:
                return (
                    f"Each quiz question must contain {field}."
                )

        for field in [
            "question",
            "option_a",
            "option_b",
            "option_c",
            "option_d",
            "correct_answer",
            "explanation",
            "concept_name",
        ]:
            if not isinstance(question[field], str):
                return f"{field} must be a string."

        if question["correct_answer"] not in valid_answers:
            return (
                "correct_answer must be one of: A, B, C, or D."
            )

        normalized_concept_name = (
            question["concept_name"].strip().lower()
        )

        if normalized_concept_name not in valid_concepts:
            return (
                "Quiz question references a concept "
                "that does not belong to the lesson."
            )

    return None

# ---------------------------------------------------------
# CODING CHALLENGE GENERATION
# ---------------------------------------------------------

def build_coding_challenge_prompt(
    course_title,
    lesson_title,
    difficulty,
):
    return f"""
You are an AI coding-challenge generation assistant.

Generate one programming coding challenge for an educational lesson.

Course Title: {course_title}
Lesson Title: {lesson_title}
Difficulty: {difficulty}

Return ONLY valid JSON.

The JSON must contain exactly these fields:

{{
    "title": "string",
    "description": "string",
    "difficulty": "string"
}}

Requirements:

1. Generate a coding challenge directly related to the lesson.
2. The challenge must require the learner to write or modify code.
3. The challenge must be appropriate for the provided course and lesson.
4. The challenge difficulty must match the provided difficulty.
5. The description must clearly explain what the learner needs to implement.
6. Do not provide the complete solution.
7. Do not include fields outside the requested JSON structure.
8. Do not include markdown or code fences.
9. Do not invent unrelated course information.
"""


def generate_coding_challenge_with_ai(
    course_title,
    lesson_title,
    difficulty,
):
    ai_mode = os.getenv("AI_MODE", "development").lower()

    if ai_mode == "development":
        return generate_development_coding_challenge(
            course_title=course_title,
            lesson_title=lesson_title,
            difficulty=difficulty,
        )

    if ai_mode != "gemini":
        return {
            "message": "Invalid AI_MODE configuration.",
            "status_code": 500,
        }

    return generate_gemini_coding_challenge(
        course_title=course_title,
        lesson_title=lesson_title,
        difficulty=difficulty,
    )


def generate_development_coding_challenge(
    course_title,
    lesson_title,
    difficulty,
):
    return {
        "title": f"{lesson_title} Coding Challenge",
        "description": (
            f"Create a programming solution that demonstrates "
            f"the concepts covered in {lesson_title}."
        ),
        "difficulty": difficulty,
    }


def generate_gemini_coding_challenge(
    course_title,
    lesson_title,
    difficulty,
):
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return {
            "message": "GEMINI_API_KEY is not configured.",
            "status_code": 500,
        }

    try:
        client = genai.Client(api_key=api_key)

        prompt = build_coding_challenge_prompt(
            course_title=course_title,
            lesson_title=lesson_title,
            difficulty=difficulty,
        )

        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt,
        )

        if not response.text:
            return {
                "message": "Gemini returned an empty response.",
                "status_code": 502,
            }

        challenge_data = json.loads(response.text)

        validation_error = validate_coding_challenge_response(
            challenge_data
        )

        if validation_error:
            return {
                "message": validation_error,
                "status_code": 502,
            }

        return challenge_data

    except json.JSONDecodeError:
        return {
            "message": "Gemini returned an invalid JSON response.",
            "status_code": 502,
        }

    except Exception as error:
        return {
            "message": "Gemini coding challenge generation failed.",
            "error": str(error),
            "status_code": 502,
        }


def validate_coding_challenge_response(challenge_data):
    if not isinstance(challenge_data, dict):
        return "AI coding challenge response must be a JSON object."

    required_fields = [
        "title",
        "description",
        "difficulty",
    ]

    for field in required_fields:
        if field not in challenge_data:
            return (
                f"AI coding challenge response is missing "
                f"required field: {field}."
            )

    for field in required_fields:
        if not isinstance(challenge_data[field], str):
            return f"{field} must be a string."

    return None

# ============================================================
# AKDG - Adaptive Knowledge Dependency Graph
# ============================================================

ALLOWED_KNOWLEDGE_RELATIONSHIPS = {
    "prerequisite",
    "builds_on",
    "related_to",
}


def build_knowledge_graph_prompt(
    course_title,
    course_description,
    lessons,
):
    lesson_information = []

    for lesson in lessons:
        lesson_information.append(
            {
                "sequence_number": lesson["sequence_number"],
                "title": lesson["title"],
                "content": lesson["content"],
                "summary": lesson["summary"],
            }
        )

    return f"""
You are generating a Knowledge Dependency Graph for a single course.

Course title:
{course_title}

Course description:
{course_description}

Lessons:
{json.dumps(lesson_information, indent=2)}

Your task is to identify the meaningful concepts taught in this course
and the relationships between those concepts.

Return ONLY valid JSON.

The JSON must have exactly this structure:

{{
  "nodes": [
    {{
      "concept_name": "string",
      "description": "string",
      "lesson_sequence_number": 1
    }}
  ],
  "relationships": [
    {{
      "source_concept": "string",
      "target_concept": "string",
      "relationship_type": "prerequisite"
    }}
  ]
}}

Rules:

1. Each node represents a meaningful concept taught in the course.
2. A lesson may contain multiple concepts.
3. Every node must reference the lesson where that concept is taught
   using lesson_sequence_number.
4. lesson_sequence_number must exactly match one of the provided lesson
   sequence numbers.
5. Do not create concepts that are unrelated to the provided course content.
6. Do not create database IDs.
7. relationship_type must be exactly one of:
   - prerequisite
   - builds_on
   - related_to
8. "prerequisite" means the source concept is required before the target
   concept can be properly understood.
9. "builds_on" means the target concept extends or develops the source
   concept.
10. "related_to" means the concepts are connected but neither is
    necessarily a prerequisite of the other.
11. Do not create self-relationships.
12. Do not assume that lesson order automatically means dependency.
13. Create relationships only when the course content supports them.
14. Do not add explanations outside the JSON.
15. Do not use Markdown code fences.
"""


def generate_knowledge_graph_with_ai(
    course_title,
    course_description,
    lessons,
):
    mode = os.getenv("AI_MODE", "development").lower()

    if mode == "gemini":
        return generate_gemini_knowledge_graph(
            course_title=course_title,
            course_description=course_description,
            lessons=lessons,
        )

    return generate_development_knowledge_graph(
        course_title=course_title,
        course_description=course_description,
        lessons=lessons,
    )


def generate_development_knowledge_graph(
    course_title,
    course_description,
    lessons,
):
    nodes = []

    for lesson in lessons:
        nodes.append(
            {
                "concept_name": lesson["title"],
                "description": lesson["summary"],
                "lesson_sequence_number": lesson["sequence_number"],
            }
        )

    relationships = []

    for index in range(1, len(nodes)):
        previous_node = nodes[index - 1]
        current_node = nodes[index]

        relationships.append(
            {
                "source_concept": previous_node["concept_name"],
                "target_concept": current_node["concept_name"],
                "relationship_type": "builds_on",
            }
        )

    result = {
        "nodes": nodes,
        "relationships": relationships,
    }

    validation_result = validate_knowledge_graph_response(
        result=result,
        lessons=lessons,
    )

    if validation_result is not None:
        return validation_result

    return result


def generate_gemini_knowledge_graph(
    course_title,
    course_description,
    lessons,
):
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return {
            "message": "GEMINI_API_KEY is not configured.",
            "status_code": 500,
        }

    prompt = build_knowledge_graph_prompt(
        course_title=course_title,
        course_description=course_description,
        lessons=lessons,
    )

    try:
        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt,
        )

        response_text = response.text.strip()

        result = json.loads(response_text)

        validation_result = validate_knowledge_graph_response(
            result=result,
            lessons=lessons,
        )

        if validation_result is not None:
            return validation_result

        return result

    except json.JSONDecodeError:
        return {
            "message": "Gemini returned invalid JSON.",
            "status_code": 502,
        }

    except Exception as error:
        return {
            "message": "Knowledge graph generation failed.",
            "error": str(error),
            "status_code": 500,
        }


def validate_knowledge_graph_response(result, lessons):
    if not isinstance(result, dict):
        return {
            "message": "Knowledge graph response must be a JSON object.",
            "status_code": 502,
        }

    nodes = result.get("nodes")
    relationships = result.get("relationships")

    if not isinstance(nodes, list):
        return {
            "message": "Knowledge graph nodes must be a list.",
            "status_code": 502,
        }

    if not isinstance(relationships, list):
        return {
            "message": "Knowledge graph relationships must be a list.",
            "status_code": 502,
        }

    valid_sequences = {
        lesson["sequence_number"]
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
                "message": "Knowledge graph node is missing required fields.",
                "status_code": 502,
            }

        concept_name = node["concept_name"]
        description = node["description"]
        sequence_number = node["lesson_sequence_number"]

        if not isinstance(concept_name, str) or not concept_name.strip():
            return {
                "message": "Knowledge graph concept name must be a non-empty string.",
                "status_code": 502,
            }

        if not isinstance(description, str):
            return {
                "message": "Knowledge graph concept description must be a string.",
                "status_code": 502,
            }

        if not isinstance(sequence_number, int):
            return {
                "message": "Knowledge graph lesson sequence number must be an integer.",
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

        normalized_concept_name = concept_name.strip().lower()

        if normalized_concept_name in concept_names:
            return {
                "message": "Knowledge graph contains duplicate concepts.",
                "status_code": 502,
            }

        concept_names.add(normalized_concept_name)

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
                    "Knowledge graph relationship is "
                    "missing required fields."
                ),
                "status_code": 502,
            }

        source_concept = relationship["source_concept"]
        target_concept = relationship["target_concept"]
        relationship_type = relationship["relationship_type"]

        if not isinstance(source_concept, str) or not source_concept.strip():
            return {
                "message": "Source concept must be a non-empty string.",
                "status_code": 502,
            }

        if not isinstance(target_concept, str) or not target_concept.strip():
            return {
                "message": "Target concept must be a non-empty string.",
                "status_code": 502,
            }

        if source_concept.strip().lower() == target_concept.strip().lower():
            return {
                "message": "Knowledge graph cannot contain self-relationships.",
                "status_code": 502,
            }

        if relationship_type not in ALLOWED_KNOWLEDGE_RELATIONSHIPS:
            return {
                "message": (
                    "Knowledge graph contains an invalid "
                    "relationship type."
                ),
                "status_code": 502,
            }

        if source_concept.strip().lower() not in concept_names:
            return {
                "message": (
                    "Knowledge graph relationship references "
                    "an unknown source concept."
                ),
                "status_code": 502,
            }

        if target_concept.strip().lower() not in concept_names:
            return {
                "message": (
                    "Knowledge graph relationship references "
                    "an unknown target concept."
                ),
                "status_code": 502,
            }

    return None