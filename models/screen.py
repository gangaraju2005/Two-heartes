from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from core.database import Base
from models.theatre import Theatre # Import for relationship discovery

class Screen(Base):
    __tablename__ = "screens"

    id = Column(Integer, primary_key=True, index=True)

    theatre_id = Column(Integer, ForeignKey("theatres.id"), nullable=False)
    name = Column(String(100), nullable=False)
    technology = Column(String(50), nullable=True) # IMAX, Dolby, 4DX etc

    total_seats = Column(Integer, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    theatre = relationship("Theatre")
