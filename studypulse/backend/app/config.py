from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mongodb_url: str
    db_name: str = "studypulse"
    openai_api_key: str = ""
    gemini_api_key: str = ""
    frontend_url: str = "http://localhost:5173"
    jwt_secret: str
    jwt_expire_days: int = 7

    class Config:
        env_file = ".env"


settings = Settings()