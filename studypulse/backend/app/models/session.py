from pydantic import BaseModel


class StudySessionCreate(BaseModel):
    subject: str
    minutes: int
    notes: str = ""