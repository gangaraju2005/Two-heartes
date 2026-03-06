from sqlalchemy import Column, Integer, String, Date, Float, DateTime, ForeignKey
from sqlalchemy.sql import func

from core.database import Base
from models.user import User # Discovery


class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(255), nullable=False)
    language = Column(String(50), nullable=False)
    duration_minutes = Column(Integer, nullable=False)

    rating = Column(Float, default=0.0)
    release_date = Column(Date, nullable=True)
    genre = Column(String(100), nullable=True)
    poster_url = Column(String(500), nullable=True)
    
    # New fields
    description = Column(String(1000), nullable=True)
    cast_members = Column(String(500), nullable=True) # Stored as comma-separated string or JSON string
    status = Column(String(50), default="ACTIVE") # e.g. "ACTIVE" or "COMING_SOON"
    
    # Owner - scopes movies to the merchant who created them
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
