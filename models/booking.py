from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Float
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from core.database import Base
from models.user import User  # Prevent uninitialized relation lookup
class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)

    # Either user_id OR guest_session_id will be present
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    show_id = Column(Integer, nullable=False)

    status = Column(
        String(20),
        nullable=False,
        default="LOCKED"  # LOCKED | CONFIRMED | CANCELLED | FAILED
    )

    total_amount = Column(Float, nullable=False, default=0.0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships (optional, useful later)
    user = relationship("User", backref="bookings")


class BookingSeat(Base):
    __tablename__ = "booking_seats"

    id = Column(Integer, primary_key=True, index=True)

    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)
    seat_id = Column(Integer, nullable=False)
