from pathlib import Path
import sys

from sqlalchemy import text

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.infrastructure.db.session import SessionLocal


SCHEMA_PATH = Path(__file__).resolve().parents[1] / "app" / "infrastructure" / "db" / "schema.sql"


def main() -> None:
    sql = SCHEMA_PATH.read_text(encoding="utf-8")
    statements = [statement.strip() for statement in sql.split(";") if statement.strip()]

    db = SessionLocal()
    try:
        for statement in statements:
            db.execute(text(statement))
        db.commit()
        print(f"Applied schema from {SCHEMA_PATH}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
