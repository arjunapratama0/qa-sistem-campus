import argparse
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.infrastructure.db.models import User
from app.infrastructure.db.session import SessionLocal
from app.infrastructure.repositories.roles import RoleRepository
from app.infrastructure.security.password import hash_password


def main() -> None:
    parser = argparse.ArgumentParser(description="Create or update the first admin account")
    parser.add_argument("--email", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--password", required=True)
    args = parser.parse_args()

    db = SessionLocal()
    try:
        roles = RoleRepository(db)
        admin_role = roles.get_by_name("admin")
        if not admin_role:
            raise RuntimeError("Admin role does not exist. Run apply_schema.py first.")

        user = db.query(User).filter(User.email == args.email.lower()).first()
        if user:
            user.full_name = args.name
            user.password_hash = hash_password(args.password)
            user.role_id = admin_role.id
            user.is_active = True
            action = "Updated"
        else:
            user = User(
                full_name=args.name,
                email=args.email.lower(),
                password_hash=hash_password(args.password),
                role_id=admin_role.id,
                is_active=True,
            )
            db.add(user)
            action = "Created"
        db.commit()
        print(f"{action} admin user: {args.email.lower()}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
