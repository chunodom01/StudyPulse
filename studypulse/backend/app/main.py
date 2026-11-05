from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes import ai, auth, sessions
from app.routes import ai, auth, quiz, sessions
app = FastAPI(title="StudyPulse API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", settings.frontend_url],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(sessions.router)
app.include_router(ai.router)
app.include_router(quiz.router)


@app.get("/")
def health():
    return {"status": "StudyPulse API is running"}