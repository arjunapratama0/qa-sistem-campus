import { Bot, FileText, History, ShieldCheck } from "lucide-react";
import StatCard from "../components/StatCard.jsx";
import { useAuth } from "../contexts/useAuth.js";

export default function DashboardPage() {
  const { user } = useAuth();

  return (
    <div className="mx-auto max-w-6xl">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-campus-ink">Dashboard</h1>
        <p className="mt-1 text-sm text-campus-muted">Welcome, {user?.full_name}</p>
      </div>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Role" value={user?.role?.name || "student"} helper="Current access level" icon={ShieldCheck} />
        <StatCard label="Ask AI" value="Ready" helper="Semantic retrieval enabled" icon={Bot} />
        <StatCard label="History" value="Stored" helper="Questions are saved by user" icon={History} />
        <StatCard label="Sources" value="Cited" helper="Answers include evidence" icon={FileText} />
      </div>
      <section className="mt-6 rounded-lg border border-slate-200 bg-white p-5 shadow-panel">
        <h2 className="text-lg font-semibold text-campus-ink">System overview</h2>
        <div className="mt-4 grid gap-3 md:grid-cols-3">
          {["JWT authentication", "Jina Embeddings v3", "Supabase pgvector"].map((item) => (
            <div key={item} className="rounded-md border border-slate-200 px-4 py-3 text-sm font-medium text-campus-ink">
              {item}
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
