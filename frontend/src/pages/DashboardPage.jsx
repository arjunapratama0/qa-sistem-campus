import { Bot, FileText, GraduationCap, History, ShieldCheck, Sparkles } from "lucide-react";
import StatCard from "../components/StatCard.jsx";
import { useAuth } from "../contexts/useAuth.js";

export default function DashboardPage() {
  const { user } = useAuth();

  return (
    <div className="mx-auto max-w-6xl">
      <section className="premium-gradient overflow-hidden rounded-2xl p-6 text-white shadow-premium md:p-8">
        <div className="flex flex-col gap-6 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="inline-flex items-center gap-2 rounded-full bg-white/15 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-campus-gold">
              <Sparkles size={14} /> Academic AI Assistant
            </p>
            <h1 className="mt-4 text-3xl font-bold md:text-4xl">Selamat datang, {user?.full_name}</h1>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-blue-50">
              Akses informasi akademik Universitas Udayana dengan jawaban berbasis dokumen, citation, dan riwayat pertanyaan yang tersimpan.
            </p>
          </div>
          <div className="rounded-2xl border border-white/15 bg-white/10 px-4 py-3 backdrop-blur">
            <p className="text-xs uppercase tracking-wide text-blue-100">{user?.identity_type === "staff" ? "NIP" : "NIM"}</p>
            <p className="mt-1 text-lg font-semibold">{user?.identity_type === "staff" ? user?.nip : user?.nim}</p>
          </div>
        </div>
      </section>
      <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Identity" value={user?.identity_type === "staff" ? "Tata Usaha" : "Mahasiswa"} helper="Login NIM/NIP aktif" icon={GraduationCap} />
        <StatCard label="Role" value={user?.role?.name || "student"} helper="Current access level" icon={ShieldCheck} />
        <StatCard label="Ask AI" value="Ready" helper="Semantic retrieval enabled" icon={Bot} />
        <StatCard label="History" value="Stored" helper="Questions are saved by user" icon={History} />
      </div>
      <section className="premium-panel mt-6 p-5">
        <div className="flex items-center gap-3">
          <FileText className="text-campus-blue dark:text-campus-gold" size={22} />
          <div>
            <h2 className="text-lg font-semibold text-campus-ink dark:text-white">System overview</h2>
            <p className="text-sm text-campus-muted dark:text-slate-400">Pipeline RAG untuk data akademik kampus</p>
          </div>
        </div>
        <div className="mt-4 grid gap-3 md:grid-cols-3">
          {["JWT + refresh token", "Jina Embeddings v3", "Groq LLM + Supabase pgvector"].map((item) => (
            <div key={item} className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm font-medium text-campus-ink dark:border-white/10 dark:bg-white/5 dark:text-slate-100">
              {item}
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
