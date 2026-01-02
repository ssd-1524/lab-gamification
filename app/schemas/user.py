from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional

# ------------------ Base Schemas ------------------ #

class UserBase(BaseModel):
    name: str

# ------------------ Input Schemas ------------------ #

class UserCreate(UserBase):
    """Schema for POST /auth/signup"""
    email: EmailStr
    password: str
    loc_id: UUID
    role_id: UUID

class UserLogin(BaseModel):
    """Schema for POST /auth/login"""
    email: EmailStr
    password: str

# ------------------ Output Schemas ------------------ #

class UserOut(UserBase):
    """Standard user profile representation"""
    user_id: UUID
    loc_id: UUID
    role_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

class LoginResponse(BaseModel):
    """Combined response for successful login"""
    access_token: str
    token_type: str = "bearer"
    user: UserOut
    session_id: Optional[UUID] = None

    class Config:
        from_attributes = True