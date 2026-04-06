import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pythonjsonlogger.json import JsonFormatter
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.config import settings

# Sentry — initialise early, only if DSN is configured
if settings.sentry_dsn:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        integrations=[FastApiIntegration(), SqlalchemyIntegration()],
        traces_sample_rate=0.1,
        send_default_pii=False,
    )

from app.database import engine
from app.middleware.request_id import RequestIdMiddleware
from app.middleware.security import SecurityHeadersMiddleware
from app.routers import colleges, health, industries, submissions

# Structured JSON logging
_handler = logging.StreamHandler(sys.stdout)
_handler.setFormatter(JsonFormatter(
    fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
    rename_fields={"asctime": "timestamp", "levelname": "level"},
))
logging.root.handlers = [_handler]
logging.root.setLevel(logging.INFO)
logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Renate Talent API")
    yield
    logger.info("Shutting down, disposing connection pool")
    await engine.dispose()


app = FastAPI(title="Renate Talent", version="0.1.0", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(RequestIdMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-API-Key"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error(
        "Unhandled error on %s %s: %s",
        request.method,
        request.url.path,
        exc,
        extra={"request_id": request_id},
    )
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


app.include_router(health.router, prefix="/api")
app.include_router(colleges.router, prefix="/api")
app.include_router(industries.router, prefix="/api")
app.include_router(submissions.router, prefix="/api")
