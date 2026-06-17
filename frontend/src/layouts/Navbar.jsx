import { LogOut, Moon, Sun, User } from "lucide-react";
import { useEffect, useState } from "react";
import { useAuth } from "../contexts/useAuth.js";

export default function Navbar() {
  const { user, logout } = useAuth();
  const [darkMode, setDarkMode] = useState(() => localStorage.getItem("sic_theme") === "dark");

  useEffect(() => {
    document.documentElement.classList.toggle("dark", darkMode);
    localStorage.setItem("sic_theme", darkMode ? "dark" : "light");
  }, [darkMode]);

  return (
    <header className="sticky top-0 z-10 flex min-h-16 items-center justify-between border-b border-slate-200/80 bg-white/85 px-4 backdrop-blur-xl dark:border-white/10 dark:bg-[#07111f]/80 md:px-6">
      <div>
        <p className="text-sm font-semibold text-campus-ink dark:text-white">Smart Informant Campus</p>
        <p className="text-xs text-campus-muted dark:text-slate-400">Universitas Udayana - Teknologi Informasi</p>
      </div>
      <div className="flex items-center gap-3">
        <div className="hidden items-center gap-2 rounded-xl border border-slate-200 bg-white/80 px-3 py-2 shadow-sm dark:border-white/10 dark:bg-white/5 sm:flex">
          <User size={16} className="text-campus-blue dark:text-campus-gold" />
          <div className="min-w-0">
            <span className="block max-w-40 truncate text-sm font-semibold text-campus-ink dark:text-white">{user?.full_name}</span>
            <span className="block text-xs text-campus-muted dark:text-slate-400">
              {user?.identity_type === "staff" ? `NIP ${user?.nip}` : `NIM ${user?.nim}`}
            </span>
          </div>
        </div>
        <button
          type="button"
          onClick={() => setDarkMode((value) => !value)}
          className="inline-flex h-10 w-10 items-center justify-center rounded-xl border border-slate-200 bg-white text-campus-muted transition hover:bg-campus-blue hover:text-white dark:border-white/10 dark:bg-white/5 dark:text-slate-300"
          aria-label="Toggle dark mode"
          title="Toggle dark mode"
        >
          {darkMode ? <Sun size={18} /> : <Moon size={18} />}
        </button>
        <button
          type="button"
          onClick={logout}
          className="inline-flex h-10 w-10 items-center justify-center rounded-xl border border-slate-200 bg-white text-campus-muted transition hover:bg-red-50 hover:text-red-600 dark:border-white/10 dark:bg-white/5 dark:text-slate-300"
          aria-label="Logout"
          title="Logout"
        >
          <LogOut size={18} />
        </button>
      </div>
    </header>
  );
}
