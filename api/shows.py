from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db

router = APIRouter(prefix="/shows", tags=["Shows"])


from api import deps
from models.user import User

from models.show import Show
from models.screen import Screen
from models.theatre import Theatre
from schemas.shows import TheatreShowsResponse, ShowResponse
from collections import defaultdict

@router.get("/movie/{movie_id}", response_model=List[TheatreShowsResponse])
def list_shows_for_movie(
    movie_id: int,
    city: str = None,
    db: Session = Depends(get_db)
):
    """
    List all shows for a given movie, grouped by theatre.
    """
    # Join Show -> Screen -> Theatre
    query = (
        db.query(Show, Screen, Theatre)
        .join(Screen, Show.screen_id == Screen.id)
        .join(Theatre, Screen.theatre_id == Theatre.id)
        .filter(Show.movie_id == movie_id)
    )

    if city:
        query = query.filter(Theatre.city == city)

    results = query.all()

    # Group by Theatre
    theatre_map = defaultdict(lambda: {"shows": []})
    
    for show, screen, theatre in results:
        # Check if theatre already added to map, if not, add basic info
        if theatre.id not in theatre_map:
            theatre_map[theatre.id].update({
                "theatre_id": theatre.id,
                "theatre_name": theatre.name,
                "city": theatre.city,
                "image_url": theatre.image_url,
                "shows": []
            })
        
        # Add show details
        theatre_map[theatre.id]["shows"].append(
            ShowResponse(
                show_id=show.id,
                show_time=show.show_time,
                screen_id=screen.id,
                screen_name=screen.name,
                screen_technology=screen.technology
            )
        )

    return list(theatre_map.values())
