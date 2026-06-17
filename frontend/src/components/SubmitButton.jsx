export default function SubmitButton({ loading, children }) {
  return (
    <button
      type="submit"
      disabled={loading}
      className="inline-flex min-h-11 items-center justify-center rounded-xl bg-campus-blue px-5 py-2 text-sm font-semibold text-white shadow-panel transition hover:-translate-y-0.5 hover:bg-campus-navy disabled:translate-y-0 disabled:cursor-not-allowed disabled:bg-slate-400"
    >
      {loading ? "Processing..." : children}
    </button>
  );
}
