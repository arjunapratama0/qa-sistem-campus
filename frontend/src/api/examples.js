import { apiRequest } from "./client.js";

export function getQAExamples() {
  return apiRequest("/qa/examples");
}
