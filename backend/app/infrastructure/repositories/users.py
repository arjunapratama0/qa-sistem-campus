from uuid import UUID

from sqlalchemy.orm import Session, joinedload

from app.infrastructure.db.models import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).options(joinedload(User.role)).filter(User.email == email.lower()).first()

    def get_by_id(self, user_id: UUID) -> User | None:
        return self.db.query(User).options(joinedload(User.role)).filter(User.id == user_id).first()

    def create(self, full_name: str, email: str, password_hash: str, role_id: UUID) -> User:
        user = User(
            full_name=full_name.strip(),
            email=email.lower(),
            password_hash=password_hash,
            role_id=role_id,
        )
        self.db.add(user)
        self.db.flush()
        self.db.refresh(user)
        return user

