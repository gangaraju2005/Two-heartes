from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class AddTheatreRequest(BaseModel):
    name: str
    city: str

class AddScreenRequest(BaseModel):
    theatre_id: int
    name: str
    total_seats: int

class AddMovieRequest(BaseModel):
    title: str
    language: str
    duration_minutes: int
    rating: float = 0.0
    release_date: Optional[date] = None

class AddShowRequest(BaseModel):
    movie_id: int
    screen_id: int
    show_times: list[datetime]
