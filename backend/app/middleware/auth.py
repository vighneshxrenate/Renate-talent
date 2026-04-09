"""API key authentication for admin endpoints."""

import secrets

from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader

from app.config import settings

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def require_admin_key(
    api_key: str | None = Security(_api_key_header),
) -> str:
    """Dependency that enforces a valid admin API key."""
    if not settings.admin_api_key:
        raise HTTPException(503, "Admin access is not configured")
    if not api_key or not secrets.compare_digest(api_key, settings.admin_api_key):
        raise HTTPException(401, "Invalid or missing API key")
    return api_key
