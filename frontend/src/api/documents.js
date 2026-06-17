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

export function uploadDocumentPdf({ file, title }) {
  const formData = new FormData();
  formData.append("file", file);
  if (title) {
    formData.append("title", title);
  }

  return apiRequest("/documents/upload", {
    method: "POST",
    body: formData,
  });
}
