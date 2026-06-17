import { FileText, FileUp, Loader2, RefreshCw } from "lucide-react";
import { useEffect, useState } from "react";
import { getDocuments, uploadDocumentPdf } from "../api/documents.js";

export default function DocumentsPage() {
  const [documents, setDocuments] = useState([]);
  const [title, setTitle] = useState("");
  const [file, setFile] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  async function loadDocuments() {
    setLoading(true);
    try {
      const data = await getDocuments();
      setDocuments(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    let active = true;

    getDocuments()
      .then((data) => {
        if (active) {
          setDocuments(data);
        }
      })
      .catch((err) => {
        if (active) {
          setError(err.message);
        }
      })
      .finally(() => {
        if (active) {
          setLoading(false);
        }
      });

    return () => {
      active = false;
    };
  }, []);

  async function handleSubmit(event) {
    event.preventDefault();
    if (!file) {
      setError("Please choose a PDF file.");
      return;
    }
    setError("");
    setSaving(true);
    try {
      await uploadDocumentPdf({ file, title });
      setTitle("");
      setFile(null);
      event.currentTarget.reset();
      await loadDocuments();
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="mx-auto grid max-w-6xl gap-6 xl:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)]">
      <section className="premium-panel p-5">
        <div className="flex items-center justify-between gap-3">
          <div>
            <p className="text-sm font-semibold uppercase tracking-wide text-campus-blue dark:text-campus-gold">Knowledge Base</p>
            <h1 className="mt-1 text-2xl font-bold text-campus-ink dark:text-white">Dokumen Akademik</h1>
            <p className="mt-1 text-sm text-campus-muted dark:text-slate-400">Sumber yang dipakai untuk pencarian semantik dan citation.</p>
          </div>
          <button
            type="button"
            onClick={loadDocuments}
            className="inline-flex h-10 w-10 items-center justify-center rounded-xl border border-slate-200 text-campus-muted transition hover:bg-slate-100 dark:border-white/10 dark:text-slate-300 dark:hover:bg-white/10"
            aria-label="Refresh documents"
            title="Refresh documents"
          >
            <RefreshCw size={17} />
          </button>
        </div>
        {error ? <p className="mt-4 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p> : null}
        <div className="mt-5 overflow-hidden rounded-2xl border border-slate-200 dark:border-white/10">
          <table className="w-full border-collapse text-left text-sm">
            <thead className="bg-slate-50 text-campus-muted dark:bg-white/5 dark:text-slate-400">
              <tr>
                <th className="px-4 py-3 font-semibold">Title</th>
                <th className="px-4 py-3 font-semibold">Type</th>
                <th className="px-4 py-3 font-semibold">Chunks</th>
                <th className="px-4 py-3 font-semibold">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 dark:divide-white/10">
              {documents.map((document) => (
                <tr key={document.id} className="bg-white/70 dark:bg-transparent">
                  <td className="px-4 py-3 font-medium text-campus-ink dark:text-white">{document.title}</td>
                  <td className="px-4 py-3 text-campus-muted dark:text-slate-400">{document.source_type}</td>
                  <td className="px-4 py-3 text-campus-muted dark:text-slate-400">{document.chunk_count}</td>
                  <td className="px-4 py-3">
                    <span className="rounded-full bg-campus-green/10 px-2 py-1 text-xs font-semibold text-campus-green dark:bg-campus-gold/15 dark:text-campus-gold">
                      {document.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {loading ? (
            <div className="space-y-3 border-t border-slate-200 p-4 dark:border-white/10">
              <div className="skeleton-line h-4 w-3/4" />
              <div className="skeleton-line h-4 w-2/3" />
              <div className="skeleton-line h-4 w-1/2" />
            </div>
          ) : null}
          {!loading && !documents.length ? (
            <p className="border-t border-slate-200 px-4 py-4 text-sm text-campus-muted dark:border-white/10 dark:text-slate-400">No documents found.</p>
          ) : null}
        </div>
      </section>

      <section className="premium-panel p-5">
        <div className="rounded-2xl bg-campus-navy p-5 text-white">
          <FileText className="text-campus-gold" size={24} />
          <h2 className="mt-3 text-xl font-bold">Upload PDF Tata Usaha</h2>
          <p className="mt-2 text-sm leading-6 text-blue-50">
            PDF teks dan tabel akan diekstrak, dipotong menjadi chunks, lalu dibuat embedding otomatis.
          </p>
        </div>
        <form onSubmit={handleSubmit} className="mt-5 space-y-4">
          <input
            value={title}
            onChange={(event) => setTitle(event.target.value)}
            placeholder="Document title, optional"
            className="field-control h-12 w-full"
          />
          <input
            type="file"
            accept="application/pdf,.pdf"
            onChange={(event) => setFile(event.target.files?.[0] || null)}
            className="block w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm text-campus-muted file:mr-4 file:rounded-lg file:border-0 file:bg-blue-50 file:px-3 file:py-2 file:text-sm file:font-semibold file:text-campus-blue dark:border-white/10 dark:bg-white/5 dark:text-slate-300 dark:file:bg-campus-gold/15 dark:file:text-campus-gold"
            required
          />
          <p className="text-sm leading-6 text-campus-muted dark:text-slate-400">
            PDF akan diekstrak, dipotong menjadi chunks, dibuat embedding dengan Jina, lalu tersimpan sebagai sumber QA.
          </p>
          <button
            type="submit"
            disabled={saving}
            className="inline-flex min-h-11 items-center gap-2 rounded-xl bg-campus-blue px-5 py-2 text-sm font-semibold text-white shadow-panel transition hover:-translate-y-0.5 hover:bg-campus-navy disabled:translate-y-0 disabled:bg-slate-400"
          >
            {saving ? <Loader2 className="animate-spin" size={17} /> : <FileUp size={17} />}
            {saving ? "Uploading..." : "Upload and embed"}
          </button>
        </form>
      </section>
    </div>
  );
}
