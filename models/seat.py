from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.sql import func

from core.database import Base
from models.screen import Screen # Discovery


class Seat(Base):
    __tablename__ = "seats"

    id = Column(Integer, primary_key=True, index=True)

    screen_id = Column(Integer, ForeignKey("screens.id"), nullable=False)

    seat_number = Column(String(10), nullable=False)   # e.g. A1, B12
    row = Column(String(5), nullable=True)             # e.g. A
    col = Column(Integer, nullable=True)               # e.g. 1
    
    seat_type = Column(String(50), nullable=False)     # REGULAR / PREMIUM / RECLINER
    is_blocked = Column(Boolean, default=False)        # Maintenance or blocked by merchant
    price = Column(Float, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
