from __future__ import annotations

from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    allowed_origins: str = "http://localhost:3000"
    max_upload_size_mb: int = 5
    upload_dir: str = "./uploads"
    admin_api_key: str = ""
    sentry_dsn: str = ""

    model_config = {"env_file": ".env"}

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024

    @property
    def cors_origins(self) -> List[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]


settings = Settings()
