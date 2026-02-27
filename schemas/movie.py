from pydantic import BaseModel
from typing import Optional
from datetime import date


class MovieBase(BaseModel):
    title: str
    language: str
    duration_minutes: int
    release_date: Optional[date] = None


class MovieCreate(MovieBase):
    pass


class MovieResponse(MovieBase):
    id: int
    rating: float
    genre: Optional[str] = None
    poster_url: Optional[str] = None
    description: Optional[str] = None
    cast_members: Optional[str] = None
    status: Optional[str] = "ACTIVE"

    class Config:
        from_attributes = True
