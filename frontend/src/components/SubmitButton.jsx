export default function SubmitButton({ loading, children }) {
  return (
    <button
      type="submit"
      disabled={loading}
      className="inline-flex min-h-11 items-center justify-center rounded-md bg-campus-blue px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-400"
    >
      {loading ? "Processing..." : children}
    </button>
  );
}

