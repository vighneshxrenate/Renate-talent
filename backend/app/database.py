import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

logger = logging.getLogger(__name__)

engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_size=5,       # per worker; 5 × 4 workers = 20 base connections
    max_overflow=5,    # per worker; 5 × 4 workers = 20 overflow → 40 total max
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_timeout=30,
)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
