from typing import Dict
from models.payment import Payment


def initiate_payment(
    booking_id: int,
    amount: float,
    gateway: str = "razorpay"
) -> Dict:
    """
    Create a payment intent/order.
    Gateway integration will be added later.
    """

    # Placeholder response (to be replaced with real gateway call)
    return {
        "booking_id": booking_id,
        "amount": amount,
        "gateway": gateway,
        "status": "INITIATED"
    }


def verify_payment(payload: Dict) -> bool:
    """
    Verify payment using gateway webhook data.
    """
    # Real verification logic will be added later
    return True


def update_payment_status(
    payment: Payment,
    status: str,
    gateway_payment_id: str | None = None
) -> None:
    """
    Update payment record after verification.
    """
    payment.status = status
    if gateway_payment_id:
        payment.gateway_payment_id = gateway_payment_id
