from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import os
import uuid
import shutil

from core.database import get_db
from api import deps
from models.user import User

router = APIRouter(prefix="/users", tags=["Users"])

from schemas.user import UserResponse, UserUpdateRequest

@router.post("/upload-avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a profile picture and return its URL.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Generate unique filename
    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{ext}"
    filepath = os.path.join("uploads/avatars", filename)

    # Save file
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # URL to access the file
    # Note: In production this would be a full URL, for now relative works with StaticFiles
    avatar_url = f"/uploads/avatars/{filename}"
    
    return {"avatar_url": avatar_url}

@router.get("/profile", response_model=UserResponse)
def get_user_profile(
    current_user: User = Depends(deps.get_current_user)
):
    return current_user

@router.put("/profile", response_model=UserResponse)
def update_user_profile(
    payload: UserUpdateRequest,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db)
):
    print(f"Update Profile Payload: Name={payload.name}, Email={payload.email}")
    if payload.avatar_url:
        print(f"PAYLOAD AVATAR FOUND: Length={len(payload.avatar_url)}")
    else:
        print("PAYLOAD AVATAR IS NONE")

    if payload.name is not None:
        current_user.name = payload.name
    if payload.email is not None:
        current_user.email = payload.email
    if payload.mobile is not None:
        current_user.mobile = payload.mobile
    if payload.push_token is not None:
        current_user.push_token = payload.push_token
    if payload.avatar_url is not None:
        print("SETTING AVATAR URL IN DB OBJECT")
        current_user.avatar_url = payload.avatar_url
    
    db.commit()
    db.refresh(current_user)
    print(f"POST-COMMIT CHECK: Avatar Length in DB Object={len(current_user.avatar_url) if current_user.avatar_url else 0}")
    return current_user
