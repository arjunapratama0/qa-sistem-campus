from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.orm import Session, joinedload

from app.infrastructure.db.models import RefreshToken, User


class RefreshTokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: UUID, token_hash: str, expires_at: datetime) -> RefreshToken:
        refresh_token = RefreshToken(user_id=user_id, token_hash=token_hash, expires_at=expires_at)
        self.db.add(refresh_token)
        self.db.flush()
        return refresh_token

    def get_active_by_hash(self, token_hash: str) -> RefreshToken | None:
        now = datetime.now(UTC)
        return (
            self.db.query(RefreshToken)
            .options(joinedload(RefreshToken.user).joinedload(User.role))
            .filter(RefreshToken.token_hash == token_hash)
            .filter(RefreshToken.revoked_at.is_(None))
            .filter(RefreshToken.expires_at > now)
            .first()
        )

    def revoke(self, refresh_token: RefreshToken) -> None:
        refresh_token.revoked_at = datetime.now(UTC)
        self.db.flush()

    def revoke_all_for_user(self, user_id: UUID) -> None:
        (
            self.db.query(RefreshToken)
            .filter(RefreshToken.user_id == user_id)
            .filter(RefreshToken.revoked_at.is_(None))
            .update({RefreshToken.revoked_at: datetime.now(UTC)})
        )
        self.db.flush()
