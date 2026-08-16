from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: Optional[int] = None

# User Base Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    is_superuser: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)