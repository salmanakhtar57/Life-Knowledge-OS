import type { AskResponse } from "../types/api";

const API_URL = import.meta.env.VITE_API_URL;

export class ApiError extends Error {}

export async function askQuestion(question: string): Promise<AskResponse> {
  const response = await fetch(`${API_URL}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    const message =
      (body && typeof body.detail === "string" && body.detail) ||
      "Something went wrong asking that question.";
    throw new ApiError(message);
  }

  return response.json();
}
