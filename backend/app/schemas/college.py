import uuid

from pydantic import BaseModel


class CollegeOut(BaseModel):
    id: uuid.UUID
    name: str
    slug: str

    model_config = {"from_attributes": True}
