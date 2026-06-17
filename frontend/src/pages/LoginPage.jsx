import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import SubmitButton from "../components/SubmitButton.jsx";
import { useAuth } from "../contexts/useAuth.js";

export default function LoginPage() {
  const navigate = useNavigate();
  const { isAuthenticated, login } = useAuth();
  const [form, setForm] = useState({ identifier: "", password: "" });
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
      await login(form);
      navigate("/dashboard");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="premium-gradient flex min-h-screen items-center justify-center px-4 py-10">
      <form onSubmit={handleSubmit} className="w-full max-w-md rounded-2xl border border-white/20 bg-white/95 p-7 shadow-premium backdrop-blur">
        <p className="text-sm font-semibold uppercase tracking-[0.18em] text-campus-gold">Universitas Udayana</p>
        <h1 className="mt-3 text-3xl font-bold text-campus-ink">Smart Informant Campus</h1>
        <p className="mt-2 text-sm leading-6 text-campus-muted">Masuk sebagai mahasiswa dengan NIM atau pegawai Tata Usaha dengan NIP.</p>
        <div className="mt-6 space-y-4">
          <label className="block">
            <span className="text-sm font-semibold text-campus-ink">NIM / NIP</span>
            <input
              value={form.identifier}
              onChange={(event) => setForm({ ...form, identifier: event.target.value })}
              placeholder="2305551000 atau 197000000000000000"
              className="field-control mt-2 h-12 w-full"
              required
            />
          </label>
          <label className="block">
            <span className="text-sm font-semibold text-campus-ink">Password</span>
            <input
              type="password"
              value={form.password}
              onChange={(event) => setForm({ ...form, password: event.target.value })}
              className="field-control mt-2 h-12 w-full"
              required
            />
          </label>
        </div>
        {error ? <p className="mt-4 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p> : null}
        <div className="mt-6 flex items-center justify-between gap-3">
          <Link to="/register" className="text-sm font-semibold text-campus-blue hover:underline">
            Daftar mahasiswa
          </Link>
          <SubmitButton loading={loading}>Login</SubmitButton>
        </div>
      </form>
    </main>
  );
}
