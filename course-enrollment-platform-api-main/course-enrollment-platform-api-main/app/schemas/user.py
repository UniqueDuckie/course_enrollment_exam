from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models import UserRole


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    role: UserRole = UserRole.student


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: UserRole
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
