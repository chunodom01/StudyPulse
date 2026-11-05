from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.security import get_current_user
from app.services.quiz import generate_quiz

router = APIRouter(prefix="/quiz", tags=["quiz"])

SUBJECTS = {
    "Mathematics",
    "Physics",
    "Chemistry",
    "Biology",
    "Earth Science",
    "Khmer Language",
    "History",
    "Geography",
    "Moral & Civics",
    "English",
    "ICT",
}


@router.get("/")
async def get_quiz(
    grade: Annotated[int, Query(ge=7, le=12)],
    subject: str,
    count: Annotated[int, Query(ge=1, le=10)] = 5,
    lang: str = "en",
    topic: Annotated[str, Query(max_length=100)] = "",
    user: dict = Depends(get_current_user),
):
    if subject not in SUBJECTS:
        raise HTTPException(status_code=400, detail="Unknown subject")
    if lang not in ("en", "km"):
        lang = "en"

    questions = await generate_quiz(grade, subject, count, lang, topic.strip())
    if not questions:
        raise HTTPException(
            status_code=503, detail="The AI is busy right now. Please try again."
        )
    return {"grade": grade, "subject": subject, "questions": questions}