from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class CourseBase(BaseModel):
    code: str
    title: str
    description: Optional[str] = None

class CourseCreate(CourseBase):
    pass

class CourseResponse(CourseBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)