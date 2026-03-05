from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    mobile: Optional[str] = None
    avatar_url: Optional[str] = None
    push_token: Optional[str] = None

class UserUpdateRequest(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    is_verified: bool
    is_admin: bool
    is_merchant: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        orm_mode = True