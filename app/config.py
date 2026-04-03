from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_name: str = "Jarvis Local Assistant"
    workspace_dir: Path = BASE_DIR
    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1-mini"
    command_timeout_seconds: int = 20

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def static_dir(self) -> Path:
        return self.workspace_dir / "static"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
