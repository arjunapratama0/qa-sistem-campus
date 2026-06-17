import { BookOpenCheck, Quote, Send, Sparkles } from "lucide-react";
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
      <section className="premium-panel p-5">
        <div className="rounded-2xl bg-campus-navy p-5 text-white shadow-premium">
          <p className="inline-flex items-center gap-2 text-sm font-semibold text-campus-gold">
            <Sparkles size={16} /> Groq + Jina RAG
          </p>
          <h1 className="mt-3 text-2xl font-bold">Tanya AI Akademik</h1>
          <p className="mt-2 text-sm leading-6 text-blue-50">
            Jawaban dibuat dari dokumen kampus yang sudah di-chunk, di-embedding, lalu dicocokkan dengan pgvector.
          </p>
        </div>
        <form onSubmit={handleSubmit} className="mt-5 space-y-4">
          <textarea
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Contoh: kapan masa KRS semester ganjil?"
            className="field-control min-h-44 w-full resize-y py-3"
            required
          />
          {error ? <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p> : null}
          <button
            type="submit"
            disabled={loading}
            className="inline-flex min-h-11 items-center gap-2 rounded-xl bg-campus-blue px-5 py-2 text-sm font-semibold text-white shadow-panel transition hover:-translate-y-0.5 hover:bg-campus-navy disabled:translate-y-0 disabled:bg-slate-400"
          >
            <Send size={17} />
            {loading ? "Mencari sumber..." : "Kirim pertanyaan"}
          </button>
        </form>
        {examples.length ? (
          <div className="mt-6 border-t border-slate-200 pt-5">
            <p className="text-sm font-semibold text-campus-ink dark:text-white">Contoh pertanyaan</p>
            <div className="mt-3 space-y-2">
              {examples.slice(0, 5).map((example) => (
                <button
                  key={`${example.category}-${example.question}`}
                  type="button"
                  onClick={() => setQuestion(example.question)}
                  className="block w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-left text-sm text-campus-muted transition hover:border-campus-blue hover:bg-blue-50 hover:text-campus-ink dark:border-white/10 dark:bg-white/5 dark:text-slate-300 dark:hover:bg-white/10 dark:hover:text-white"
                >
                  <span className="block text-xs font-semibold uppercase text-campus-blue">{example.category}</span>
                  {example.question}
                </button>
              ))}
            </div>
          </div>
        ) : null}
      </section>

      <section className="premium-panel p-5">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-campus-gold/20 text-campus-navy dark:text-campus-gold">
            <BookOpenCheck size={21} />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-campus-ink dark:text-white">Jawaban</h2>
            <p className="text-sm text-campus-muted dark:text-slate-400">Dengan citation dan confidence score</p>
          </div>
        </div>
        {loading ? (
          <div className="mt-5 space-y-4">
            <div className="skeleton-line h-4 w-11/12" />
            <div className="skeleton-line h-4 w-10/12" />
            <div className="skeleton-line h-4 w-8/12" />
            <div className="h-24 animate-pulse rounded-2xl bg-slate-100 dark:bg-white/10" />
          </div>
        ) : answer ? (
          <div className="mt-4 space-y-5">
            <p className="rounded-2xl bg-slate-50 p-4 leading-7 text-campus-ink dark:bg-white/5 dark:text-slate-100">{answer.answer}</p>
            <div className="rounded-2xl border border-slate-200 bg-white px-4 py-3 dark:border-white/10 dark:bg-white/5">
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium text-campus-ink dark:text-white">Confidence</p>
                <p className="text-2xl font-semibold text-campus-blue dark:text-campus-gold">
                {Math.round(answer.confidence_score * 100)}%
              </p>
              </div>
              <div className="mt-3 h-2 overflow-hidden rounded-full bg-slate-100 dark:bg-white/10">
                <div className="h-full rounded-full bg-campus-blue dark:bg-campus-gold" style={{ width: `${Math.round(answer.confidence_score * 100)}%` }} />
              </div>
            </div>
            <div>
              <h3 className="text-sm font-semibold text-campus-ink dark:text-white">Citation Cards</h3>
              <div className="mt-3 space-y-3">
                {answer.citations.length ? (
                  answer.citations.map((citation) => (
                    <article key={`${citation.document_chunk_id}-${citation.rank}`} className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm dark:border-white/10 dark:bg-white/5">
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <p className="inline-flex items-center gap-2 text-sm font-semibold text-campus-ink dark:text-white">
                          <Quote size={16} className="text-campus-gold" /> {citation.document_title}
                        </p>
                        <span className="rounded-full bg-campus-blue/10 px-2 py-1 text-xs font-semibold text-campus-blue dark:bg-campus-gold/15 dark:text-campus-gold">
                          Similarity {Math.round(citation.similarity_score * 100)}%
                        </span>
                      </div>
                      <p className="mt-2 text-sm leading-6 text-campus-muted dark:text-slate-300">{citation.quote}</p>
                    </article>
                  ))
                ) : (
                  <p className="text-sm text-campus-muted dark:text-slate-400">Belum ada citation yang melewati threshold relevansi.</p>
                )}
              </div>
            </div>
          </div>
        ) : (
          <p className="mt-4 rounded-2xl border border-dashed border-slate-300 p-5 text-sm leading-6 text-campus-muted dark:border-white/10 dark:text-slate-400">
            Jawaban, confidence, dan citation akan muncul setelah pertanyaan dikirim.
          </p>
        )}
      </section>
    </div>
  );
}
