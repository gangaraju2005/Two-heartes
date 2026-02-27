from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from models.user import User
from models.theatre import Theatre
from models.screen import Screen
from models.movie import Movie
from models.show import Show
from schemas.admin import (
    AddTheatreRequest,
    AddScreenRequest,
    AddMovieRequest,
    AddShowRequest
)
from api import deps

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/add-theatre")
def add_theatre(
    payload: AddTheatreRequest,
    current_user: User = Depends(deps.get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Add a new theatre (Admin only).
    """
    theatre = Theatre(
        name=payload.name,
        city=payload.city,
        owner_id=current_user.id
    )
    db.add(theatre)
    db.commit()
    db.refresh(theatre)
    return {"message": "Theatre added successfully", "theatre_id": theatre.id}


@router.post("/add-screen")
def add_screen(
    payload: AddScreenRequest,
    current_user: User = Depends(deps.get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Add a screen to a theatre (Admin only).
    """
    # Verify theatre ownership
    theatre = db.query(Theatre).filter(Theatre.id == payload.theatre_id).first()
    if not theatre:
        raise HTTPException(status_code=404, detail="Theatre not found")
    
    if theatre.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to add screen to this theatre")

    screen = Screen(
        theatre_id=payload.theatre_id,
        name=payload.name,
        total_seats=payload.total_seats
    )
    db.add(screen)
    db.commit()
    db.refresh(screen)
    return {"message": "Screen added successfully", "screen_id": screen.id}


@router.post("/add-movie")
def add_movie(
    payload: AddMovieRequest,
    current_user: User = Depends(deps.get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Add a new movie (Admin only).
    """
    movie = Movie(
        title=payload.title,
        language=payload.language,
        duration_minutes=payload.duration_minutes,
        rating=payload.rating,
        release_date=payload.release_date
    )
    db.add(movie)
    db.commit()
    db.refresh(movie)
    return {"message": "Movie added successfully", "movie_id": movie.id}


@router.post("/add-show")
def add_show(
    payload: AddShowRequest,
    current_user: User = Depends(deps.get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Add a show for a movie on a screen (Admin only).
    """
    # Verify screen and theatre ownership
    screen = db.query(Screen).filter(Screen.id == payload.screen_id).first()
    if not screen:
        raise HTTPException(status_code=404, detail="Screen not found")

    theatre = db.query(Theatre).filter(Theatre.id == screen.theatre_id).first()
    if not theatre or theatre.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to schedule shows for this screen")

    created_shows = []
    for show_time in payload.show_times:
        show = Show(
            movie_id=payload.movie_id,
            screen_id=payload.screen_id,
            show_time=show_time
        )
        db.add(show)
        created_shows.append(show)
    
    db.commit()
    for show in created_shows:
        db.refresh(show)
        
    return {
        "message": f"{len(created_shows)} shows added successfully", 
        "show_ids": [s.id for s in created_shows]
    }
