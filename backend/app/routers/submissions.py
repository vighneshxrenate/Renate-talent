import csv
import io
import logging
import uuid
import zipfile
from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request, UploadFile
from fastapi.responses import StreamingResponse
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
    phone: str = Form(..., min_length=10, max_length=10, pattern=r'^\d{10}$'),
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
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
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


def _csv_safe(value: str) -> str:
    """Prevent CSV injection by prefixing formula-triggering characters."""
    if value and value[0] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + value
    return value


@router.get("/submissions/export/csv")
@limiter.limit("10/minute")
async def export_submissions_csv(
    request: Request,
    industry_id: Optional[uuid.UUID] = None,
    college_id: Optional[uuid.UUID] = None,
    db: AsyncSession = Depends(get_db),
    _key: str = Depends(require_admin_key),
):
    query = select(Submission).order_by(Submission.created_at.desc())
    if industry_id:
        query = query.where(Submission.industry_id == industry_id)
    if college_id:
        query = query.where(Submission.college_id == college_id)

    result = await db.execute(query)
    submissions = result.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "name", "email", "phone", "college", "industry", "note", "submitted_at", "resume_link"])
    for s in submissions:
        signed_url = await storage_service.create_signed_url(s.resume_storage_path)
        writer.writerow([
            str(s.id),
            _csv_safe(s.student_name),
            _csv_safe(s.email),
            s.phone,
            _csv_safe(s.college.name if s.college else ""),
            _csv_safe(s.industry.name if s.industry else ""),
            _csv_safe(s.note or ""),
            s.created_at.isoformat(),
            signed_url,
        ])

    output.seek(0)
    filename = f"submissions_{industry_id or 'all'}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/submissions/export/zip")
@limiter.limit("5/minute")
async def export_submissions_zip(
    request: Request,
    industry_id: Optional[uuid.UUID] = None,
    college_id: Optional[uuid.UUID] = None,
    db: AsyncSession = Depends(get_db),
    _key: str = Depends(require_admin_key),
):
    query = select(Submission).order_by(Submission.created_at.desc())
    if industry_id:
        query = query.where(Submission.industry_id == industry_id)
    if college_id:
        query = query.where(Submission.college_id == college_id)

    result = await db.execute(query)
    submissions = result.scalars().all()

    if not submissions:
        raise HTTPException(404, "No submissions found for the given filters")

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for s in submissions:
            try:
                file_bytes = await storage_service.download_resume(s.resume_storage_path)
                industry_name = s.industry.name if s.industry else "unknown"
                college_name = s.college.name if s.college else "unknown"
                safe_name = s.student_name.replace(" ", "_")[:40]
                filename = f"{industry_name}/{college_name}/{safe_name}.pdf"
                zf.writestr(filename, file_bytes)
            except Exception as e:
                logger.error("Failed to fetch resume %s: %s", s.resume_storage_path, e)

    zip_buffer.seek(0)
    label = f"resumes_{industry_id or 'all'}"
    return StreamingResponse(
        iter([zip_buffer.getvalue()]),
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={label}.zip"},
    )
