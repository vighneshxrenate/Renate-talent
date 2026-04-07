import time
from typing import List

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.industry import Industry
from app.schemas.industry import IndustryOut

router = APIRouter(tags=["industries"])

_cache: List[IndustryOut] = []
_cache_time: float = 0
_CACHE_TTL = 3600  # 1 hour


@router.get("/industries", response_model=List[IndustryOut])
async def list_industries(db: AsyncSession = Depends(get_db)):
    global _cache, _cache_time
    if _cache and (time.time() - _cache_time) < _CACHE_TTL:
        data = [i.model_dump(mode="json") for i in _cache]
        response = JSONResponse(content=data)
        response.headers["Cache-Control"] = "public, max-age=3600, stale-while-revalidate=600"
        return response
    result = await db.execute(select(Industry).order_by(Industry.name))
    _cache = [IndustryOut.model_validate(i) for i in result.scalars().all()]
    _cache_time = time.time()
    data = [i.model_dump(mode="json") for i in _cache]
    response = JSONResponse(content=data)
    response.headers["Cache-Control"] = "public, max-age=3600, stale-while-revalidate=600"
    return response
