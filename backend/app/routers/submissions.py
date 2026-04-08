import logging
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request, UploadFile
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.middleware.auth import require_admin_key
from app.models.college import College
from app.models.industry import Industry
from app.models.submission import Submission
from app.schemas.submission import SubmissionBrief, SubmissionListOut, SubmissionOut
from app.services.storage import storage_service

logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)
router = APIRouter(tags=["submissions"])


@router.post("/submissions", response_model=SubmissionBrief, status_code=201)
@limiter.limit("5/minute")
async def create_submission(
    request: Request,
    student_name: str = Form(..., min_length=1, max_length=200),
    email: str = Form(...),
    phone: str = Form(..., min_length=7, max_length=20),
    college_id: uuid.UUID = Form(...),
    industry_id: uuid.UUID = Form(...),
    resume: UploadFile = UploadFile(...),
    note: Optional[str] = Form(None, max_length=1000),
    db: AsyncSession = Depends(get_db),
):
    # Validate file type
    if resume.content_type != "application/pdf":
        raise HTTPException(400, "Only PDF files are accepted")

    file_bytes = await resume.read()

    # Validate file size
    if len(file_bytes) > settings.max_upload_size_bytes:
        raise HTTPException(400, f"File size exceeds {settings.max_upload_size_mb}MB limit")

    # Validate PDF magic bytes
    if not file_bytes[:5] == b"%PDF-":
        raise HTTPException(400, "File does not appear to be a valid PDF")

    # Verify college exists and get slug
    college = await db.get(College, college_id)
    if not college:
        raise HTTPException(400, "Invalid college_id")

    # Verify industry exists
    industry = await db.get(Industry, industry_id)
    if not industry:
        raise HTTPException(400, "Invalid industry_id")

    # Upload to Supabase Storage (raises HTTPException on failure)
    storage_path = await storage_service.upload_resume(
        file_bytes, college.slug, student_name
    )

    # Insert DB row
    submission = Submission(
        student_name=student_name,
        email=email,
        phone=phone,
        college_id=college_id,
        industry_id=industry_id,
        resume_storage_path=storage_path,
        resume_original_name=resume.filename or "resume.pdf",
        note=note,
    )
    db.add(submission)
    try:
        await db.commit()
        await db.refresh(submission)
        logger.info("Submission created: %s (%s, %s)", submission.id, email, college.slug)
    except IntegrityError:
        await db.rollback()
        await storage_service.delete_resume(storage_path)
        raise HTTPException(409, "A submission with this email already exists for this college")
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error("DB error saving submission: %s", e)
        await storage_service.delete_resume(storage_path)
        raise HTTPException(500, "Failed to save submission, please try again")

    return SubmissionBrief(id=submission.id, message="Submission received successfully")


@router.get("/submissions", response_model=SubmissionListOut)
@limiter.limit("30/minute")
async def list_submissions(
    request: Request,
    college_id: Optional[uuid.UUID] = None,
    industry_id: Optional[uuid.UUID] = None,
    page: int = 1,
    page_size: int = 50,
    db: AsyncSession = Depends(get_db),
    _key: str = Depends(require_admin_key),
):
    query = select(Submission)
    count_query = select(func.count()).select_from(Submission)

    if college_id:
        query = query.where(Submission.college_id == college_id)
        count_query = count_query.where(Submission.college_id == college_id)
    if industry_id:
        query = query.where(Submission.industry_id == industry_id)
        count_query = count_query.where(Submission.industry_id == industry_id)

    total = (await db.execute(count_query)).scalar_one()

    query = query.order_by(Submission.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)

    return SubmissionListOut(
        submissions=result.scalars().all(),
        total=total,
        page=page,
        page_size=page_size,
    )
