from pydantic import BaseModel
from typing import List, Optional


class SeatLockRequest(BaseModel):
    show_id: int
    seat_ids: List[int]


class BookingCreate(BaseModel):
    show_id: int
    seat_ids: List[int]


class BookingResponse(BaseModel):
    id: int
    show_id: int
    status: str
    total_amount: float
    # Enhanced Details
    movie_id: Optional[int] = None
    movie_title: Optional[str] = None
    theater_name: Optional[str] = None
    show_time: Optional[str] = None
    poster_url: Optional[str] = None
    seat_label: Optional[str] = None

    class Config:
        from_attributes = True
