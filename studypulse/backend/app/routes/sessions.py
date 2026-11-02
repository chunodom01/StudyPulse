from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, HTTPException

from app.database import db
from app.models.session import StudySessionCreate

router = APIRouter(prefix="/sessions", tags=["sessions"])


def to_object_id(session_id: str) -> ObjectId:
    try:
        return ObjectId(session_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid session id")


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
        created = s.get("created_at")
        s["created_at"] = created.isoformat() + "Z" if created else None
        sessions.append(s)
    return sessions


@router.put("/{session_id}")
async def update_session(session_id: str, data: StudySessionCreate):
    result = await db.sessions.update_one(
        {"_id": to_object_id(session_id)},
        {"$set": data.model_dump()},
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"updated": True}


@router.delete("/{session_id}")
async def delete_session(session_id: str):
    result = await db.sessions.delete_one({"_id": to_object_id(session_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"deleted": True}