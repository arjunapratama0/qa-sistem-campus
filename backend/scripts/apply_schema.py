from pathlib import Path

from sqlalchemy import text

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

