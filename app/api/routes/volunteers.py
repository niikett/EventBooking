import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core import jwt_token
from app.models import Event, Registration, User
from app.core.config_db import get_db

router = APIRouter(
    prefix="/volunteers",
    tags=["volunteers"]
)


# -----------------------------
# Assign Volunteer Access (Admin only)
# -----------------------------
@router.post("/{event_id}/{student_id}", status_code=status.HTTP_200_OK)
def assign_volunteer(
    event_id: uuid.UUID,
    student_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(jwt_token.get_current_user)
):
    current_user = db.query(User).filter(User.id == current_user.id).first()
    event = db.query(Event).filter(Event.id == event_id).first()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    if current_user.role != "admin" or event.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Only the event's admin can assign volunteers")

    student = db.query(User).filter(User.id == student_id).first()
    if not student or student.role != "student":
        raise HTTPException(status_code=404, detail="Student not found")

    registration = db.query(Registration).filter(
        Registration.user_id == student_id,
        Registration.event_id == event_id
    ).first()
    if not registration:
        raise HTTPException(status_code=400, detail="Student is not registered for this event")

    if student_id not in event.volunteers:
        event.volunteers.append(student_id)

    db.commit()
    db.refresh(event)

    return {
        "detail": f"{student.name} assigned as volunteer for {event.title}",
        "volunteers": event.volunteers
    }


# -----------------------------
# De-Assign Volunteer Access (Admin only)
# -----------------------------
@router.delete("/{event_id}/{student_id}", status_code=status.HTTP_200_OK)
def remove_volunteer(
    event_id: uuid.UUID,
    student_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(jwt_token.get_current_user)
):
    current_user = db.query(User).filter(User.id == current_user.id).first()
    event = db.query(Event).filter(Event.id == event_id).first()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    if current_user.role != "admin" or event.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Only the event's admin can remove volunteers")

    if student_id not in event.volunteers:
        raise HTTPException(status_code=400, detail="Student is not a volunteer for this event")

    # remove from volunteers
    event.volunteers.remove(student_id)

    db.commit()
    db.refresh(event)

    return {
        "detail": f"Volunteer access removed for student {student_id} from {event.title}",
        "volunteers": event.volunteers
    }
