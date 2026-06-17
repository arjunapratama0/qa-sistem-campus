import { LogOut, User } from "lucide-react";
import { useAuth } from "../contexts/useAuth.js";

export default function Navbar() {
  const { user, logout } = useAuth();

  return (
    <header className="flex min-h-16 items-center justify-between border-b border-slate-200 bg-white px-4 md:px-6">
      <div>
        <p className="text-sm font-semibold text-campus-ink">Smart Informant Campus</p>
        <p className="text-xs text-campus-muted">AI academic information assistant</p>
      </div>
      <div className="flex items-center gap-3">
        <div className="hidden items-center gap-2 rounded-md border border-slate-200 px-3 py-2 sm:flex">
          <User size={16} className="text-campus-muted" />
          <span className="max-w-40 truncate text-sm text-campus-ink">{user?.full_name}</span>
        </div>
        <button
          type="button"
          onClick={logout}
          className="inline-flex h-10 w-10 items-center justify-center rounded-md border border-slate-200 text-campus-muted transition hover:bg-slate-100 hover:text-campus-ink"
          aria-label="Logout"
          title="Logout"
        >
          <LogOut size={18} />
        </button>
      </div>
    </header>
  );
}
