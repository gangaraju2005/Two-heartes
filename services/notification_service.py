def send_booking_confirmation(
    destination: str,
    booking_id: int
) -> None:
    """
    Send booking confirmation notification.
    destination: email or mobile
    """

    # Placeholder for email / SMS / push integration
    print(
        f"Booking confirmation sent to {destination} "
        f"for booking #{booking_id}"
    )


def send_payment_failure(
    destination: str,
    booking_id: int
) -> None:
    """
    Notify user about payment failure.
    """

    print(
        f"Payment failure notification sent to {destination} "
        f"for booking #{booking_id}"
    )
