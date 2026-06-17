# Cara Menjalankan Smart Informant Campus

Panduan ini diasumsikan dijalankan dari folder:

```powershell
C:\Users\PC\Downloads\TUGAS AKHIR SKRIPSI\qa-sistem
```

## 1. Siapkan Supabase

1. Buka Supabase SQL Editor.
2. Jalankan isi file:

```text
backend/app/infrastructure/db/schema.sql
```

Schema ini membuat tabel `roles`, `users`, `documents`, `document_chunks`, `question_histories`, `citations`, `audit_logs`, dan index pgvector.

## 2. Siapkan Backend Environment

```powershell
cd "C:\Users\PC\Downloads\TUGAS AKHIR SKRIPSI\qa-sistem\backend"
copy .env.example .env
```

Isi `.env`:

```env
DATABASE_URL=postgresql+psycopg://postgres.ofdjfpwfvkryhfmchssq:SUPABASE_PASSWORD@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres?sslmode=require
JWT_SECRET_KEY=ganti-dengan-secret-panjang
FRONTEND_ORIGIN=http://localhost:5173
JINA_API_KEY=ganti-dengan-jina-api-key
LLM_PROVIDER=groq
GROQ_API_KEY=ganti-dengan-groq-api-key
GROQ_MODEL=llama-3.1-8b-instant
```

Install dependency backend:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

Kalau ingin menjalankan schema dari terminal:

```powershell
.\venv\Scripts\python.exe scripts\apply_schema.py
```

Cek koneksi database:

```powershell
.\venv\Scripts\python.exe scripts\check_database.py
```

Cek retrieval Jina + pgvector:

```powershell
.\venv\Scripts\python.exe scripts\smoke_retrieval.py --question "Berapa maksimal SKS jika IPS 3.6?"
```

Jalankan test suite:

```powershell
.\venv\Scripts\python.exe -m pytest
```

## 3. Import Data RAG

Project sudah memiliki:

- `backend/data/chunks.json` berisi 1.199 chunks
- `backend/data/qa_dataset_rag.json` berisi 121 contoh pertanyaan

Import semua chunks ke Supabase pgvector:

```powershell
.\venv\Scripts\python.exe scripts\import_chunks.py --replace
```

Untuk tes kecil dulu:

```powershell
.\venv\Scripts\python.exe scripts\import_chunks.py --replace --limit 5
```

## 4. Jalankan Backend

```powershell
cd "C:\Users\PC\Downloads\TUGAS AKHIR SKRIPSI\qa-sistem\backend"
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Backend berjalan di:

```text
http://127.0.0.1:8000
```

API docs:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
http://127.0.0.1:8000/health
```

## 5. Jalankan Frontend

Buka terminal baru:

```powershell
cd "C:\Users\PC\Downloads\TUGAS AKHIR SKRIPSI\qa-sistem\frontend"
copy .env.example .env
npm.cmd install
npm.cmd run dev
```

Frontend berjalan di:

```text
http://127.0.0.1:5173
```

## 6. Urutan Tes Aplikasi

1. Buka frontend.
2. Register user baru.
3. Login.
4. Masuk ke halaman Ask AI.
5. Klik contoh pertanyaan atau ketik pertanyaan sendiri.
6. Sistem akan:
   - membuat embedding pertanyaan memakai Jina,
   - mencari top 5 chunks di Supabase pgvector,
   - membuat jawaban dengan Groq jika `GROQ_API_KEY` tersedia,
   - fallback ke jawaban extractive jika Groq belum dikonfigurasi,
   - menampilkan citations,
   - menyimpan question history.

## Upload PDF Admin

Admin/staff memperbarui data hanya lewat upload PDF di halaman Documents.

Pipeline upload:

1. Validasi file PDF.
2. Ekstraksi teks memakai `pypdf`.
3. Ekstraksi tabel memakai `pdfplumber`.
4. Halaman yang hanya gambar/scanned ditandai `needs_ocr` di metadata.
5. Teks dan tabel dipotong menjadi chunks dengan overlap.
6. Chunks dibuat embedding dengan Jina.
7. Chunks disimpan ke Supabase dengan metadata sumber, halaman, tabel, dan citation support.

## Troubleshooting

Jika register/login gagal:

- Pastikan `DATABASE_URL` benar.
- Jika password Supabase berisi karakter khusus seperti `@`, `#`, `/`, atau `:`, encode dulu password untuk URL.
- Pastikan schema SQL sudah dijalankan di Supabase.
- Pastikan tabel `roles` berisi `student`, `staff`, dan `admin`.

Jika Ask AI gagal:

- Pastikan `JINA_API_KEY` benar.
- Pastikan `scripts/import_chunks.py` sudah dijalankan.
- Pastikan tabel `document_chunks` sudah terisi dan punya embedding.
- Jika jawaban LLM tidak muncul, pastikan `GROQ_API_KEY` benar. Tanpa Groq, sistem tetap menjawab dari chunk sumber.

Jika request API ditolak oleh host:

- Tambahkan host backend ke `TRUSTED_HOSTS`.
- Untuk lokal, nilai aman adalah `localhost,127.0.0.1,testserver`.

Jika `npm` gagal di PowerShell:

Gunakan:

```powershell
npm.cmd run dev
```

bukan:

```powershell
npm run dev
```
