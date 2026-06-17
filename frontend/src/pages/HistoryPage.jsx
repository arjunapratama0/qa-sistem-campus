import { useEffect, useState } from "react";
import { getHistory } from "../api/history.js";

export default function HistoryPage() {
  const [items, setItems] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadHistory() {
      try {
        const data = await getHistory();
        setItems(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    loadHistory();
  }, []);

  return (
    <div className="mx-auto max-w-6xl">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-campus-ink">Question History</h1>
        <p className="mt-1 text-sm text-campus-muted">Your saved campus questions and cited answers</p>
      </div>

      {error ? <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p> : null}
      {loading ? <p className="text-sm text-campus-muted">Loading history...</p> : null}

      <div className="space-y-4">
        {items.map((item) => (
          <article key={item.id} className="rounded-lg border border-slate-200 bg-white p-5 shadow-panel">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <p className="text-sm font-semibold text-campus-ink">{item.question}</p>
                <p className="mt-1 text-xs text-campus-muted">{new Date(item.created_at).toLocaleString()}</p>
              </div>
              <span className="rounded-md bg-blue-50 px-2 py-1 text-xs font-semibold text-campus-blue">
                {Math.round(item.confidence_score * 100)}%
              </span>
            </div>
            <p className="mt-4 text-sm leading-6 text-campus-ink">{item.answer}</p>
            {item.citations.length ? (
              <div className="mt-4 border-t border-slate-200 pt-4">
                <p className="text-xs font-semibold uppercase text-campus-muted">Sources</p>
                <div className="mt-2 space-y-2">
                  {item.citations.map((citation) => (
                    <p key={citation.id} className="text-sm text-campus-muted">
                      {citation.rank}. {citation.document_title}
                      {citation.page_number ? `, page ${citation.page_number}` : ""}
                    </p>
                  ))}
                </div>
              </div>
            ) : null}
          </article>
        ))}
      </div>

      {!loading && !items.length ? (
        <div className="rounded-lg border border-slate-200 bg-white p-5 text-sm text-campus-muted shadow-panel">
          No question history yet.
        </div>
      ) : null}
    </div>
  );
}

