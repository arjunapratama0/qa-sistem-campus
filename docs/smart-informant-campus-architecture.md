# Smart Informant Campus Architecture

## 1. High-Level Architecture

Smart Informant Campus is a retrieval-augmented question answering system for university students. The system is split into a React client, a FastAPI API, Supabase PostgreSQL with pgvector, and Jina Embeddings v3.

```text
React + Vite UI
  -> FastAPI REST API
    -> Auth/RBAC services
    -> QA service
    -> Document service
    -> History service
      -> Supabase PostgreSQL
        -> relational tables
        -> pgvector semantic index
      -> Jina Embeddings v3 API
```

The backend owns application rules and database access. The frontend only handles presentation, routing, local session state, and API calls. Supabase PostgreSQL stores users, roles, documents, chunks, embeddings, question history, and citations.

## 2. Component Diagram

```text
+------------------------+      +--------------------------+
| React Frontend         |      | FastAPI Backend          |
|------------------------|      |--------------------------|
| Landing/Login/Register | ---> | Auth Router              |
| Dashboard Layout       | ---> | QA Router                |
| Ask AI Page            | ---> | Documents Router         |
| History Page           | ---> | History Router           |
| Admin Dashboard        |      | Profile/User Router      |
+------------------------+      +------------+-------------+
                                             |
                     +-----------------------+----------------------+
                     |                                              |
          +----------v-----------+                       +----------v-----------+
          | Application Services |                       | Infrastructure       |
          |----------------------|                       |----------------------|
          | AuthService          |                       | SQLAlchemy Session   |
          | QAService            |                       | Repositories         |
          | DocumentService      |                       | JinaEmbeddingClient  |
          | HistoryService       |                       | JWT/Password Utils   |
          +----------+-----------+                       +----------+-----------+
                     |                                              |
                     +-----------------------+----------------------+
                                             |
                                  +----------v-----------+
                                  | Supabase PostgreSQL  |
                                  |----------------------|
                                  | users, roles         |
                                  | documents, chunks    |
                                  | vector embeddings    |
                                  | histories, citations |
                                  +----------------------+
```

## 3. Data Flow

Authentication flow:

1. User registers with name, email, password.
2. Backend hashes the password with bcrypt.
3. Backend assigns the default `student` role.
4. Login validates credentials and returns a signed JWT.
5. Frontend stores the token and sends `Authorization: Bearer <token>`.
6. Backend resolves the current user and role for protected requests.

Question answering flow:

1. Student submits a question from Ask AI.
2. Backend validates JWT and request payload.
3. Backend calls Jina Embeddings v3 using `retrieval.query`.
4. Backend searches `document_chunks.embedding` with cosine distance in pgvector.
5. Backend retrieves the top 5 chunks above the similarity threshold.
6. Backend creates a grounded answer from the retrieved context.
7. Backend stores question, answer, confidence score, and citations.
8. Frontend renders the answer, citations, and history entry.

Document ingestion flow:

1. Admin uploads or registers a campus document.
2. Backend extracts text and metadata.
3. Text is normalized and chunked.
4. Each chunk is embedded with Jina Embeddings v3 using `retrieval.passage`.
5. Document, chunks, and vectors are stored in Supabase PostgreSQL.
6. Vector indexes support fast semantic search.

## 4. Technology Justification

React + Vite:

- Fast development workflow and small build setup.
- Component model suits dashboard, forms, chat-like QA, and admin views.
- Works well with TailwindCSS for consistent responsive layouts.

FastAPI:

- Strong async API support and automatic OpenAPI documentation.
- Pydantic validation keeps API contracts explicit.
- Dependency injection maps cleanly to JWT auth, RBAC, sessions, and services.

Supabase PostgreSQL:

- Managed PostgreSQL with SQL-native relational integrity.
- pgvector enables semantic search without introducing a second vector database.
- Row-level security can be enabled later for defense in depth.

Jina Embeddings v3:

- Designed for retrieval use cases with explicit query and passage tasks.
- Multilingual support is valuable for Indonesian campus documents.
- Embeddings can be stored directly in pgvector and queried by cosine similarity.

Clean Architecture:

- Routers stay thin and framework-specific.
- Services hold business rules.
- Repositories isolate database persistence.
- Infrastructure clients isolate Jina, JWT, password hashing, and SQLAlchemy.

## Production Project Structure

```text
qa-sistem/
  backend/
    app/
      api/
        routers/
      application/
        schemas/
        services/
      core/
      domain/
      infrastructure/
        db/
        repositories/
        security/
        external/
    migrations/
    main.py
    requirements.txt
  frontend/
    src/
      api/
      components/
      contexts/
      layouts/
      pages/
      routes/
      styles/
    package.json
  docs/
```

