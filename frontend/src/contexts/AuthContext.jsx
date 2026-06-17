import { useEffect, useMemo, useState } from "react";
import { clearToken, getToken, setToken } from "../api/client.js";
import { getMe, login as loginRequest, register as registerRequest } from "../api/auth.js";
import { AuthContext } from "./authContext.js";

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [booting, setBooting] = useState(true);

  useEffect(() => {
    async function hydrateSession() {
      if (!getToken()) {
        setBooting(false);
        return;
      }

      try {
        const currentUser = await getMe();
        setUser(currentUser);
      } catch {
        clearToken();
        setUser(null);
      } finally {
        setBooting(false);
      }
    }

    hydrateSession();
  }, []);

  async function login(payload) {
    const data = await loginRequest(payload);
    setToken(data.access_token);
    setUser(data.user);
    return data.user;
  }

  async function register(payload) {
    const data = await registerRequest(payload);
    setToken(data.access_token);
    setUser(data.user);
    return data.user;
  }

  function logout() {
    clearToken();
    setUser(null);
  }

  const value = useMemo(
    () => ({
      user,
      booting,
      isAuthenticated: Boolean(user),
      login,
      register,
      logout,
    }),
    [user, booting],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
