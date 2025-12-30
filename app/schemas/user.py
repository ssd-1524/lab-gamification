from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class UserBase(BaseModel):
    name: str

class UserOut(UserBase):
    user_id: UUID
    loc_id: UUID
    role_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
