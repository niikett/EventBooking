import re
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator


class UserCreate(BaseModel):
    name: str
    department: str
    year: str
    role: str
    email: EmailStr
    password: str

    @field_validator("role")
    @classmethod
    def validate_role(cls, value):
        if value not in ["admin", "student"]:
            raise ValueError("user role can only be `admin` or `student`")
        
        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        errors = []

        if len(value) < 8:
            errors.append("at least 8 characters long")
        if not re.search(r"[A-Za-z]", value):
            errors.append("at least one letter")
        if not re.search(r"[0-9]", value):
            errors.append("at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            errors.append("at least one special character (e.g., !@#...)")

        if errors:
            raise ValueError("password must contain:\n" + "\n".join(errors))

        return value  


class UserResponse(BaseModel):
    id: UUID
    name: str
    role: str
    department: str
    year: str
    email: EmailStr


class UserUpdate(BaseModel):
    user_id: Optional[UUID] = None
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    contact: Optional[str] = None

    @field_validator("contact")
    @classmethod
    def validate_contact(cls, value):
        if value == "":
            return value
        str_val = str(value)
        if not str_val.isdigit() or len(str_val) != 10:
            raise ValueError("contact must contain exactly 10 digits")
        return value
