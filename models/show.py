from sqlalchemy import Column, Integer, ForeignKey, DateTime, Float
from sqlalchemy.sql import func

from core.database import Base
from models.movie import Movie # Discovery
from models.screen import Screen # Discovery


class Show(Base):
    __tablename__ = "shows"

    id = Column(Integer, primary_key=True, index=True)

    movie_id = Column(Integer, ForeignKey("movies.id"), nullable=False)
    screen_id = Column(Integer, ForeignKey("screens.id"), nullable=False)

    show_time = Column(DateTime(timezone=True), nullable=False)
    price = Column(Float, nullable=False, default=10.0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
