from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str = ""
    openai_model: str = "gpt-3.5-turbo"
    database_path: str = "/app/data/cv_filtering.db"
    cache_ttl_hours: int = 168
    match_threshold: int = 70
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
