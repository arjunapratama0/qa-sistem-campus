import { Mail, ShieldCheck, UserCircle } from "lucide-react";
import { useAuth } from "../contexts/useAuth.js";

export default function ProfilePage() {
  const { user } = useAuth();

  return (
    <div className="mx-auto max-w-3xl">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-campus-ink">Profile</h1>
        <p className="mt-1 text-sm text-campus-muted">Account details and access role</p>
      </div>
      <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-panel">
        <div className="space-y-4">
          <div className="flex items-center gap-3 rounded-md border border-slate-200 px-4 py-3">
            <UserCircle className="text-campus-blue" size={20} />
            <div>
              <p className="text-xs uppercase text-campus-muted">Name</p>
              <p className="text-sm font-semibold text-campus-ink">{user?.full_name}</p>
            </div>
          </div>
          <div className="flex items-center gap-3 rounded-md border border-slate-200 px-4 py-3">
            <Mail className="text-campus-green" size={20} />
            <div>
              <p className="text-xs uppercase text-campus-muted">Email</p>
              <p className="text-sm font-semibold text-campus-ink">{user?.email}</p>
            </div>
          </div>
          <div className="flex items-center gap-3 rounded-md border border-slate-200 px-4 py-3">
            <ShieldCheck className="text-campus-gold" size={20} />
            <div>
              <p className="text-xs uppercase text-campus-muted">Role</p>
              <p className="text-sm font-semibold text-campus-ink">{user?.role?.name}</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
