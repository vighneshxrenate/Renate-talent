import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr

from app.schemas.college import CollegeOut
from app.schemas.industry import IndustryOut


class SubmissionCreate(BaseModel):
    student_name: str
    email: EmailStr
    phone: str
    college_id: uuid.UUID
    industry_id: uuid.UUID
    note: Optional[str] = None


class SubmissionOut(BaseModel):
    id: uuid.UUID
    student_name: str
    email: str
    phone: str
    college: CollegeOut
    industry: IndustryOut
    resume_original_name: str
    note: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class SubmissionBrief(BaseModel):
    id: uuid.UUID
    message: str


class SubmissionListOut(BaseModel):
    submissions: List[SubmissionOut]
    total: int
    page: int
    page_size: int
