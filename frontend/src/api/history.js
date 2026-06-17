import { apiRequest } from "./client.js";

export function getHistory() {
  return apiRequest("/history");
}

