export default function StatCard({ label, value, helper, icon: Icon }) {
  return (
    <div className="premium-panel group p-5 transition duration-300 hover:-translate-y-0.5 hover:shadow-premium">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm font-medium text-campus-muted dark:text-slate-400">{label}</p>
          <p className="mt-2 text-2xl font-semibold text-campus-ink dark:text-white">{value}</p>
        </div>
        {Icon ? (
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-campus-blue/10 text-campus-blue transition group-hover:bg-campus-gold/20 group-hover:text-campus-navy dark:bg-white/10 dark:text-campus-gold">
            <Icon size={20} />
          </div>
        ) : null}
      </div>
      {helper ? <p className="mt-3 text-sm text-campus-muted dark:text-slate-400">{helper}</p> : null}
    </div>
  );
}
