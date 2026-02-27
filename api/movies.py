from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from models.movie import Movie
from schemas.movie import MovieResponse

router = APIRouter(prefix="/movies", tags=["Movies"])


from api import deps
from models.user import User

@router.get("", response_model=List[MovieResponse])
def list_movies(
    db: Session = Depends(get_db)
):
    """
    List all movies.
    """
    movies = db.query(Movie).all()
    return movies


@router.get("/{movie_id}", response_model=MovieResponse)
def get_movie(
    movie_id: int,
    db: Session = Depends(get_db)
):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()

    if not movie:
        raise HTTPException(
            status_code=404,
            detail="Movie not found"
        )

    return movie

