import { Database, KeyRound, ShieldAlert } from "lucide-react";
import StatCard from "../components/StatCard.jsx";
import { useAuth } from "../contexts/useAuth.js";

export default function AdminDashboardPage() {
  const { user } = useAuth();
  const isAdmin = user?.role?.name === "admin";

  if (!isAdmin) {
    return (
      <div className="mx-auto max-w-3xl rounded-lg border border-amber-200 bg-amber-50 p-5 text-sm text-amber-900">
        Admin access is required.
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-6xl">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-campus-ink">Admin Dashboard</h1>
        <p className="mt-1 text-sm text-campus-muted">Security and operational overview</p>
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        <StatCard label="RBAC" value="Enabled" helper="Admin-only operations protected" icon={KeyRound} />
        <StatCard label="Database" value="pgvector" helper="Semantic index ready" icon={Database} />
        <StatCard label="Audit" value="Planned" helper="Schema prepared for logging" icon={ShieldAlert} />
      </div>
    </div>
  );
}
