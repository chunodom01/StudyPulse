from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import sessions
from app.routes import sessions, ai
app = FastAPI(title="StudyPulse API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sessions.router)
app.include_router(ai.router)

@app.get("/")
def health():
    return {"status": "StudyPulse API is running"}