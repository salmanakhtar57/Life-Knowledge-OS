import type { AskResponse, UploadResult } from "../types/api";

const API_URL = import.meta.env.VITE_API_URL;

export class ApiError extends Error {}

async function errorMessage(response: Response, fallback: string): Promise<string> {
  const body = await response.json().catch(() => null);
  return (body && typeof body.detail === "string" && body.detail) || fallback;
}

export async function askQuestion(question: string): Promise<AskResponse> {
  const response = await fetch(`${API_URL}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });

  if (!response.ok) {
    throw new ApiError(await errorMessage(response, "Something went wrong asking that question."));
  }

  return response.json();
}

export async function uploadDocument(file: File): Promise<UploadResult> {
  const form = new FormData();
  form.append("file", file);

  const response = await fetch(`${API_URL}/documents/upload`, {
    method: "POST",
    body: form,
  });

  if (!response.ok) {
    throw new ApiError(await errorMessage(response, "Something went wrong uploading that file."));
  }

  return response.json();
}
