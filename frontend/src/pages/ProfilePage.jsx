import { BadgeCheck, IdCard, Mail, ShieldCheck, UserCircle } from "lucide-react";
import { useAuth } from "../contexts/useAuth.js";

export default function ProfilePage() {
  const { user } = useAuth();

  return (
    <div className="mx-auto max-w-3xl">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-campus-ink dark:text-white">Profile</h1>
        <p className="mt-1 text-sm text-campus-muted dark:text-slate-400">Account details and access role</p>
      </div>
      <section className="premium-panel p-5">
        <div className="space-y-4">
          <div className="flex items-center gap-3 rounded-xl border border-slate-200 bg-white px-4 py-3 dark:border-white/10 dark:bg-white/5">
            <UserCircle className="text-campus-blue" size={20} />
            <div>
              <p className="text-xs uppercase text-campus-muted dark:text-slate-400">Name</p>
              <p className="text-sm font-semibold text-campus-ink dark:text-white">{user?.full_name}</p>
            </div>
          </div>
          <div className="flex items-center gap-3 rounded-xl border border-slate-200 bg-white px-4 py-3 dark:border-white/10 dark:bg-white/5">
            <IdCard className="text-campus-gold" size={20} />
            <div>
              <p className="text-xs uppercase text-campus-muted dark:text-slate-400">{user?.identity_type === "staff" ? "NIP" : "NIM"}</p>
              <p className="text-sm font-semibold text-campus-ink dark:text-white">{user?.identity_type === "staff" ? user?.nip : user?.nim}</p>
            </div>
          </div>
          <div className="flex items-center gap-3 rounded-xl border border-slate-200 bg-white px-4 py-3 dark:border-white/10 dark:bg-white/5">
            <Mail className="text-campus-green" size={20} />
            <div>
              <p className="text-xs uppercase text-campus-muted dark:text-slate-400">Email</p>
              <p className="text-sm font-semibold text-campus-ink dark:text-white">{user?.email}</p>
            </div>
          </div>
          <div className="flex items-center gap-3 rounded-xl border border-slate-200 bg-white px-4 py-3 dark:border-white/10 dark:bg-white/5">
            <ShieldCheck className="text-campus-gold" size={20} />
            <div>
              <p className="text-xs uppercase text-campus-muted dark:text-slate-400">Role</p>
              <p className="text-sm font-semibold text-campus-ink dark:text-white">{user?.role?.name}</p>
            </div>
          </div>
          <div className="flex items-center gap-3 rounded-xl border border-campus-green/20 bg-campus-green/5 px-4 py-3 dark:border-campus-gold/20 dark:bg-campus-gold/10">
            <BadgeCheck className="text-campus-green dark:text-campus-gold" size={20} />
            <div>
              <p className="text-xs uppercase text-campus-muted dark:text-slate-400">Status</p>
              <p className="text-sm font-semibold text-campus-ink dark:text-white">{user?.is_active ? "Active" : "Inactive"}</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
