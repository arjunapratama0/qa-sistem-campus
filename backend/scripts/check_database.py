from sqlalchemy import text

from app.infrastructure.db.session import SessionLocal


def main() -> None:
    db = SessionLocal()
    try:
        version = db.execute(text("select version()")).scalar_one()
        vector_available = db.execute(
            text("select exists(select 1 from pg_extension where extname = 'vector')")
        ).scalar_one()
        roles_count = db.execute(text("select count(*) from roles")).scalar_one()
        chunks_count = db.execute(text("select count(*) from document_chunks")).scalar_one()

        print("Database connection: OK")
        print(f"PostgreSQL: {version}")
        print(f"pgvector extension: {'OK' if vector_available else 'NOT INSTALLED'}")
        print(f"roles rows: {roles_count}")
        print(f"document_chunks rows: {chunks_count}")
    finally:
        db.close()


if __name__ == "__main__":
    main()

