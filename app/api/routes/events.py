import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core import jwt_token
from app.models import Event, Registration, User
from app.schemas.events import EventCreate, EventUpdate, EventResponse
from app.core.config_db import get_db

router = APIRouter(
    prefix="/events",
    tags=["events"]
)

# -----------------------------
# Create Event (Admin only)
# -----------------------------
@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    event: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(jwt_token.get_current_user)
):
    current_user = db.query(User).filter(User.id == current_user.id).first()

    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can create events")

    new_event = Event(**event.dict(), created_by=current_user.id)
    db.add(new_event)
    db.flush()
    db.refresh(new_event)

    registration = Registration(
        user_id=current_user.id,
        event_id=new_event.id
    )
    db.add(registration)
    db.commit()

    return new_event


# -----------------------------
# Update Event (Admin only)
# -----------------------------
@router.put("/{event_id}", response_model=EventResponse)
def update_event(
    event_id: uuid.UUID,
    updates: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(jwt_token.get_current_user)
):
    current_user = db.query(User).filter(User.id == current_user.id).first()
    
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can update events")

    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    for key, value in updates.dict(exclude_unset=True).items():
        setattr(event, key, value)

    db.commit()
    db.refresh(event)
    return event


# -----------------------------
# Delete Event (Admin only)
# -----------------------------
@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(jwt_token.get_current_user)
):
    current_user = db.query(User).filter(User.id == current_user.id).first()
    
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can delete events")

    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    db.delete(event)
    db.commit()
    return {"detail": "Event deleted"}


# -----------------------------
# Get Events (All)
# -----------------------------
@router.get("all-events/", response_model=list[EventResponse])
def get_registered_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(jwt_token.get_current_user)
):
    current_user = db.query(User).filter(User.id == current_user.id).first()
    
    events = db.query(Event).all()
    return events
