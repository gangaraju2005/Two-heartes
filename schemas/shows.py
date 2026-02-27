from pydantic import BaseModel
from datetime import datetime
from typing import List

class ShowResponse(BaseModel):
    show_id: int
    show_time: datetime
    screen_id: int
    screen_name: str
    screen_technology: str | None = None

class TheatreShowsResponse(BaseModel):
    theatre_id: int
    theatre_name: str
    city: str
    image_url: str | None = None
    shows: List[ShowResponse]