Backend responsibilities:

- `api/routers`: HTTP endpoints and dependency wiring.
- `application/services`: use cases such as register, login, ask question, store history.
- `application/schemas`: request and response DTOs.
- `domain`: business entities, enums, and repository protocols.
- `infrastructure/db`: SQLAlchemy engine, session, models, schema SQL.
- `infrastructure/repositories`: PostgreSQL implementations of repository contracts.
- `infrastructure/security`: JWT, password hashing, and auth dependencies.
- `infrastructure/external`: Jina client and future third-party integrations.

Frontend responsibilities:

- `api`: API client and typed endpoint functions.
- `components`: reusable UI components.
- `contexts`: auth/session state.
- `layouts`: dashboard shell, navbar, sidebar.
- `pages`: route-level screens.
- `routes`: route guards and route definitions.
- `styles`: Tailwind entry and shared styling.

## Database Design

ERD:

```text
roles 1---* users
users 1---* documents
documents 1---* document_chunks
users 1---* question_histories
question_histories 1---* citations
document_chunks 1---* citations
```

Tables:

- `roles`: role catalog: `student`, `admin`, `staff`.
- `users`: authenticated users with hashed passwords and role assignment.
- `documents`: campus source documents and metadata.
- `document_chunks`: searchable text chunks with pgvector embeddings.
- `question_histories`: questions, generated answers, confidence score, and requester.
- `citations`: links each answer to the chunks used as evidence.
- `audit_logs`: security and operational events.

Recommended indexes:

- `users.email` unique btree.
- `roles.name` unique btree.
- `documents.created_by`, `documents.status`.
- `document_chunks.document_id`.
- `document_chunks.embedding vector_cosine_ops` using HNSW.
- `question_histories.user_id, created_at desc`.
- `citations.question_history_id`.
- `audit_logs.actor_user_id, created_at desc`.

## PostgreSQL Schema

```sql
create extension if not exists vector;
create extension if not exists pgcrypto;

create table roles (
  id uuid primary key default gen_random_uuid(),
  name varchar(50) not null unique,
  description text,
  created_at timestamptz not null default now()
);

create table users (
  id uuid primary key default gen_random_uuid(),
  role_id uuid not null references roles(id),
  full_name varchar(150) not null,
  email varchar(255) not null unique,
  password_hash text not null,
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table documents (
  id uuid primary key default gen_random_uuid(),
  created_by uuid references users(id),
  title varchar(255) not null,
  source_type varchar(50) not null default 'manual',
  source_url text,
  file_name varchar(255),
  status varchar(30) not null default 'active',
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table document_chunks (
  id uuid primary key default gen_random_uuid(),
  document_id uuid not null references documents(id) on delete cascade,
  chunk_index int not null,
  content text not null,
  page_number int,
  section_title varchar(255),
  token_count int not null default 0,
  embedding vector(1024) not null,
  created_at timestamptz not null default now(),
  unique(document_id, chunk_index)
);

create table question_histories (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references users(id) on delete cascade,
  question text not null,
  answer text not null,
  confidence_score numeric(5,4) not null default 0,
  created_at timestamptz not null default now()
);

create table citations (
  id uuid primary key default gen_random_uuid(),
  question_history_id uuid not null references question_histories(id) on delete cascade,
  document_chunk_id uuid not null references document_chunks(id),
  rank int not null,
  similarity_score numeric(6,5) not null,
  quote text not null,
  created_at timestamptz not null default now()
);

create table audit_logs (
  id uuid primary key default gen_random_uuid(),
  actor_user_id uuid references users(id),
  action varchar(100) not null,
  resource_type varchar(100),
  resource_id uuid,
  ip_address inet,
  user_agent text,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index idx_documents_created_by on documents(created_by);
create index idx_documents_status on documents(status);
create index idx_chunks_document_id on document_chunks(document_id);
create index idx_chunks_embedding_hnsw on document_chunks using hnsw (embedding vector_cosine_ops);
create index idx_histories_user_created on question_histories(user_id, created_at desc);
create index idx_citations_history on citations(question_history_id);
create index idx_audit_actor_created on audit_logs(actor_user_id, created_at desc);

insert into roles(name, description)
values
  ('student', 'Default student user'),
  ('staff', 'Campus staff document manager'),
  ('admin', 'System administrator')
on conflict(name) do nothing;
```

## Backend API Architecture

Router structure:

- `/api/v1/auth/register`
- `/api/v1/auth/login`
- `/api/v1/auth/me`
- `/api/v1/qa/ask`
- `/api/v1/history`
- `/api/v1/documents`
- `/api/v1/admin/*`

Service structure:

- `AuthService`: register, login, token subject construction.
- `QAService`: embed question, retrieve chunks, calculate confidence, store history.
- `DocumentService`: create documents, chunk content, generate passage embeddings.
- `HistoryService`: list user history and citation details.

