from pydantic import BaseModel
from enum import Enum

class UserRole(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"
    MERCHANT = "MERCHANT"

class LoginRequest(BaseModel):
    mobile: str
    password: str | None = None
    role: UserRole = UserRole.USER

class VerifyOTPRequest(BaseModel):
    mobile: str
    otp: int
    password: str | None = None
    role: UserRole = UserRole.USER

class SetPasswordRequest(BaseModel):
    password: str
