import { Database, FileUp, KeyRound, ShieldAlert } from "lucide-react";
import { Link } from "react-router-dom";
import StatCard from "../components/StatCard.jsx";
import { useAuth } from "../contexts/useAuth.js";

export default function AdminDashboardPage() {
  const { user } = useAuth();
  const isAdmin = user?.role?.name === "admin";

  if (!isAdmin) {
    return (
      <div className="mx-auto max-w-3xl rounded-2xl border border-amber-200 bg-amber-50 p-5 text-sm text-amber-900 dark:border-amber-400/30 dark:bg-amber-400/10 dark:text-amber-100">
        Admin access is required.
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-6xl">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-campus-ink dark:text-white">Admin Dashboard</h1>
        <p className="mt-1 text-sm text-campus-muted dark:text-slate-400">Security and operational overview for Tata Usaha</p>
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        <StatCard label="RBAC" value="Enabled" helper="Admin-only operations protected" icon={KeyRound} />
        <StatCard label="Database" value="pgvector" helper="Semantic index ready" icon={Database} />
        <StatCard label="Audit" value="Active" helper="Security middleware tested" icon={ShieldAlert} />
      </div>
      <section className="premium-panel mt-6 p-5">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <h2 className="text-lg font-semibold text-campus-ink dark:text-white">Perbarui Data Akademik</h2>
            <p className="mt-1 text-sm leading-6 text-campus-muted dark:text-slate-400">
              Upload PDF pedoman atau kalender akademik, sistem akan memprosesnya menjadi chunks dan embeddings.
            </p>
          </div>
          <Link
            to="/documents"
            className="inline-flex min-h-11 items-center justify-center gap-2 rounded-xl bg-campus-blue px-5 py-2 text-sm font-semibold text-white shadow-panel transition hover:bg-campus-navy"
          >
            <FileUp size={17} /> Upload PDF
          </Link>
        </div>
      </section>
    </div>
  );
}
