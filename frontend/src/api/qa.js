import { apiRequest } from "./client.js";

export function askQuestion(question) {
  return apiRequest("/qa/ask", {
    method: "POST",
    body: JSON.stringify({ question }),
  });
}

