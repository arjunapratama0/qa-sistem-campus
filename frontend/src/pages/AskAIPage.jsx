import { Send } from "lucide-react";
import { useEffect, useState } from "react";
import { getQAExamples } from "../api/examples.js";
import { askQuestion } from "../api/qa.js";

export default function AskAIPage() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState(null);
  const [examples, setExamples] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let active = true;

    getQAExamples()
      .then((data) => {
        if (active) {
          setExamples(data);
        }
      })
      .catch(() => {
        if (active) {
          setExamples([]);
        }
      });

    return () => {
      active = false;
    };
  }, []);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      const data = await askQuestion(question);
      setAnswer(data);
      setQuestion("");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto grid max-w-6xl gap-6 xl:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)]">
      <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-panel">
        <h1 className="text-2xl font-semibold text-campus-ink">Ask AI</h1>
        <form onSubmit={handleSubmit} className="mt-5 space-y-4">
          <textarea
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Tanyakan informasi akademik kampus"
            className="min-h-40 w-full resize-y rounded-md border border-slate-300 p-3 text-sm outline-none focus:border-campus-blue focus:ring-2 focus:ring-blue-100"
            required
          />
          {error ? <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p> : null}
          <button
            type="submit"
            disabled={loading}
            className="inline-flex min-h-11 items-center gap-2 rounded-md bg-campus-blue px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:bg-slate-400"
          >
            <Send size={17} />
            {loading ? "Searching..." : "Submit question"}
          </button>
        </form>
        {examples.length ? (
          <div className="mt-6 border-t border-slate-200 pt-5">
            <p className="text-sm font-semibold text-campus-ink">Example questions</p>
            <div className="mt-3 space-y-2">
              {examples.slice(0, 5).map((example) => (
                <button
                  key={`${example.category}-${example.question}`}
                  type="button"
                  onClick={() => setQuestion(example.question)}
                  className="block w-full rounded-md border border-slate-200 px-3 py-2 text-left text-sm text-campus-muted transition hover:border-campus-blue hover:bg-blue-50 hover:text-campus-ink"
                >
                  <span className="block text-xs font-semibold uppercase text-campus-blue">{example.category}</span>
                  {example.question}
                </button>
              ))}
            </div>
          </div>
        ) : null}
      </section>

      <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-panel">
        <h2 className="text-lg font-semibold text-campus-ink">Answer</h2>
        {answer ? (
          <div className="mt-4 space-y-5">
            <p className="leading-7 text-campus-ink">{answer.answer}</p>
            <div className="rounded-md bg-slate-50 px-4 py-3">
              <p className="text-sm font-medium text-campus-ink">Confidence</p>
              <p className="mt-1 text-2xl font-semibold text-campus-blue">
                {Math.round(answer.confidence_score * 100)}%
              </p>
            </div>
            <div>
              <h3 className="text-sm font-semibold text-campus-ink">Citations</h3>
              <div className="mt-3 space-y-3">
                {answer.citations.length ? (
                  answer.citations.map((citation) => (
                    <article key={`${citation.document_chunk_id}-${citation.rank}`} className="rounded-md border border-slate-200 p-4">
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <p className="text-sm font-semibold text-campus-ink">{citation.document_title}</p>
                        <span className="text-xs text-campus-muted">
                          Similarity {Math.round(citation.similarity_score * 100)}%
                        </span>
                      </div>
                      <p className="mt-2 text-sm leading-6 text-campus-muted">{citation.quote}</p>
                    </article>
                  ))
                ) : (
                  <p className="text-sm text-campus-muted">No citation met the relevance threshold.</p>
                )}
              </div>
            </div>
          </div>
        ) : (
          <p className="mt-4 text-sm leading-6 text-campus-muted">
            Answers and citations will appear here after a question is submitted.
          </p>
        )}
      </section>
    </div>
  );
}
