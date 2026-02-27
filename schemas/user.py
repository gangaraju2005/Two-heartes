from pydantic import BaseModel, EmailStr
from typing import Optional


class UserBase(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    mobile: Optional[str] = None


class UserUpdateRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None


class UserResponse(UserBase):
    id: int
    is_verified: bool
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True
        orm_mode = True