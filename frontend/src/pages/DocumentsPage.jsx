import { FileUp } from "lucide-react";
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
      <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-panel">
        <h1 className="text-2xl font-semibold text-campus-ink">Documents</h1>
        {error ? <p className="mt-4 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p> : null}
        <div className="mt-5 overflow-hidden rounded-lg border border-slate-200">
          <table className="w-full border-collapse text-left text-sm">
            <thead className="bg-slate-50 text-campus-muted">
              <tr>
                <th className="px-4 py-3 font-semibold">Title</th>
                <th className="px-4 py-3 font-semibold">Type</th>
                <th className="px-4 py-3 font-semibold">Chunks</th>
                <th className="px-4 py-3 font-semibold">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {documents.map((document) => (
                <tr key={document.id}>
                  <td className="px-4 py-3 font-medium text-campus-ink">{document.title}</td>
                  <td className="px-4 py-3 text-campus-muted">{document.source_type}</td>
                  <td className="px-4 py-3 text-campus-muted">{document.chunk_count}</td>
                  <td className="px-4 py-3 text-campus-muted">{document.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {!loading && !documents.length ? (
            <p className="border-t border-slate-200 px-4 py-4 text-sm text-campus-muted">No documents found.</p>
          ) : null}
        </div>
      </section>

      <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-panel">
        <h2 className="text-lg font-semibold text-campus-ink">Upload PDF source</h2>
        <form onSubmit={handleSubmit} className="mt-5 space-y-4">
          <input
            value={title}
            onChange={(event) => setTitle(event.target.value)}
            placeholder="Document title, optional"
            className="h-11 w-full rounded-md border border-slate-300 px-3 text-sm outline-none focus:border-campus-blue focus:ring-2 focus:ring-blue-100"
          />
          <input
            type="file"
            accept="application/pdf,.pdf"
            onChange={(event) => setFile(event.target.files?.[0] || null)}
            className="block w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-campus-muted file:mr-4 file:rounded-md file:border-0 file:bg-blue-50 file:px-3 file:py-2 file:text-sm file:font-semibold file:text-campus-blue"
            required
          />
          <p className="text-sm leading-6 text-campus-muted">
            PDF akan diekstrak, dipotong menjadi chunks, dibuat embedding dengan Jina, lalu tersimpan sebagai sumber QA.
          </p>
          <button
            type="submit"
            disabled={saving}
            className="inline-flex min-h-11 items-center gap-2 rounded-md bg-campus-blue px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:bg-slate-400"
          >
            <FileUp size={17} />
            {saving ? "Uploading..." : "Upload and embed"}
          </button>
        </form>
      </section>
    </div>
  );
}
