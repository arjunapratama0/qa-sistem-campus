import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../contexts/useAuth.js";

export default function ProtectedRoute() {
  const { booting, isAuthenticated } = useAuth();

  if (booting) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-50 text-sm text-campus-muted">
        Loading session...
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
}
