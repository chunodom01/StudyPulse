from fastapi import APIRouter
from app.database import db
from app.services.ai import generate_tip

router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/tip")
async def study_tip():
    sessions = [s async for s in db.sessions.find()]
    return {"tip": await generate_tip(sessions)}