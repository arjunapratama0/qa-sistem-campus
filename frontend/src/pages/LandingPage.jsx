import { ArrowRight, BookOpen, LockKeyhole, SearchCheck } from "lucide-react";
import { Link } from "react-router-dom";
import heroImage from "../assets/hero.png";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <section
        className="relative flex min-h-[82vh] items-center bg-cover bg-center px-4"
        style={{ backgroundImage: `linear-gradient(rgba(15, 23, 42, 0.72), rgba(15, 23, 42, 0.84)), url(${heroImage})` }}
      >
        <div className="mx-auto w-full max-w-6xl">
          <div className="max-w-2xl">
            <p className="mb-4 text-sm font-semibold uppercase text-blue-200">
              Smart Informant Campus
            </p>
            <h1 className="text-4xl font-semibold leading-tight md:text-6xl">
              AI question answering for trusted campus information
            </h1>
            <p className="mt-5 max-w-xl text-base leading-7 text-slate-200 md:text-lg">
              Students can ask academic questions, get source-backed answers, and review their question history from one focused dashboard.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link
                to="/login"
                className="inline-flex min-h-11 items-center gap-2 rounded-md bg-white px-5 py-2 text-sm font-semibold text-slate-950 transition hover:bg-slate-100"
              >
                Login <ArrowRight size={18} />
              </Link>
              <Link
                to="/register"
                className="inline-flex min-h-11 items-center rounded-md border border-white/50 px-5 py-2 text-sm font-semibold text-white transition hover:bg-white/10"
              >
                Register
              </Link>
            </div>
          </div>
        </div>
      </section>

      <section className="bg-white px-4 py-8 text-campus-ink">
        <div className="mx-auto grid max-w-6xl gap-4 md:grid-cols-3">
          <div className="rounded-lg border border-slate-200 p-5">
            <SearchCheck className="text-campus-blue" size={24} />
            <h2 className="mt-4 text-lg font-semibold">Semantic answers</h2>
            <p className="mt-2 text-sm leading-6 text-campus-muted">
              Jina embeddings and pgvector retrieve relevant document chunks before answering.
            </p>
          </div>
          <div className="rounded-lg border border-slate-200 p-5">
            <BookOpen className="text-campus-green" size={24} />
            <h2 className="mt-4 text-lg font-semibold">Source citations</h2>
            <p className="mt-2 text-sm leading-6 text-campus-muted">
              Every response includes document evidence, similarity score, and citation metadata.
            </p>
          </div>
          <div className="rounded-lg border border-slate-200 p-5">
            <LockKeyhole className="text-campus-gold" size={24} />
            <h2 className="mt-4 text-lg font-semibold">Secure access</h2>
            <p className="mt-2 text-sm leading-6 text-campus-muted">
              JWT authentication and role based access control protect student and admin workflows.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}

