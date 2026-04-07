"""Local filesystem storage service — replaces Supabase."""

import asyncio
import logging
import os
import re
import uuid
from datetime import datetime, timezone

from fastapi import HTTPException

from app.config import settings

logger = logging.getLogger(__name__)


class StorageService:
    def _build_path(self, college_slug: str, student_name: str) -> str:
        short_id = uuid.uuid4().hex[:8]
        safe_name = re.sub(r"[^a-zA-Z0-9]", "_", student_name)[:50].strip("_")
        if not safe_name:
            safe_name = "resume"
        month = datetime.now(timezone.utc).strftime("%Y-%m")
        rel_path = f"{college_slug}/{month}/{short_id}_{safe_name}_resume.pdf"
        return rel_path

    def _abs(self, rel_path: str) -> str:
        return os.path.join(settings.upload_dir, rel_path)

    async def upload_resume(
        self, file_bytes: bytes, college_slug: str, student_name: str
    ) -> str:
        rel_path = self._build_path(college_slug, student_name)
        abs_path = self._abs(rel_path)

        def _write() -> None:
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
            with open(abs_path, "wb") as f:
                f.write(file_bytes)

        try:
            await asyncio.wait_for(asyncio.to_thread(_write), timeout=10)
            logger.info("Saved resume: %s (%d bytes)", rel_path, len(file_bytes))
            return rel_path
        except asyncio.TimeoutError:
            logger.error("Write timed out for %s", rel_path)
            raise HTTPException(504, "Resume upload timed out, please try again")
        except OSError as e:
            logger.error("Failed to write %s: %s", rel_path, e)
            raise HTTPException(503, "Storage unavailable, please try again")

    async def delete_resume(self, rel_path: str) -> None:
        abs_path = self._abs(rel_path)

        def _delete() -> None:
            try:
                os.remove(abs_path)
            except FileNotFoundError:
                pass

        try:
            await asyncio.to_thread(_delete)
            logger.info("Deleted resume: %s", rel_path)
        except Exception as e:
            logger.error("Failed to delete %s (orphaned): %s", rel_path, e)


storage_service = StorageService()
