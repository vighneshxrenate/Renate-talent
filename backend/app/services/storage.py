import asyncio
import logging
import re
import uuid
from datetime import datetime, timezone

from fastapi import HTTPException
from supabase import create_client, Client

from app.config import settings

logger = logging.getLogger(__name__)


class StorageService:
    def __init__(self):
        self._client: Client = None  # type: ignore

    @property
    def client(self) -> Client:
        if self._client is None:
            self._client = create_client(settings.supabase_url, settings.supabase_service_key)
        return self._client

    @property
    def bucket(self) -> str:
        return "resumes"

    def _build_path(self, college_slug: str, student_name: str) -> str:
        short_id = uuid.uuid4().hex[:8]
        safe_name = re.sub(r"[^a-zA-Z0-9]", "_", student_name)[:50].strip("_")
        if not safe_name:
            safe_name = "resume"
        month = datetime.now(timezone.utc).strftime("%Y-%m")
        return f"{college_slug}/{month}/{short_id}_{safe_name}_resume.pdf"

    async def upload_resume(
        self, file_bytes: bytes, college_slug: str, student_name: str
    ) -> str:
        path = self._build_path(college_slug, student_name)
        try:
            await asyncio.wait_for(
                asyncio.to_thread(
                    self.client.storage.from_(self.bucket).upload,
                    path,
                    file_bytes,
                    {"content-type": "application/pdf"},
                ),
                timeout=30,
            )
            logger.info("Uploaded resume: %s (%d bytes)", path, len(file_bytes))
            return path
        except asyncio.TimeoutError:
            logger.error("Upload timed out for %s", path)
            raise HTTPException(504, "Resume upload timed out, please try again")
        except Exception as e:
            logger.error("Upload failed for %s: %s", path, e)
            raise HTTPException(503, "Storage service unavailable, please try again")

    async def delete_resume(self, path: str) -> None:
        try:
            await asyncio.wait_for(
                asyncio.to_thread(
                    self.client.storage.from_(self.bucket).remove, [path]
                ),
                timeout=10,
            )
            logger.info("Deleted resume: %s", path)
        except Exception as e:
            logger.error("Failed to delete %s (orphaned): %s", path, e)


storage_service = StorageService()
