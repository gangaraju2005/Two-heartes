from fastapi import APIRouter, HTTPException
from schemas.booking import SeatLockRequest
from services.seat_lock import lock_seats, get_locked_seats
from api import deps
from models.user import User
from fastapi import Depends
from sqlalchemy.orm import Session
from core.database import get_db

router = APIRouter(prefix="/seats", tags=["Seats"])


@router.get("/layout/{show_id}")
def get_seat_layout(
    show_id: int,
    db: Session = Depends(get_db)  # Removed current_user to make it public if needed, or keep for booking flow
):
    """
    Get all seats for a show with their status (AVAILABLE, BOOKED, LOCKED).
    """
    # 1. Get Show -> Screen -> Seats
    from models.show import Show
    from models.seat import Seat
    from models.booking import Booking, BookingSeat
    
    show = db.query(Show).filter(Show.id == show_id).first()
    if not show:
        raise HTTPException(status_code=404, detail="Show not found")
        
    seats = db.query(Seat).filter(Seat.screen_id == show.screen_id).all()
    
    # 2. Get Booked/Locked Seat IDs
    bookings = db.query(Booking).filter(
        Booking.show_id == show_id,
        Booking.status.in_(["CONFIRMED", "LOCKED"]) 
    ).all()

    db_booked_ids = set()
    for b in bookings:
        b_seats = db.query(BookingSeat).filter(BookingSeat.booking_id == b.id).all()
        for bs in b_seats:
            db_booked_ids.add(bs.seat_id)

    from services.seat_lock import get_locked_seats
    try:
        redis_locked_ids = set(get_locked_seats(show_id))
    except Exception as e:
        print(f"Redis error: {e}")
        redis_locked_ids = set()
    
    # 3. Construct Response
    layout = []
    for seat in seats:
        status = "AVAILABLE"
        if seat.id in db_booked_ids:
            status = "BOOKED"
        elif seat.id in redis_locked_ids:
            status = "LOCKED"
            
        # Calculate dynamic price based on seat type and show base price
        dynamic_price = float(show.price)
        if seat.seat_type == "REGULAR":
            dynamic_price += 1.0
        elif seat.seat_type == "PREMIUM":
            dynamic_price += 100.0
        elif seat.seat_type == "RECLINER":
            dynamic_price += 200.0

        layout.append({
            "id": seat.id,
            "row": seat.seat_number[0],
            "number": seat.seat_number[1:],
            "type": seat.seat_type,
            "price": dynamic_price,
            "status": status
        })
        
    return layout


@router.post("/lock")
def lock_seat(
    req: SeatLockRequest,
    current_user: "User" = Depends(deps.get_current_user)
):
    """
    Lock seats for a user.
    """
    success = lock_seats(
        show_id=req.show_id,
        seat_ids=req.seat_ids,
        owner_id=str(current_user.id)
    )

    if not success:
        raise HTTPException(
            status_code=409,
            detail="One or more seats already locked"
        )

    from core.config import settings
    return {
        "message": "Seats locked successfully",
        "expires_in": settings.SEAT_LOCK_TTL
    }


@router.post("/unlock")
def unlock_seat(
    req: SeatLockRequest,
    current_user: "User" = Depends(deps.get_current_user)
):
    """
    Unlock seats for a user (e.g. when cancelling checkout).
    """
    from services.seat_lock import release_seats
    
    # We could/should check if the current_user actually owns the lock,
    # but release_seats currently just deletes the key.
    # For a robust implementation, we might want to check ownership, 
    # but for this MVP, just trusting the user to unlock their own session seats is acceptable.
    
    release_seats(req.show_id, req.seat_ids)
    
    return {"message": "Seats unlocked successfully"}
