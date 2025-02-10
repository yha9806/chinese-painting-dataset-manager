from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.sql import func
from ..core.database import Base

class Painting(Base):
    __tablename__ = "paintings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), index=True)
    artist = Column(String(100), index=True)
    dynasty = Column(String(50))
    category = Column(String(50))
    description = Column(Text)
    painting_metadata = Column(JSON)
    image_path = Column(String(255))
    json_path = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 