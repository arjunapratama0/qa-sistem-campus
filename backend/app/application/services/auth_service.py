from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.application.schemas.auth import LoginRequest, RefreshTokenRequest, RegisterRequest, TokenResponse
from app.core.config import get_settings
from app.infrastructure.repositories.roles import RoleRepository
from app.infrastructure.repositories.tokens import RefreshTokenRepository
from app.infrastructure.repositories.users import UserRepository
from app.infrastructure.security.jwt import create_access_token
from app.infrastructure.security.password import hash_password, verify_password
from app.infrastructure.security.tokens import create_opaque_token, hash_token

settings = get_settings()


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)
        self.roles = RoleRepository(db)
        self.refresh_tokens = RefreshTokenRepository(db)

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

        response = self._create_token_response(user)
        self.db.commit()
        return response

    def login(self, payload: LoginRequest) -> TokenResponse:
        user = self.users.get_by_email(str(payload.email))
        if not user or not verify_password(payload.password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive")

        response = self._create_token_response(user)
        self.db.commit()
        return response

    def refresh(self, payload: RefreshTokenRequest) -> TokenResponse:
        token_hash = hash_token(payload.refresh_token)
        stored_token = self.refresh_tokens.get_active_by_hash(token_hash)
        if not stored_token or not stored_token.user or not stored_token.user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        self.refresh_tokens.revoke(stored_token)
        response = self._create_token_response(stored_token.user)
        self.db.commit()
        return response

    def logout(self, refresh_token: str) -> None:
        stored_token = self.refresh_tokens.get_active_by_hash(hash_token(refresh_token))
        if stored_token:
            self.refresh_tokens.revoke(stored_token)
            self.db.commit()

    def _create_token_response(self, user) -> TokenResponse:
        access_token = create_access_token(str(user.id), {"email": user.email, "role": user.role.name})
        refresh_token = create_opaque_token()
        expires_at = datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days)
        self.refresh_tokens.create(user.id, hash_token(refresh_token), expires_at)
        return TokenResponse(access_token=access_token, refresh_token=refresh_token, user=user)
