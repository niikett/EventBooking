import uuid
import json
import cloudinary.uploader
from urllib.parse import urlparse
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.core import jwt_token
from app.utils.utils_cloudinary import upload
from app.models import Event, Registration, User
from app.schemas.events import EventCreate, EventUpdate, EventResponse, EventUsersResponse, UserResponse
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
    event_data: str = Form(...),
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(jwt_token.get_current_user)
):
    current_user = db.query(User).filter(User.id == current_user.id).first()

    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can create events")

    try:
        event_dict = json.loads(event_data)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid event data format")

    if file:
        event_dict["image_url"] = upload(file)

    new_event = Event(**event_dict, created_by=current_user.id)
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
    updates: str = Form(...),
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(jwt_token.get_current_user)
):
    current_user = db.query(User).filter(User.id == current_user.id).first()

    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can update events")

    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    try:
        updates_dict = json.loads(updates)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid updates format")

    if file:
        updates_dict["image_url"] = upload(file)

    for key, value in updates_dict.items():
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

    if event.image_url:
        try:
            path = urlparse(event.image_url).path  
            public_id = "/".join(path.split("/")[-2:])
            public_id = public_id.rsplit(".", 1)[0]
        except Exception as e:
            return f"Failed to delete Cloudinary image: {e}"

    db.delete(event)
    db.commit()

    return {"detail": "Event and associated banner deleted"}


# -----------------------------
# Get All Events
# -----------------------------
@router.get("/all-events", response_model=list[EventResponse])
def get_all_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(jwt_token.get_current_user)
):
    current_user = db.query(User).filter(User.id == current_user.id).first()
    events = db.query(Event).all()
    return events


# -----------------------------
# Get Single Event by ID
# -----------------------------
@router.get("/{event_id}", response_model=EventResponse)
def get_event_by_id(
    event_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(jwt_token.get_current_user)
):
    current_user = db.query(User).filter(User.id == current_user.id).first()

    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    return event


# -----------------------------
# Get registered Users for an Event
# -----------------------------
@router.get("/{event_id}/users", response_model=EventUsersResponse)
def get_event_users(event_id: uuid.UUID, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    registrations = db.query(Registration).filter(Registration.event_id == event_id).all()
    users_list = [
        UserResponse(
            id=reg.user.id,
            name=reg.user.name,
            role=reg.user.role,
            department=reg.user.department,
            year=reg.user.year,
            email=reg.user.email
        ) for reg in registrations
    ]

    volunteers_list = []
    if event.volunteers:
        volunteers = db.query(User).filter(User.id.in_(event.volunteers)).all()
        volunteers_list = [
            UserResponse(
                id=v.id,
                name=v.name,
                role=v.role,
                department=v.department,
                year=v.year,
                email=v.email
            ) for v in volunteers
        ]

    return EventUsersResponse(
        total_count=len(users_list),
        users=users_list,
        volunteers=volunteers_list
    )