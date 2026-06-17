import { AuthProvider } from "./contexts/AuthContext.jsx";
import AppRouter from "./routes/AppRouter.jsx";

export default function App() {
  return (
    <AuthProvider>
      <AppRouter />
    </AuthProvider>
  );
}

