import { apiRequest } from "./client.js";

export function getDocuments() {
  return apiRequest("/documents");
}

export function createDocument(payload) {
  return apiRequest("/documents", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

