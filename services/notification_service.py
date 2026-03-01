from sqlalchemy.orm import Session
from models.notification import Notification

def send_booking_confirmation(
    db: Session,
    user_id: int,
    booking_id: int,
    movie_title: str
) -> None:
    """
    Send and persist booking confirmation notification.
    """
    notification = Notification(
        user_id=user_id,
        title="Booking Confirmed!",
        message=f"Your ticket for '{movie_title}' has been booked successfully. Enjoy the show!"
    )
    db.add(notification)
    db.commit()
    
    print(f"Notification stored for user {user_id}: Booking #{booking_id}")


def send_checkin_notification(
    db: Session,
    user_id: int,
    booking_id: int,
    movie_title: str
) -> None:
    """
    Notify user that they have checked in.
    """
    notification = Notification(
        user_id=user_id,
        title="Welcome to the Cinema!",
        message=f"You've successfully checked in for '{movie_title}'. Have a great time!"
    )
    db.add(notification)
    db.commit()

    print(f"Notification stored for user {user_id}: Check-in for #{booking_id}")

def send_merchant_booking_notification(
    db: Session,
    merchant_user_id: int,
    booking_id: int,
    movie_title: str
) -> None:
    """
    Notify the merchant that a new ticket was booked.
    """
    notification = Notification(
        user_id=merchant_user_id,
        title="New Ticket Booked!",
        message=f"A ticket for '{movie_title}' has been booked (Booking #{booking_id})."
    )
    db.add(notification)
    db.commit()

    print(f"Merchant notification stored for user {merchant_user_id}: Booking #{booking_id}")
    
def send_merchant_cancellation_notification(
    db: Session,
    merchant_user_id: int,
    booking_id: int,
    movie_title: str
) -> None:
    """
    Notify the merchant that a ticket was cancelled.
    """
    notification = Notification(
        user_id=merchant_user_id,
        title="Ticket Cancelled",
        message=f"Ticket for '{movie_title}' has been cancelled."
    )
    db.add(notification)
    db.commit()

    print(f"Merchant cancellation notification stored for user {merchant_user_id}: Booking #{booking_id}")

def send_payment_failure(
    db: Session,
    user_id: int,
    booking_id: int
) -> None:
    """
    Notify user about payment failure.
    """
    notification = Notification(
        user_id=user_id,
        title="Payment Failed",
        message=f"There was an issue processing your payment for booking #{booking_id}. Please try again."
    )
    db.add(notification)
    db.commit()
