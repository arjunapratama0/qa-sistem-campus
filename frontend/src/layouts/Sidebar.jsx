import {
  Bot,
  FileText,
  History,
  LayoutDashboard,
  ShieldCheck,
  UserCircle,
} from "lucide-react";
import { NavLink } from "react-router-dom";
import { useAuth } from "../contexts/useAuth.js";

const navItems = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/ask", label: "Ask AI", icon: Bot },
  { to: "/history", label: "History", icon: History },
  { to: "/documents", label: "Documents", icon: FileText, roles: ["staff", "admin"] },
  { to: "/profile", label: "Profile", icon: UserCircle },
  { to: "/admin", label: "Admin", icon: ShieldCheck, roles: ["admin"] },
];

export default function Sidebar() {
  const { user } = useAuth();
  const role = user?.role?.name;
  const visibleItems = navItems.filter((item) => !item.roles || item.roles.includes(role));

  return (
    <aside className="hidden w-72 border-r border-slate-200/80 bg-white/90 backdrop-blur-xl dark:border-white/10 dark:bg-[#07111f]/95 md:block">
      <div className="border-b border-slate-200/80 px-5 py-5 dark:border-white/10">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-campus-navy text-sm font-bold text-campus-gold shadow-premium">
            SIC
          </div>
          <div>
            <p className="text-base font-semibold text-campus-ink dark:text-white">Smart Informant</p>
            <p className="mt-1 text-xs uppercase tracking-wide text-campus-muted dark:text-slate-400">{role || "student"}</p>
          </div>
        </div>
      </div>
      <nav className="space-y-1 px-3 py-4">
        {visibleItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                [
                  "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition",
                  isActive
                    ? "bg-campus-blue text-white shadow-panel"
                    : "text-campus-muted hover:bg-slate-100 hover:text-campus-ink dark:text-slate-400 dark:hover:bg-white/10 dark:hover:text-white",
                ].join(" ")
              }
            >
              <Icon size={18} />
              {item.label}
            </NavLink>
          );
        })}
      </nav>
    </aside>
  );
}
