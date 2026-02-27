from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict

from core.database import get_db
from models.payment import Payment
from models.booking import Booking
from services.payment_service import (
    initiate_payment,
    verify_payment,
    update_payment_status
)

router = APIRouter(prefix="/payments", tags=["Payments"])


from schemas.request import BookingIdRequest
from models.user import User
from api import deps

@router.post("/initiate")
def initiate_payment_api(
    payload: BookingIdRequest,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Initiate payment for a booking.
    """

    booking = db.query(Booking).filter(Booking.id == payload.booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    payment_data = initiate_payment(
        booking_id=booking.id,
        amount=booking.total_amount
    )

    payment = Payment(
        booking_id=booking.id,
        gateway=payment_data["gateway"],
        status="INITIATED",
        amount=payment_data["amount"]
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return payment_data


@router.post("/webhook")
def payment_webhook(
    payload: Dict,
    db: Session = Depends(get_db)
):
    """
    Payment gateway webhook endpoint.
    """

    is_valid = verify_payment(payload)
    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid payment")

    booking_id = payload.get("booking_id")
    gateway_payment_id = payload.get("gateway_payment_id")

    payment = (
        db.query(Payment)
        .filter(Payment.booking_id == booking_id)
        .first()
    )

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    update_payment_status(
        payment,
        status="SUCCESS",
        gateway_payment_id=gateway_payment_id
    )

    booking = (
        db.query(Booking)
        .filter(Booking.id == booking_id)
        .first()
    )
    booking.status = "CONFIRMED"

    db.commit()

    return {"message": "Payment verified and booking confirmed"}
