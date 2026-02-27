from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.database import get_db
from schemas.booking import BookingCreate, BookingResponse
from models.booking import Booking
from services.seat_lock import release_seats
from api import deps
from models.user import User

router = APIRouter(prefix="/booking", tags=["Booking"])


@router.post("/", response_model=BookingResponse)
def create_booking(
    payload: BookingCreate,
    current_user: "User" = Depends(deps.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a booking after seats are locked.
    """

    booking = Booking(
        show_id=payload.show_id,
        user_id=current_user.id,
        status="LOCKED",
        total_amount=0.0
    )

    db.add(booking)
    db.commit()
    db.refresh(booking)

    # Save the seats!
    from models.booking import BookingSeat
    for seat_id in payload.seat_ids:
        booking_seat = BookingSeat(
            booking_id=booking.id,
            seat_id=seat_id
        )
        db.add(booking_seat)
    
    db.commit()

    # Calculate Total Amount using dynamic logic (Show Base Price + Seat Category offset)
    from models.show import Show
    from models.seat import Seat
    
    show = db.query(Show).filter(Show.id == payload.show_id).first()
    seats = db.query(Seat).filter(Seat.id.in_(payload.seat_ids)).all()
    
    total_price = 0.0
    if show:
        base_price = float(show.price)
        for seat in seats:
            seat_price = base_price
            if seat.seat_type == "PREMIUM":
                seat_price += 100.0  # Must match the offset in seats.py
            elif seat.seat_type == "RECLINER":
                seat_price += 200.0  # Must match the offset in seats.py
            elif seat.seat_type == "REGULAR":
                seat_price += 1.0  # Must match the offset in seats.py! User changed this to 1.0 earlier
            total_price += seat_price
            
    booking.total_amount = total_price
    db.commit()

    return booking


from schemas.request import ConfirmBookingRequest

@router.post("/confirm")
def confirm_booking(
    payload: ConfirmBookingRequest,
    current_user: "User" = Depends(deps.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Confirm booking after successful payment.
    """

    booking = db.query(Booking).filter(Booking.id == payload.booking_id).first()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    booking.status = "CONFIRMED"
    db.commit()

    # Release Redis locks
    release_seats(booking.show_id, payload.seat_ids)

    return {
        "message": "Booking confirmed",
        "booking_id": booking.id
    }


@router.get("/my-bookings", response_model=list[BookingResponse])
def get_my_bookings(
    current_user: "User" = Depends(deps.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all bookings for the current user.
    """
    try:
        # Join Booking -> Show -> Movie, Screen
        from models.show import Show
        from models.movie import Movie
        from models.screen import Screen
        from models.theatre import Theatre
        
        from datetime import datetime, time
        now = datetime.now()
        today_start = datetime.combine(now.date(), time.min)
        
        results = db.query(Booking, Movie, Show, Screen, Theatre).outerjoin(
            Show, Booking.show_id == Show.id
        ).outerjoin(
            Movie, Show.movie_id == Movie.id
        ).outerjoin(
            Screen, Show.screen_id == Screen.id
        ).outerjoin(
            Theatre, Screen.theatre_id == Theatre.id
        ).filter(
            Booking.user_id == current_user.id,
            Show.id != None,
            Movie.id != None,
            Show.show_time >= today_start
        ).order_by(Show.show_time.asc()).all()
        
        response = []
        for booking, movie, show, screen, theatre in results:
            # Convert to Pydantic model and enrich
            booking_data = BookingResponse.from_orm(booking)
            booking_data.movie_id = movie.id if movie else None
            booking_data.movie_title = movie.title if movie else "Unknown Movie"
            booking_data.theater_name = theatre.name if theatre else (screen.name if screen else "Unknown Theater")
            booking_data.show_time = show.show_time.isoformat() if show else None
            booking_data.poster_url = movie.poster_url if movie else None
            
            # Fetch seats for this booking
            from models.booking import BookingSeat
            from models.seat import Seat
            booking_seats = db.query(Seat).join(BookingSeat, BookingSeat.seat_id == Seat.id).filter(BookingSeat.booking_id == booking.id).all()
            booking_data.seat_label = ", ".join([s.seat_number for s in booking_seats])
            
            response.append(booking_data)
            
        return response
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
