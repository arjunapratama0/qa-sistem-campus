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
    login_identifier: str | None = None
    identity_type: str
    nim: str | None = None
    nip: str | None = None
    is_active: bool
    role: RoleRead
    created_at: datetime

    model_config = {"from_attributes": True}
