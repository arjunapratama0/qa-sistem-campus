from pydantic import BaseModel, EmailStr, Field, field_validator

from app.application.schemas.user import UserRead


class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=150)
    nim: str = Field(min_length=5, max_length=30)
    email: EmailStr | None = None
    password: str = Field(min_length=8, max_length=128)

    @field_validator("email", mode="before")
    @classmethod
    def empty_email_to_none(cls, value):
        if value == "":
            return None
        return value


class LoginRequest(BaseModel):
    identifier: str = Field(min_length=5, max_length=50)
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserRead


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(min_length=32)


class LogoutRequest(BaseModel):
    refresh_token: str = Field(min_length=32)
