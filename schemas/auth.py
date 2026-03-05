from pydantic import BaseModel
from enum import Enum

class UserRole(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"
    MERCHANT = "MERCHANT"

class OTPPurpose(str, Enum):
    LOGIN = "LOGIN"
    RESET = "RESET"

class LoginRequest(BaseModel):
    email: str | None = None
    mobile: str | None = None
    password: str | None = None
    role: UserRole = UserRole.USER
    purpose: OTPPurpose = OTPPurpose.LOGIN

class VerifyOTPRequest(BaseModel):
    email: str | None = None
    mobile: str | None = None
    otp: int
    password: str | None = None
    role: UserRole = UserRole.USER

class SetPasswordRequest(BaseModel):
    password: str
