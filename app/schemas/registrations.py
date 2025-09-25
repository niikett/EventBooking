from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class RegistrationBase(BaseModel):
    event_id: UUID


class RegistrationCreate(RegistrationBase):
    pass


class RegistrationResponse(BaseModel):
    id: UUID
    user_id: UUID
    event_id: UUID
    registered_at: datetime

    class Config:
        orm_mode = True
