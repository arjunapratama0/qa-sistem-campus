export default function StatCard({ label, value, helper, icon: Icon }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-panel">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm font-medium text-campus-muted">{label}</p>
          <p className="mt-2 text-2xl font-semibold text-campus-ink">{value}</p>
        </div>
        {Icon ? (
          <div className="flex h-10 w-10 items-center justify-center rounded-md bg-slate-100 text-campus-blue">
            <Icon size={20} />
          </div>
        ) : null}
      </div>
      {helper ? <p className="mt-3 text-sm text-campus-muted">{helper}</p> : null}
    </div>
  );
}

