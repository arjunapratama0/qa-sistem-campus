import { Plus } from "lucide-react";
import { useEffect, useState } from "react";
import { createDocument, getDocuments } from "../api/documents.js";

const emptyForm = {
  title: "",
  source_type: "manual",
  source_url: "",
  file_name: "",
  chunks: [{ content: "", page_number: "", section_title: "" }],
};

export default function DocumentsPage() {
  const [documents, setDocuments] = useState([]);
  const [form, setForm] = useState(emptyForm);
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

  function updateChunk(index, key, value) {
    const chunks = form.chunks.map((chunk, currentIndex) =>
      currentIndex === index ? { ...chunk, [key]: value } : chunk,
    );
    setForm({ ...form, chunks });
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setSaving(true);
    try {
      const payload = {
        ...form,
        source_url: form.source_url || null,
        file_name: form.file_name || null,
        chunks: form.chunks.map((chunk) => ({
          ...chunk,
          page_number: chunk.page_number ? Number(chunk.page_number) : null,
        })),
      };
      await createDocument(payload);
      setForm(emptyForm);
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
        <h2 className="text-lg font-semibold text-campus-ink">Add source document</h2>
        <form onSubmit={handleSubmit} className="mt-5 space-y-4">
          <input
            value={form.title}
            onChange={(event) => setForm({ ...form, title: event.target.value })}
            placeholder="Document title"
            className="h-11 w-full rounded-md border border-slate-300 px-3 text-sm outline-none focus:border-campus-blue focus:ring-2 focus:ring-blue-100"
            required
          />
          <textarea
            value={form.chunks[0].content}
            onChange={(event) => updateChunk(0, "content", event.target.value)}
            placeholder="Document text chunk"
            className="min-h-36 w-full rounded-md border border-slate-300 p-3 text-sm outline-none focus:border-campus-blue focus:ring-2 focus:ring-blue-100"
            required
          />
          <div className="grid gap-3 sm:grid-cols-2">
            <input
              value={form.chunks[0].section_title}
              onChange={(event) => updateChunk(0, "section_title", event.target.value)}
              placeholder="Section title"
              className="h-11 rounded-md border border-slate-300 px-3 text-sm outline-none focus:border-campus-blue focus:ring-2 focus:ring-blue-100"
            />
            <input
              type="number"
              value={form.chunks[0].page_number}
              onChange={(event) => updateChunk(0, "page_number", event.target.value)}
              placeholder="Page"
              className="h-11 rounded-md border border-slate-300 px-3 text-sm outline-none focus:border-campus-blue focus:ring-2 focus:ring-blue-100"
            />
          </div>
          <button
            type="submit"
            disabled={saving}
            className="inline-flex min-h-11 items-center gap-2 rounded-md bg-campus-blue px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:bg-slate-400"
          >
            <Plus size={17} />
            {saving ? "Saving..." : "Create document"}
          </button>
        </form>
      </section>
    </div>
  );
}
