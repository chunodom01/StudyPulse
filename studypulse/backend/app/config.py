from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mongodb_url: str
    db_name: str = "studypulse"
    openai_api_key: str = ""
    gemini_api_key: str = ""

    class Config:
        env_file = ".env"


settings = Settings()