from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.application.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.infrastructure.repositories.roles import RoleRepository
from app.infrastructure.repositories.users import UserRepository
from app.infrastructure.security.jwt import create_access_token
from app.infrastructure.security.password import hash_password, verify_password


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)
        self.roles = RoleRepository(db)

    def register(self, payload: RegisterRequest) -> TokenResponse:
        if self.users.get_by_email(payload.email):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is already registered")

        role = self.roles.get_default_student_role()
        user = self.users.create(
            full_name=payload.full_name,
            email=str(payload.email),
            password_hash=hash_password(payload.password),
            role_id=role.id,
        )
        self.db.commit()
        self.db.refresh(user)

        token = create_access_token(str(user.id), {"email": user.email, "role": user.role.name})
        return TokenResponse(access_token=token, user=user)

    def login(self, payload: LoginRequest) -> TokenResponse:
        user = self.users.get_by_email(str(payload.email))
        if not user or not verify_password(payload.password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive")

        token = create_access_token(str(user.id), {"email": user.email, "role": user.role.name})
        return TokenResponse(access_token=token, user=user)

