from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class RoleRead(BaseModel):
    id: UUID
    name: str
    description: str | None = None

    model_config = {"from_attributes": True}


class UserRead(BaseModel):
    id: UUID
    full_name: str
    email: EmailStr
    is_active: bool
    role: RoleRead
    created_at: datetime

    model_config = {"from_attributes": True}

