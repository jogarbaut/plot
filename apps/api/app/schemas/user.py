from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    first_name: str
    last_name: str
    birthday: date


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    auth0_id: str
    email: str
    username: str
    first_name: str
    last_name: str
    birthday: date
    avatar_url: str | None
    created_at: datetime
    updated_at: datetime
