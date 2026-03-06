from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func

from core.database import Base
from models.user import User # Discovery


class Theatre(Base):
    __tablename__ = "theatres"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False, default="Unknown")
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    image_url = Column(String(500), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
