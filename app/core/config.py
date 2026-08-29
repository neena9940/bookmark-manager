from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./bookmarks.db"
    SECRET_KEY: str = "change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    # OPENAI_API_KEY: str
    REDIS_URL: str = "redis://localhost:6379"

    # ✅ NEW: S3 / MinIO Settings
    S3_ENDPOINT: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_BUCKET: str = "bookmarks"
    S3_REGION: str = "us-east-1"

    class Config:
        env_file = ".env"


settings = Settings()
