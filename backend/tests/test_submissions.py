import uuid
from io import BytesIO
from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.asyncio
async def test_missing_fields_returns_422(client):
    response = await client.post("/api/submissions")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_non_pdf_content_type_rejected(client, seed_data):
    response = await client.post(
        "/api/submissions",
        data={
            "student_name": "Test User",
            "email": "test@example.com",
            "phone": "1234567890",
            "college_id": str(seed_data["college"].id),
            "industry_id": str(seed_data["industry"].id),
        },
        files={"resume": ("resume.txt", BytesIO(b"not a pdf"), "text/plain")},
    )
    assert response.status_code == 400
    assert "PDF" in response.json()["detail"]


@pytest.mark.asyncio
async def test_invalid_pdf_magic_bytes_rejected(client, seed_data):
    response = await client.post(
        "/api/submissions",
        data={
            "student_name": "Test User",
            "email": "test@example.com",
            "phone": "1234567890",
            "college_id": str(seed_data["college"].id),
            "industry_id": str(seed_data["industry"].id),
        },
        files={
            "resume": ("resume.pdf", BytesIO(b"not a real pdf"), "application/pdf")
        },
    )
    assert response.status_code == 400
    assert "valid PDF" in response.json()["detail"]


@pytest.mark.asyncio
async def test_invalid_college_id_rejected(client, seed_data):
    fake_pdf = b"%PDF-1.4 fake content"
    response = await client.post(
        "/api/submissions",
        data={
            "student_name": "Test User",
            "email": "test@example.com",
            "phone": "1234567890",
            "college_id": str(uuid.uuid4()),
            "industry_id": str(seed_data["industry"].id),
        },
        files={
            "resume": ("resume.pdf", BytesIO(fake_pdf), "application/pdf")
        },
    )
    assert response.status_code == 400
    assert "college_id" in response.json()["detail"]


@pytest.mark.asyncio
@patch("app.routers.submissions.storage_service")
async def test_valid_submission_succeeds(mock_storage, client, seed_data):
    mock_storage.upload_resume = AsyncMock(return_value="test-college/2026-04/abc_test_resume.pdf")
    mock_storage.delete_resume = AsyncMock()

    fake_pdf = b"%PDF-1.4 fake content for testing"
    response = await client.post(
        "/api/submissions",
        data={
            "student_name": "Test User",
            "email": "test@example.com",
            "phone": "1234567890",
            "college_id": str(seed_data["college"].id),
            "industry_id": str(seed_data["industry"].id),
            "note": "Excited to apply!",
        },
        files={
            "resume": ("resume.pdf", BytesIO(fake_pdf), "application/pdf")
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["message"] == "Submission received successfully"
    mock_storage.upload_resume.assert_called_once()
