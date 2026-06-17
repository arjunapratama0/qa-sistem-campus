from sqlalchemy.orm import Session

from app.infrastructure.db.models import Role


class RoleRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_name(self, name: str) -> Role | None:
        return self.db.query(Role).filter(Role.name == name).first()

    def get_default_student_role(self) -> Role:
        role = self.get_by_name("student")
        if role:
            return role

        role = Role(name="student", description="Default student user")
        self.db.add(role)
        self.db.flush()
        return role

