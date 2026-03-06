from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func

from core.database import Base
from models.user import User # Discovery
from models.booking import Booking # Discovery

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)

    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)

    gateway = Column(String(50), nullable=False)  # razorpay / stripe / etc
    gateway_payment_id = Column(String(255), nullable=True)
    gateway_order_id = Column(String(255), nullable=True)

    status = Column(
        String(20),
        nullable=False,
        default="INITIATED"  # INITIATED | SUCCESS | FAILED
    )

    amount = Column(Float, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
