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
        <h1 className="text-2xl font-semibold text-campus-ink dark:text-white">Question History</h1>
        <p className="mt-1 text-sm text-campus-muted dark:text-slate-400">Your saved campus questions and cited answers</p>
      </div>

      {error ? <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p> : null}
      {loading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((item) => (
            <div key={item} className="premium-panel p-5">
              <div className="skeleton-line h-4 w-3/4" />
              <div className="mt-3 skeleton-line h-3 w-1/3" />
              <div className="mt-5 skeleton-line h-4 w-11/12" />
              <div className="mt-3 skeleton-line h-4 w-8/12" />
            </div>
          ))}
        </div>
      ) : null}

      <div className="space-y-4">
        {items.map((item) => (
          <article key={item.id} className="premium-panel p-5">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <p className="text-sm font-semibold text-campus-ink dark:text-white">{item.question}</p>
                <p className="mt-1 text-xs text-campus-muted dark:text-slate-400">{new Date(item.created_at).toLocaleString()}</p>
              </div>
              <span className="rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-campus-blue dark:bg-campus-gold/15 dark:text-campus-gold">
                {Math.round(item.confidence_score * 100)}%
              </span>
            </div>
            <p className="mt-4 rounded-2xl bg-slate-50 p-4 text-sm leading-6 text-campus-ink dark:bg-white/5 dark:text-slate-100">{item.answer}</p>
            {item.citations.length ? (
              <div className="mt-4 border-t border-slate-200 pt-4 dark:border-white/10">
                <p className="text-xs font-semibold uppercase text-campus-muted dark:text-slate-400">Sources</p>
                <div className="mt-2 space-y-2">
                  {item.citations.map((citation) => (
                    <p key={citation.id} className="rounded-xl border border-slate-200 px-3 py-2 text-sm text-campus-muted dark:border-white/10 dark:text-slate-300">
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
        <div className="premium-panel p-5 text-sm text-campus-muted dark:text-slate-400">
          No question history yet.
        </div>
      ) : null}
    </div>
  );
}
