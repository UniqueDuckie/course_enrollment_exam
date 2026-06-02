from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CourseCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    code: str = Field(min_length=1, max_length=50)
    capacity: int = Field(gt=0)


class CourseUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    code: Optional[str] = Field(default=None, min_length=1, max_length=50)
    capacity: Optional[int] = Field(default=None, gt=0)


class CourseOut(BaseModel):
    id: int
    title: str
    code: str
    capacity: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
