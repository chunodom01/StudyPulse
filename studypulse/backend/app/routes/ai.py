from datetime import datetime, timedelta, timezone

from fastapi import APIRouter

from app.database import db
from app.services.ai import generate_tip

router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/tip")
async def study_tip():
    since = datetime.now(timezone.utc) - timedelta(days=7)
    sessions = [s async for s in db.sessions.find({"created_at": {"$gte": since}})]
    return {"tip": await generate_tip(sessions)}