Repository structure:

- `UserRepository`: find by email/id, create user.
- `RoleRepository`: find default and named roles.
- `DocumentRepository`: create/list documents and chunks.
- `ChunkRepository`: vector search with pgvector cosine similarity.
- `QuestionHistoryRepository`: persist questions and citations.

Middleware structure:

- CORS for frontend origin.
- Trusted host in production.
- Request logging and correlation id.
- Rate limiting at API gateway/reverse proxy, with app-level fallback for auth and QA endpoints.

## Frontend Architecture

Pages:

- Landing Page
- Login
- Register
- Dashboard
- Ask AI
- Question History
- Documents
- Profile
- Admin Dashboard

Component hierarchy:

```text
App
  AuthProvider
  AppRouter
    PublicRoute
      LandingPage
      LoginPage
      RegisterPage
    ProtectedRoute
      DashboardLayout
        Navbar
        Sidebar
        DashboardPage
        AskAIPage
        HistoryPage
        DocumentsPage
        ProfilePage
        AdminDashboardPage
```

State management:

- Auth state in React Context.
- Server calls via a small API client.
- Page-local state for forms, loading, and errors.
- Future production upgrade: TanStack Query for caching and retries.

UI layout:

- Public pages use a full-height split composition with auth forms.
- App pages use a fixed sidebar on desktop and compact top navigation on mobile.
- Ask AI uses a two-column desktop layout: question input and answer/citations.
- Admin and dashboard pages use dense operational cards, tables, and status rows.

## Question Answering Pipeline

Document ingestion:

1. Validate admin/staff access.
2. Extract text from PDF, DOCX, or manual input.
3. Normalize whitespace, remove repeated headers/footers where possible.
4. Split into chunks.
5. Generate embeddings with Jina v3 using `task: retrieval.passage`.
6. Store document metadata, chunk content, and vector embeddings.

Chunking strategy:

- Target 500-800 tokens per chunk.
- 80-120 token overlap to preserve context across boundaries.
- Keep page number, section title, and chunk index as citation metadata.
- Do not mix unrelated document sections inside one chunk.

Embedding generation:

- Model: `jina-embeddings-v3`.
- Dimensions: 1024.
- Query task: `retrieval.query`.
- Passage task: `retrieval.passage`.
- Store vectors in `document_chunks.embedding`.

Retrieval flow:

1. Embed question.
2. Run cosine similarity search with pgvector.
3. Retrieve top 5 chunks.
4. Apply a minimum similarity threshold.
5. Build answer from the most relevant chunks.

Citation generation:

- Each citation records chunk id, document title, page, rank, similarity, and quote.
- The answer should only include facts present in retrieved chunks.
- If no chunk clears the threshold, return an insufficient-context answer.

Confidence score:

- Convert cosine distance to similarity: `similarity = 1 - distance`.
- Weighted formula:
  - 70% top similarity.
  - 20% average top-k similarity.
  - 10% retrieval coverage, capped by number of usable chunks.
- Store a numeric value from `0.0000` to `1.0000`.

## Security Review

Authentication:

- Email and password login.
- Passwords are never stored in plaintext.
- JWT access tokens are short-lived and signed with a strong secret.

Authorization:

- RBAC roles: `student`, `staff`, `admin`.
- Students can ask questions and view their own history.
- Staff can manage documents.
- Admin can manage documents and users.

JWT strategy:

- Use `sub`, `email`, `role`, `exp`, `iat`, and `type`.
- Keep token lifetime short, default 60 minutes.
- Use HTTPS only in production.
- Store refresh tokens later as opaque, revocable server-side records.

Password hashing:

- Use bcrypt via Passlib.
- Enforce minimum password length.
- Consider breached password screening before production launch.

API protection:

- Validate all payloads with Pydantic.
- Use RBAC dependencies on restricted routes.
- Limit CORS to configured frontend origins.
- Disable debug errors in production.

SQL injection protection:

- Use SQLAlchemy ORM and parameterized `text()` queries.
- Never concatenate untrusted user input into SQL.
- Vector literals are constructed from numeric embedding output only.

XSS protection:

- React escapes rendered text by default.
- Do not render answer markdown as raw HTML unless sanitized.
- Add CSP headers at the reverse proxy.

Rate limiting:

- Rate-limit `/auth/login`, `/auth/register`, and `/qa/ask`.
- Prefer edge/proxy limits in production.
- Add app-level limits with Redis if deployed horizontally.

Audit logging:

- Log login success/failure, document changes, role changes, and QA usage.
- Store actor, action, resource, request IP, user agent, and timestamp.
- Do not log passwords or full JWTs.

