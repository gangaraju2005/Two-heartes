from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from uuid import uuid4
import random
from pydantic import BaseModel
from typing import Optional
from core.database import get_db
from models.user import User
from schemas.user import UserResponse, UserUpdateRequest
from utils.jwt import create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])
OTP_STORE = {}




from schemas.auth import LoginRequest, VerifyOTPRequest, UserRole
from utils.password import get_password_hash, verify_password

@router.post("/request-otp")
async def request_otp(payload: LoginRequest, db: Session = Depends(get_db)):
    """
    Send OTP to mobile. Returns is_existing_user flag.
    """
    mobile = payload.mobile
    otp = random.randint(100000, 999999)
    print(f" Your ShowGO OTP for {mobile}: {otp}")
    OTP_STORE[mobile] = otp

    # Check if user already exists
    existing_user = db.query(User).filter(User.mobile == mobile).first()
    is_existing_user = existing_user is not None

    # Send OTP via SMS (AWS SNS)
    from services.sms import send_otp_sms
    sms_sent = await send_otp_sms(mobile, otp)

    return {
        "message": f"OTP sent to {mobile}",
        "sms_sent": sms_sent,
        "is_existing_user": is_existing_user
    }
    


@router.post("/verify-otp")
def verify_otp(
    payload: VerifyOTPRequest,
    db: Session = Depends(get_db)
):
    mobile = payload.mobile
    otp = payload.otp
    role = payload.role
    password = payload.password
    
    stored_otp = OTP_STORE.get(mobile)

    if not stored_otp or stored_otp != otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    # OTP verified, remove it
    OTP_STORE.pop(mobile, None)

    user = db.query(User).filter(User.mobile == mobile).first()

    if not user:
        # Create new user with appropriate role
        is_admin = (role == "ADMIN" or role == UserRole.ADMIN)
        is_merchant = (role == "MERCHANT" or role == UserRole.MERCHANT)
        
        # Hash password if provided
        hashed_pw = get_password_hash(password) if password else None
        
        user = User(
            mobile=mobile, 
            is_verified=True, 
            is_admin=is_admin, 
            is_merchant=is_merchant,
            password_hash=hashed_pw
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # User exists, check privileges if creating admin session
        if (role == "ADMIN" or role == UserRole.ADMIN) and not user.is_admin:
             raise HTTPException(status_code=403, detail="User exists but is not an admin")
        
        # Update password if provided and not set? Or just ignore? 
        # Let's allow setting it if not set, or updating it (reset flow)
        if password:
             user.password_hash = get_password_hash(password)
             db.commit()

    access_token = create_access_token(subject=str(user.id))

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_role": "ADMIN" if user.is_admin else "USER"
    }


class FirebaseVerifyRequest(BaseModel):
    id_token: str
    role: Optional[str] = "USER"
    password: Optional[str] = None


@router.post("/firebase-verify")
def firebase_verify(
    payload: FirebaseVerifyRequest,
    db: Session = Depends(get_db)
):
    """
    Verify Firebase ID token from client-side phone auth, create/find user, return JWT.
    """
    from services.firebase import verify_firebase_token

    try:
        decoded = verify_firebase_token(payload.id_token)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid Firebase token: {str(e)}")

    phone = decoded.get("phone_number")
    if not phone:
        raise HTTPException(status_code=400, detail="No phone number in Firebase token")

    # Normalize: remove +91 prefix for storage consistency
    mobile = phone
    if mobile.startswith("+91"):
        mobile = mobile[3:]
    elif mobile.startswith("+"):
        mobile = mobile[1:]

    user = db.query(User).filter(User.mobile == mobile).first()

    role = payload.role
    is_new_user = user is None

    if not user:
        is_admin = (role == "ADMIN" or role == UserRole.ADMIN)
        is_merchant = (role == "MERCHANT" or role == UserRole.MERCHANT)

        hashed_pw = get_password_hash(payload.password) if payload.password else None

        user = User(
            mobile=mobile,
            is_verified=True,
            is_admin=is_admin,
            is_merchant=is_merchant,
            password_hash=hashed_pw
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        if (role == "ADMIN" or role == UserRole.ADMIN) and not user.is_admin:
            raise HTTPException(status_code=403, detail="User exists but is not an admin")
        if payload.password:
            user.password_hash = get_password_hash(payload.password)
            db.commit()

    access_token = create_access_token(subject=str(user.id))

    user_role = "USER"
    if user.is_admin:
        user_role = "ADMIN"
    elif user.is_merchant:
        user_role = "MERCHANT"

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_role": user_role,
        "is_new_user": is_new_user
    }

@router.post("/login-password")
def login_password(
    payload: LoginRequest,
    db: Session = Depends(get_db)
):
    mobile = payload.mobile
    password = payload.password
    role = payload.role

    if not password:
        raise HTTPException(status_code=400, detail="Password is required")

    user = db.query(User).filter(User.mobile == mobile).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not user.password_hash or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
        
    if (role == "ADMIN" or role == UserRole.ADMIN) and not user.is_admin:
         raise HTTPException(status_code=403, detail="User exists but is not an admin")

    if (role == "MERCHANT" or role == UserRole.MERCHANT) and not user.is_merchant:
         raise HTTPException(status_code=403, detail="User exists but is not a merchant")

    access_token = create_access_token(subject=str(user.id))

    # Determine role for token response
    user_role = "USER"
    if user.is_admin:
        user_role = "ADMIN"
    elif user.is_merchant:
        user_role = "MERCHANT"

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_role": user_role
    }

from models.user import User
from api import deps
from schemas.auth import SetPasswordRequest

@router.post("/set-password")
def set_password(
    payload: SetPasswordRequest,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Set password for the current logged-in user.
    """
    if not payload.password:
        raise HTTPException(status_code=400, detail="Password is required")
    
    current_user.password_hash = get_password_hash(payload.password)
    db.commit()
    
    current_user.password_hash = get_password_hash(payload.password)
    db.commit()
    
    return {"message": "Password updated successfully"}


from schemas.user import UserResponse, UserUpdateRequest

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(
    current_user: User = Depends(deps.get_current_user)
):
    """
    Get current logged-in user details.
    """
    return current_user



class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    avatar_url: Optional[str] = None

@router.put("/me", response_model=UserResponse)
def update_current_user_profile(
    payload: UserProfileUpdate,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current logged-in user details (name, email, avatar).
    """
    print(f"AUTH UPDATE /me: Payload keys={payload.dict(exclude_unset=True).keys()}")
    if payload.avatar_url:
        print(f"AUTH UPDATE /me: Avatar Length={len(payload.avatar_url)}")

    if payload.name is not None:
        current_user.name = payload.name
    if payload.email is not None:
        current_user.email = payload.email
    if payload.avatar_url is not None:
        print("AUTH UPDATE /me: Setting avatar_url")
        current_user.avatar_url = payload.avatar_url
        
    db.commit()
    db.refresh(current_user)
    return current_user

