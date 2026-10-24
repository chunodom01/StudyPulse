from datetime import datetime, timezone
from fastapi import APIRouter
from app.database import db
from app.models.session import StudySessionCreate

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("/")
async def create_session(data: StudySessionCreate):
    doc = data.model_dump()
    doc["created_at"] = datetime.now(timezone.utc)
    result = await db.sessions.insert_one(doc)
    return {"id": str(result.inserted_id)}


@router.get("/")
async def list_sessions():
    sessions = []
    async for s in db.sessions.find().sort("created_at", -1):
        s["id"] = str(s.pop("_id"))
        sessions.append(s)
    return sessions