from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ReviewCreate(BaseModel):
    movie_id: int
    rating: float
    comment: Optional[str] = None

class ReviewResponse(BaseModel):
    id: int
    user_id: int
    user_name: str
    movie_id: int
    rating: float
    comment: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
