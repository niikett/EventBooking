import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core import jwt_token
from app.models import Event, Registration, User
from app.schemas.registrations import RegistrationCreate, RegistrationResponse
from app.core.config_db import get_db

router = APIRouter(
    prefix="/registrations",
    tags=["registrations"]
)


# -----------------------------
# Register for Event (Student only)
# -----------------------------
@router.post("/", response_model=RegistrationResponse, status_code=status.HTTP_201_CREATED)
def register_for_event(
    registration: RegistrationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(jwt_token.get_current_user)
):
    current_user = db.query(User).filter(User.id == current_user.id).first()

    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can register for events")

    event = db.query(Event).filter(Event.id == registration.event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # check if already registered
    existing = db.query(Registration).filter(
        Registration.user_id == current_user.id,
        Registration.event_id == registration.event_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already registered for this event")

    # check capacity
    count = db.query(Registration).filter(Registration.event_id == registration.event_id).count()
    if count >= event.capacity:
        raise HTTPException(status_code=400, detail="Event capacity full")

    new_registration = Registration(user_id=current_user.id, event_id=registration.event_id)
    db.add(new_registration)
    db.commit()
    db.refresh(new_registration)

    return new_registration


# -----------------------------
# Unregister from Event
# -----------------------------
@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def unregister_from_event(
    event_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(jwt_token.get_current_user)
):
    current_user = db.query(User).filter(User.id == current_user.id).first()

    registration = db.query(Registration).filter(
        Registration.user_id == current_user.id,
        Registration.event_id == event_id
    ).first()
    if not registration:
        raise HTTPException(status_code=404, detail="Not registered for this event")

    db.delete(registration)
    db.commit()

    return {"detail": "Unregistered successfully"}


# -----------------------------
# Get My Registrations
# -----------------------------
@router.get("/", response_model=list[RegistrationResponse])
def get_my_registrations(
    db: Session = Depends(get_db),
    current_user: User = Depends(jwt_token.get_current_user)
):
    current_user = db.query(User).filter(User.id == current_user.id).first()
    registrations = db.query(Registration).filter(Registration.user_id == current_user.id).all()
    return registrations
