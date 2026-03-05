from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func

from core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=True)
    email = Column(String(255), unique=True, index=True, nullable=True)
    mobile = Column(String(20), unique=True, index=True, nullable=True)
    password_hash = Column(String(255), nullable=True)
    avatar_url = Column(String, nullable=True)  # Changed to String (Text) for Base64

    is_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    is_merchant = Column(Boolean, default=False)
    push_token = Column(String(255), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
