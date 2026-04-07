# ---------- builder ----------
FROM python:3.12-slim AS builder

WORKDIR /build
COPY pyproject.toml .
RUN pip install --no-cache-dir --prefix=/install .

# ---------- runtime ----------
FROM python:3.12-slim

RUN groupadd -r app && useradd -r -g app -d /app app

COPY --from=builder /install /usr/local
WORKDIR /app
COPY . .

RUN chown -R app:app /app
USER app

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')" || exit 1

# 4 workers: suitable for 2-4 CPU cores. Tune via WEB_CONCURRENCY env var.
CMD ["gunicorn", "app.main:app", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "-b", "0.0.0.0:8000", \
     "-w", "4", \
     "--timeout", "120", \
     "--graceful-timeout", "30", \
     "--access-logfile", "-"]
