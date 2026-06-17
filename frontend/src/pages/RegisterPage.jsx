import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import SubmitButton from "../components/SubmitButton.jsx";
import { useAuth } from "../contexts/useAuth.js";

export default function RegisterPage() {
  const navigate = useNavigate();
  const { isAuthenticated, register } = useAuth();
  const [form, setForm] = useState({ full_name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      await register(form);
      navigate("/dashboard");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-50 px-4">
      <form onSubmit={handleSubmit} className="w-full max-w-md rounded-lg border border-slate-200 bg-white p-6 shadow-panel">
        <p className="text-sm font-semibold text-campus-blue">Smart Informant Campus</p>
        <h1 className="mt-3 text-2xl font-semibold text-campus-ink">Register</h1>
        <div className="mt-6 space-y-4">
          <label className="block">
            <span className="text-sm font-medium text-campus-ink">Full name</span>
            <input
              value={form.full_name}
              onChange={(event) => setForm({ ...form, full_name: event.target.value })}
              className="mt-2 h-11 w-full rounded-md border border-slate-300 px-3 text-sm outline-none focus:border-campus-blue focus:ring-2 focus:ring-blue-100"
              required
            />
          </label>
          <label className="block">
            <span className="text-sm font-medium text-campus-ink">Email</span>
            <input
              type="email"
              value={form.email}
              onChange={(event) => setForm({ ...form, email: event.target.value })}
              className="mt-2 h-11 w-full rounded-md border border-slate-300 px-3 text-sm outline-none focus:border-campus-blue focus:ring-2 focus:ring-blue-100"
              required
            />
          </label>
          <label className="block">
            <span className="text-sm font-medium text-campus-ink">Password</span>
            <input
              type="password"
              minLength={8}
              value={form.password}
              onChange={(event) => setForm({ ...form, password: event.target.value })}
              className="mt-2 h-11 w-full rounded-md border border-slate-300 px-3 text-sm outline-none focus:border-campus-blue focus:ring-2 focus:ring-blue-100"
              required
            />
          </label>
        </div>
        {error ? <p className="mt-4 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p> : null}
        <div className="mt-6 flex items-center justify-between gap-3">
          <Link to="/login" className="text-sm font-medium text-campus-blue hover:underline">
            Already registered
          </Link>
          <SubmitButton loading={loading}>Register</SubmitButton>
        </div>
      </form>
    </main>
  );
}
