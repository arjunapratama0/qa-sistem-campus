create extension if not exists vector;
create extension if not exists pgcrypto;

create table if not exists roles (
  id uuid primary key default gen_random_uuid(),
  name varchar(50) not null unique,
  description text,
  created_at timestamptz not null default now()
);

create table if not exists users (
  id uuid primary key default gen_random_uuid(),
  role_id uuid not null references roles(id),
  full_name varchar(150) not null,
  email varchar(255) not null unique,
  password_hash text not null,
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists refresh_tokens (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references users(id) on delete cascade,
  token_hash text not null unique,
  expires_at timestamptz not null,
  revoked_at timestamptz,
  created_at timestamptz not null default now()
);

create table if not exists documents (
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

create table if not exists document_chunks (
  id uuid primary key default gen_random_uuid(),
  document_id uuid not null references documents(id) on delete cascade,
  chunk_index int not null,
  content text not null,
  page_number int,
  section_title text,
  source_chunk_id varchar(255),
  metadata jsonb not null default '{}'::jsonb,
  token_count int not null default 0,
  embedding vector(1024) not null,
  created_at timestamptz not null default now(),
  unique(document_id, chunk_index)
);

alter table if exists document_chunks
  alter column section_title type text;

alter table if exists document_chunks
  add column if not exists source_chunk_id varchar(255);

alter table if exists document_chunks
  add column if not exists metadata jsonb not null default '{}'::jsonb;

create table if not exists question_histories (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references users(id) on delete cascade,
  question text not null,
  answer text not null,
  confidence_score numeric(5,4) not null default 0,
  created_at timestamptz not null default now()
);

create table if not exists citations (
  id uuid primary key default gen_random_uuid(),
  question_history_id uuid not null references question_histories(id) on delete cascade,
  document_chunk_id uuid not null references document_chunks(id),
  rank int not null,
  similarity_score numeric(6,5) not null,
  quote text not null,
  created_at timestamptz not null default now()
);

create table if not exists audit_logs (
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

create index if not exists idx_documents_created_by on documents(created_by);
create index if not exists idx_documents_status on documents(status);
create index if not exists idx_refresh_tokens_user on refresh_tokens(user_id);
create index if not exists idx_refresh_tokens_hash on refresh_tokens(token_hash);
create index if not exists idx_chunks_document_id on document_chunks(document_id);
create index if not exists idx_chunks_source_chunk_id on document_chunks(source_chunk_id);
create index if not exists idx_chunks_embedding_hnsw on document_chunks using hnsw (embedding vector_cosine_ops);
create index if not exists idx_histories_user_created on question_histories(user_id, created_at desc);
create index if not exists idx_citations_history on citations(question_history_id);
create index if not exists idx_audit_actor_created on audit_logs(actor_user_id, created_at desc);

insert into roles(name, description)
values
  ('student', 'Default student user'),
  ('staff', 'Campus staff document manager'),
  ('admin', 'System administrator')
on conflict(name) do nothing;
