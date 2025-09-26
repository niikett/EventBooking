import uuid
from sqlalchemy import Column, String, ForeignKey, Integer, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.config_db import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    date_time = Column(DateTime(timezone=True), nullable=False)
    location = Column(String(200), nullable=False)
    capacity = Column(Integer, nullable=False)
    event_type = Column(String(100), nullable=False)
    fees = Column(Integer, nullable=True)
    image_url = Column(String, nullable=True)    
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    volunteers = Column(ARRAY(UUID(as_uuid=True)), default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    creator = relationship("User", back_populates="events")
    registrations = relationship("Registration", back_populates="event")
