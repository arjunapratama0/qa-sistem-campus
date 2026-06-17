import { apiRequest } from "./client.js";

export function login(payload) {
  return apiRequest("/auth/login", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function register(payload) {
  return apiRequest("/auth/register", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getMe() {
  return apiRequest("/auth/me");
}

export function refreshSession(refreshToken) {
  return apiRequest("/auth/refresh", {
    method: "POST",
    body: JSON.stringify({ refresh_token: refreshToken }),
  });
}

export function logoutSession(refreshToken) {
  return apiRequest("/auth/logout", {
    method: "POST",
    body: JSON.stringify({ refresh_token: refreshToken }),
  });
}
