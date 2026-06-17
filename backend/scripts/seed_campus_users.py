from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.infrastructure.db.models import User
from app.infrastructure.db.session import SessionLocal
from app.infrastructure.repositories.roles import RoleRepository
from app.infrastructure.security.password import hash_password


def upsert_user(db, *, full_name, email, identifier, identity_type, role_name, password, nim=None, nip=None):
    role = RoleRepository(db).get_by_name(role_name)
    if not role:
        raise RuntimeError(f"Role not found: {role_name}. Run apply_schema.py first.")

    user = db.query(User).filter(User.login_identifier == identifier.lower()).first()
    if not user:
        user = db.query(User).filter(User.email == email.lower()).first()

    if user:
        user.full_name = full_name
        user.email = email.lower()
        user.login_identifier = identifier.lower()
        user.identity_type = identity_type
        user.nim = nim
        user.nip = nip
        user.password_hash = hash_password(password)
        user.role_id = role.id
        user.is_active = True
        action = "Updated"
    else:
        user = User(
            full_name=full_name,
            email=email.lower(),
            login_identifier=identifier.lower(),
            identity_type=identity_type,
            nim=nim,
            nip=nip,
            password_hash=hash_password(password),
            role_id=role.id,
            is_active=True,
        )
        db.add(user)
        action = "Created"

    db.flush()
    print(f"{action}: {identity_type} {identifier}")


def main() -> None:
    db = SessionLocal()
    try:
        upsert_user(
            db,
            full_name="Arjuna Pratama",
            email="2305551000@student.smart-campus.id",
            identifier="2305551000",
            identity_type="student",
            role_name="student",
            password="Arjuna123",
            nim="2305551000",
        )
        upsert_user(
            db,
            full_name="Pegawai Tata Usaha",
            email="197000000000000000@staff.smart-campus.id",
            identifier="197000000000000000",
            identity_type="staff",
            role_name="admin",
            password="Admin123",
            nip="197000000000000000",
        )
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    main()
