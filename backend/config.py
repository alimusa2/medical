import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent

IS_VERCEL = bool(os.getenv("VERCEL")) or bool(os.getenv("VERCEL_ENV")) or (os.name != "nt" and os.path.exists("/tmp"))
TMP_DIR = Path("/tmp") if IS_VERCEL else BASE_DIR

class Settings(BaseSettings):
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{TMP_DIR / 'medverify.db'}")
    UPLOAD_DIR: str = str(TMP_DIR / "uploads")
    REPORT_DIR: str = str(TMP_DIR / "reports")
    SAMPLE_DIR: str = str(TMP_DIR / "samples")

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

# Ensure directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.REPORT_DIR, exist_ok=True)
os.makedirs(settings.SAMPLE_DIR, exist_ok=True)

