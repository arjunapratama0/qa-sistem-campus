# Smart Informant Campus

AI-powered question answering system for university students.

## Architecture

The full system design, ERD, PostgreSQL schema, API architecture, frontend architecture, QA pipeline, and security review are in:

- `docs/smart-informant-campus-architecture.md`
- `docs/cara-menjalankan.md`

## Backend

```powershell
cd backend
copy .env.example .env
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Apply the database schema in Supabase SQL editor:

- `backend/app/infrastructure/db/schema.sql`

Import the provided document chunks into pgvector after configuring `DATABASE_URL` and `JINA_API_KEY`:

```powershell
.\venv\Scripts\python.exe scripts\import_chunks.py --replace
```

Verify database and retrieval:

```powershell
.\venv\Scripts\python.exe scripts\check_database.py
.\venv\Scripts\python.exe scripts\smoke_retrieval.py
```

For a small smoke test import:

```powershell
.\venv\Scripts\python.exe scripts\import_chunks.py --replace --limit 5
```

Required environment variables:

- `DATABASE_URL`
- `JWT_SECRET_KEY`
- `FRONTEND_ORIGIN`
- `JINA_API_KEY`

## GitHub

Remote repository:

```text
https://github.com/arjunapratama0/qa-sistem-campus.git
```

Push pertama:

```powershell
git add .
git commit -m "Initial Smart Informant Campus implementation"
git push -u origin main
```

## Frontend

```powershell
cd frontend
copy .env.example .env
npm.cmd install
npm.cmd run dev
```

Default local URLs:

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
