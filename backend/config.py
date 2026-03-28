from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Face Attendance API"
    app_env: str = "development"
    api_prefix: str = "/api"
    database_url: str = Field(default=f"sqlite+aiosqlite:///{(ROOT_DIR / 'attendance.db').as_posix()}")
    model_path: str = Field(default=str(ROOT_DIR / "shape_predictor_68_face_landmarks.dat"))
    dataset_path: str = Field(default=str(ROOT_DIR / "dataset"))
    log_level: str = "INFO"
    face_match_tolerance: float = 0.5
    blink_ear_threshold: float = 0.22
    blink_consecutive_frames: int = 2
    cors_origins: list[str] = ["http://localhost:3000"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
