import { useEffect, useMemo, useState } from "react";
import { clearToken, getRefreshToken, getToken, setRefreshToken, setToken } from "../api/client.js";
import {
  getMe,
  login as loginRequest,
  logoutSession,
  refreshSession,
  register as registerRequest,
} from "../api/auth.js";
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
        const refreshToken = getRefreshToken();
        if (!refreshToken) {
          clearToken();
          setUser(null);
        } else {
          try {
            const data = await refreshSession(refreshToken);
            setToken(data.access_token);
            setRefreshToken(data.refresh_token);
            setUser(data.user);
          } catch {
            clearToken();
            setUser(null);
          }
        }
      } finally {
        setBooting(false);
      }
    }

    hydrateSession();
  }, []);

  async function login(payload) {
    const data = await loginRequest(payload);
    setToken(data.access_token);
    setRefreshToken(data.refresh_token);
    setUser(data.user);
    return data.user;
  }

  async function register(payload) {
    const data = await registerRequest(payload);
    setToken(data.access_token);
    setRefreshToken(data.refresh_token);
    setUser(data.user);
    return data.user;
  }

  async function logout() {
    const refreshToken = getRefreshToken();
    if (refreshToken) {
      try {
        await logoutSession(refreshToken);
      } catch {
        // Local logout must still complete if the token is already invalid.
      }
    }
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
