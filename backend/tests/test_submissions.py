"""Tests for the submissions endpoints."""

import io
import uuid

import pytest
from httpx import AsyncClient

VALID_PDF = b"%PDF-1.4 fake content for testing"
ADMIN_KEY = "test-admin-key"


def _form(seed: dict, **overrides) -> dict:
    """Build multipart form data for a submission."""
    data = {
        "student_name": "Jane Doe",
        "email": "jane@example.com",
        "phone": "+919876543210",
        "college_id": seed["college_id"],
        "industry_id": seed["industry_id"],
        **overrides,
    }
    return data


def _file(content: bytes = VALID_PDF, name: str = "resume.pdf", mime: str = "application/pdf"):
    return {"resume": (name, io.BytesIO(content), mime)}


# ---------------------------------------------------------------------------
# POST /api/submissions
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_create_submission_success(client: AsyncClient):
    seed = client._seed  # type: ignore[attr-defined]
    resp = await client.post(
        "/api/submissions",
        data=_form(seed),
        files=_file(),
    )
    assert resp.status_code == 201
    body = resp.json()
    assert "id" in body
    assert body["message"] == "Submission received successfully"


@pytest.mark.asyncio
async def test_create_submission_rejects_non_pdf(client: AsyncClient):
    seed = client._seed  # type: ignore[attr-defined]
    resp = await client.post(
        "/api/submissions",
        data=_form(seed),
        files={"resume": ("resume.txt", io.BytesIO(b"not a pdf"), "text/plain")},
    )
    assert resp.status_code == 400
    assert "PDF" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_create_submission_rejects_oversized_file(client: AsyncClient):
    seed = client._seed  # type: ignore[attr-defined]
    big = b"%PDF-" + b"x" * (6 * 1024 * 1024)  # >5 MB
    resp = await client.post(
        "/api/submissions",
        data=_form(seed),
        files=_file(content=big),
    )
    assert resp.status_code == 400
    assert "size" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_create_submission_rejects_fake_pdf(client: AsyncClient):
    seed = client._seed  # type: ignore[attr-defined]
    resp = await client.post(
        "/api/submissions",
        data=_form(seed),
        files=_file(content=b"not-pdf-magic-bytes", mime="application/pdf"),
    )
    assert resp.status_code == 400
    assert "valid PDF" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_create_submission_rejects_invalid_college(client: AsyncClient):
    seed = client._seed  # type: ignore[attr-defined]
    resp = await client.post(
        "/api/submissions",
        data=_form(seed, college_id=str(uuid.uuid4())),
        files=_file(),
    )
    assert resp.status_code == 400
    assert "college" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_create_submission_rejects_invalid_industry(client: AsyncClient):
    seed = client._seed  # type: ignore[attr-defined]
    resp = await client.post(
        "/api/submissions",
        data=_form(seed, industry_id=str(uuid.uuid4())),
        files=_file(),
    )
    assert resp.status_code == 400
    assert "industry" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_duplicate_email_college_returns_409(client: AsyncClient):
    seed = client._seed  # type: ignore[attr-defined]
    # First submission succeeds
    resp1 = await client.post("/api/submissions", data=_form(seed), files=_file())
    assert resp1.status_code == 201

    # Same email + college → 409
    resp2 = await client.post("/api/submissions", data=_form(seed), files=_file())
    assert resp2.status_code == 409


# ---------------------------------------------------------------------------
# GET /api/submissions (requires auth)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_list_submissions_requires_auth(client: AsyncClient):
    resp = await client.get("/api/submissions")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_list_submissions_with_valid_key(client: AsyncClient, monkeypatch):
    monkeypatch.setattr("app.config.settings.admin_api_key", ADMIN_KEY)
    seed = client._seed  # type: ignore[attr-defined]

    # Create one submission first
    await client.post("/api/submissions", data=_form(seed), files=_file())

    resp = await client.get(
        "/api/submissions",
        headers={"X-API-Key": ADMIN_KEY},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] >= 1
    assert len(body["submissions"]) >= 1


# ---------------------------------------------------------------------------
# GET /api/colleges & /api/industries
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_list_colleges(client: AsyncClient):
    resp = await client.get("/api/colleges")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_list_industries(client: AsyncClient):
    resp = await client.get("/api/industries")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


# ---------------------------------------------------------------------------
# Security headers
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_security_headers_present(client: AsyncClient):
    resp = await client.get("/api/health")
    assert resp.headers.get("X-Content-Type-Options") == "nosniff"
    assert resp.headers.get("X-Frame-Options") == "DENY"
