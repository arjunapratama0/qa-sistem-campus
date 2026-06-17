from uuid import UUID

from sqlalchemy.orm import Session, joinedload

from app.infrastructure.db.models import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).options(joinedload(User.role)).filter(User.email == email.lower()).first()

    def get_by_identifier(self, identifier: str) -> User | None:
        normalized = identifier.strip().lower()
        return (
            self.db.query(User)
            .options(joinedload(User.role))
            .filter(User.login_identifier == normalized)
            .first()
        )

    def get_by_id(self, user_id: UUID) -> User | None:
        return self.db.query(User).options(joinedload(User.role)).filter(User.id == user_id).first()

    def create(
        self,
        full_name: str,
        email: str,
        password_hash: str,
        role_id: UUID,
        login_identifier: str,
        identity_type: str = "student",
        nim: str | None = None,
        nip: str | None = None,
    ) -> User:
        user = User(
            full_name=full_name.strip(),
            email=email.lower(),
            login_identifier=login_identifier.strip().lower(),
            identity_type=identity_type,
            nim=nim,
            nip=nip,
            password_hash=password_hash,
            role_id=role_id,
        )
        self.db.add(user)
        self.db.flush()
        self.db.refresh(user)
        return user
