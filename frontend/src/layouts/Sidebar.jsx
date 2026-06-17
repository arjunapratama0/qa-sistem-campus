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
    <aside className="hidden w-64 border-r border-slate-200 bg-white md:block">
      <div className="border-b border-slate-200 px-5 py-5">
        <p className="text-base font-semibold text-campus-ink">SIC</p>
        <p className="mt-1 text-xs uppercase text-campus-muted">{role || "student"}</p>
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
                    ? "bg-blue-50 text-campus-blue"
                    : "text-campus-muted hover:bg-slate-100 hover:text-campus-ink",
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
