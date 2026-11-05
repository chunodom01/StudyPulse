import asyncio
import uuid

from google.genai import types
from pydantic import BaseModel

from app.services.ai import MODELS, client


class QuizQuestion(BaseModel):
    question: str
    options: list[str]
    answer_index: int
    explanation: str


class Quiz(BaseModel):
    questions: list[QuizQuestion]


async def generate_quiz(
    grade: int, subject: str, count: int, lang: str, topic: str = ""
) -> list[dict]:
    if client is None:
        return []

    level = "lower secondary" if grade <= 9 else "upper secondary"
    language_line = (
        "Write everything (questions, options, explanations) in Khmer (ភាសាខ្មែរ). "
        "Keep numbers, formulas and chemical symbols in their normal form."
        if lang == "km"
        else "Write everything in clear, simple English."
    )
    topic_line = f"Focus on this topic or lesson: {topic}.\n" if topic else ""

    prompt = (
        "You are an experienced teacher in Cambodia. Write a practice quiz for a student "
        "following the Cambodian national curriculum (Ministry of Education, Youth and Sport).\n"
        f"Grade: {grade} ({level}). Subject: {subject}.\n"
        f"{topic_line}"
        f"Write exactly {count} multiple-choice questions at the right difficulty for "
        f"Grade {grade}, mixing easy and medium, covering different parts of the syllabus.\n"
        "Rules: exactly 4 options per question; exactly one correct option; "
        "answer_index is the 0-based position of the correct option; "
        "do not put letters like A) or B) in the options; "
        "the explanation is 1-2 short sentences; "
        "double-check that the marked answer is really correct.\n"
        f"{language_line}\n"
        f"Variation code (use it to make a different set each time): {uuid.uuid4().hex[:8]}"
    )

    for model in MODELS:
        try:
            response = await asyncio.wait_for(
                client.aio.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=1.0,
                        response_mime_type="application/json",
                        response_schema=Quiz,
                    ),
                ),
                timeout=30,
            )
            quiz = Quiz.model_validate_json(response.text or "")
            valid = [
                q.model_dump()
                for q in quiz.questions
                if len(q.options) == 4 and 0 <= q.answer_index < 4
            ]
            if valid:
                return valid[:count]
            print(f"Quiz had no valid questions ({model})")
        except Exception as e:
            print(f"Quiz error ({model}):", repr(e))

    return []