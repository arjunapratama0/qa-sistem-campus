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
            <p className="mb-4 inline-flex rounded-full bg-white/15 px-3 py-1 text-sm font-semibold uppercase tracking-wide text-campus-gold backdrop-blur">
              Universitas Udayana - Teknologi Informasi
            </p>
            <h1 className="text-4xl font-semibold leading-tight md:text-6xl">
              Smart Informant Campus
            </h1>
            <p className="mt-5 max-w-xl text-base leading-7 text-slate-200 md:text-lg">
              AI question answering untuk mahasiswa, lengkap dengan citation, confidence score, dan sumber akademik yang dapat diperbarui oleh Tata Usaha.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link
                to="/login"
                className="inline-flex min-h-11 items-center gap-2 rounded-xl bg-campus-gold px-5 py-2 text-sm font-semibold text-campus-ink transition hover:bg-white"
              >
                Login <ArrowRight size={18} />
              </Link>
              <Link
                to="/register"
                className="inline-flex min-h-11 items-center rounded-xl border border-white/50 px-5 py-2 text-sm font-semibold text-white transition hover:bg-white/10"
              >
                Register
              </Link>
            </div>
          </div>
        </div>
      </section>

      <section className="bg-white px-4 py-8 text-campus-ink dark:bg-[#07111f] dark:text-white">
        <div className="mx-auto grid max-w-6xl gap-4 md:grid-cols-3">
          <div className="premium-panel p-5">
            <SearchCheck className="text-campus-blue" size={24} />
            <h2 className="mt-4 text-lg font-semibold">Semantic answers</h2>
            <p className="mt-2 text-sm leading-6 text-campus-muted dark:text-slate-400">
              Jina embeddings and pgvector retrieve relevant document chunks before answering.
            </p>
          </div>
          <div className="premium-panel p-5">
            <BookOpen className="text-campus-green" size={24} />
            <h2 className="mt-4 text-lg font-semibold">Source citations</h2>
            <p className="mt-2 text-sm leading-6 text-campus-muted dark:text-slate-400">
              Every response includes document evidence, similarity score, and citation metadata.
            </p>
          </div>
          <div className="premium-panel p-5">
            <LockKeyhole className="text-campus-gold" size={24} />
            <h2 className="mt-4 text-lg font-semibold">Secure access</h2>
            <p className="mt-2 text-sm leading-6 text-campus-muted dark:text-slate-400">
              JWT authentication and role based access control protect student and admin workflows.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
