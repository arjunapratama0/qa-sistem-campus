import { Bot, History, LayoutDashboard, UserCircle } from "lucide-react";
import { NavLink } from "react-router-dom";

const items = [
  { to: "/dashboard", label: "Home", icon: LayoutDashboard },
  { to: "/ask", label: "Ask", icon: Bot },
  { to: "/history", label: "History", icon: History },
  { to: "/profile", label: "Profile", icon: UserCircle },
];

export default function MobileNav() {
  return (
    <nav className="fixed inset-x-0 bottom-0 z-20 border-t border-slate-200 bg-white/95 backdrop-blur-xl dark:border-white/10 dark:bg-[#07111f]/95 md:hidden">
      <div className="grid grid-cols-4">
        {items.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                [
                  "flex min-h-16 flex-col items-center justify-center gap-1 text-xs font-medium",
                  isActive ? "text-campus-blue dark:text-campus-gold" : "text-campus-muted dark:text-slate-400",
                ].join(" ")
              }
            >
              <Icon size={19} />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </div>
    </nav>
  );
}
