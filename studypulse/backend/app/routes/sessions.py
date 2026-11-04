from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends, HTTPException

from app.database import db
from app.models.session import StudySessionCreate
from app.security import get_current_user

router = APIRouter(prefix="/sessions", tags=["sessions"])


def to_object_id(session_id: str) -> ObjectId:
    try:
        return ObjectId(session_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid session id")


@router.post("/")
async def create_session(data: StudySessionCreate, user: dict = Depends(get_current_user)):
    doc = data.model_dump()
    doc["created_at"] = datetime.now(timezone.utc)
    doc["user_id"] = user["id"]
    result = await db.sessions.insert_one(doc)
    return {"id": str(result.inserted_id)}


@router.get("/")
async def list_sessions(user: dict = Depends(get_current_user)):
    sessions = []
    async for s in db.sessions.find({"user_id": user["id"]}).sort("created_at", -1):
        s["id"] = str(s.pop("_id"))
        s.pop("user_id", None)
        created = s.get("created_at")
        s["created_at"] = created.isoformat() + "Z" if created else None
        sessions.append(s)
    return sessions


@router.put("/{session_id}")
async def update_session(
    session_id: str, data: StudySessionCreate, user: dict = Depends(get_current_user)
):
    result = await db.sessions.update_one(
        {"_id": to_object_id(session_id), "user_id": user["id"]},
        {"$set": data.model_dump()},
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"updated": True}


@router.delete("/{session_id}")
async def delete_session(session_id: str, user: dict = Depends(get_current_user)):
    result = await db.sessions.delete_one(
        {"_id": to_object_id(session_id), "user_id": user["id"]}
    )
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"deleted": True}