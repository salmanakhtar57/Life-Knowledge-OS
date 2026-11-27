
import type { WritingIdeasResponse } from "../types/api";
import type {
  AskResponse,
  Post,
  StatsResponse,
  SyncResult,
  UploadResult,
} from "../types/api";

const API_URL = (import.meta.env.VITE_API_URL || "").replace(/\/+$/, "");

export class ApiError extends Error {}

async function request<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  if (!API_URL) {
    throw new ApiError("VITE_API_URL is not configured.");
  }

  let response: Response;

  try {
    response = await fetch(`${API_URL}${path}`, options);
  } catch {
    throw new ApiError("Could not reach the server. Check your connection.");
  }

  if (!response.ok) {
    const body = await response.json().catch(() => null);

    const detail =
      body && typeof body.detail === "string"
        ? body.detail
        : `Request failed (${response.status}).`;

    throw new ApiError(detail);
  }

  return response.json() as Promise<T>;
}

export async function askQuestion(
  question: string,
): Promise<AskResponse> {
  return request<AskResponse>("/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
}

export async function uploadDocument(
  file: File,
): Promise<UploadResult> {
  const form = new FormData();
  form.append("file", file);

  return request<UploadResult>("/documents/upload", {
    method: "POST",
    body: form,
  });
}

export async function getStats(): Promise<StatsResponse> {
  return request<StatsResponse>("/stats");
}

// Substack posts
export async function getLatestPosts(): Promise<Post[]> {
  const result = await request<Post[] | { posts: Post[] }>(
    "/posts/latest",
  );

  return Array.isArray(result) ? result : result.posts;
}

export async function getAllPosts(): Promise<Post[]> {
  const result = await request<Post[] | { posts: Post[] }>("/posts");

  return Array.isArray(result) ? result : result.posts;
}

export async function syncPosts(): Promise<SyncResult> {
  return request<SyncResult>("/posts/sync", {
    method: "POST",
  });
}

// Medium posts
export async function getLatestMediumPosts(): Promise<Post[]> {
  const result = await request<Post[] | { posts: Post[] }>(
    "/medium/posts/latest",
  );

  return Array.isArray(result) ? result : result.posts;
}

export async function getAllMediumPosts(): Promise<Post[]> {
  const result = await request<Post[] | { posts: Post[] }>(
    "/medium/posts",
  );

  return Array.isArray(result) ? result : result.posts;
}

export async function syncMediumPosts(): Promise<SyncResult> {
  return request<SyncResult>("/medium/sync", {
    method: "POST",
  });
}

// Retained for the existing URL-based source sync workflow.
export async function syncSubstack(url: string): Promise<SyncResult> {
  return request<SyncResult>("/sources/substack/sync", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });
}

export async function getWritingIdeas(): Promise<WritingIdeasResponse> {
  const response = await fetch(`${API_URL}/writing-ideas`);

  if (!response.ok) {
    throw new Error("Failed to generate writing ideas.");
  }

  return response.json();
}
