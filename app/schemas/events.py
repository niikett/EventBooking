from uuid import UUID
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    date_time: datetime
    location: str
    capacity: int
    event_type: str
    fees: Optional[int] = None


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    date_time: Optional[datetime] = None
    location: Optional[str] = None
    capacity: Optional[int] = None
    volunteers: Optional[List[UUID]] = None
    event_type: Optional[str] = None
    fees: Optional[int] = None
    image_url: Optional[str] = None


class EventResponse(EventBase):
    id: UUID
    title: str
    description: Optional[str] = None
    date_time: datetime
    location: str
    capacity: int
    event_type: str
    fees: Optional[int] = None
    image_url: Optional[str] = None
    created_by: UUID
    volunteers: List[UUID]
    created_at: datetime

    class Config:
        orm_mode = True
