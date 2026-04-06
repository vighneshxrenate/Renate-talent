import time
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.college import College
from app.schemas.college import CollegeOut

router = APIRouter(tags=["colleges"])

_cache: List[CollegeOut] = []
_cache_time: float = 0
_CACHE_TTL = 3600  # 1 hour


@router.get("/colleges", response_model=List[CollegeOut])
async def list_colleges(db: AsyncSession = Depends(get_db)):
    global _cache, _cache_time
    if _cache and (time.time() - _cache_time) < _CACHE_TTL:
        return _cache
    result = await db.execute(select(College).order_by(College.name))
    _cache = [CollegeOut.model_validate(c) for c in result.scalars().all()]
    _cache_time = time.time()
    return _cache
