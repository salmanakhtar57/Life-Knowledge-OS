
export type SourcePlatform =
  | "personal"
  | "substack"
  | "medium"
  | "portfolio";

export interface SourceOut {
  document_id: number;
  document_title: string;
  chunk_id: number;
  chunk_index: number;
  snippet: string;  
  source_platform: SourcePlatform;
  document_url: string | null;
}

export interface AskResponse {
  answer: string;
  sources: SourceOut[];
}

export interface UploadResult {
  id: number;
  title: string;
  chunk_count: number;
}

export interface SyncResult {
  fetched: number;
  new: number;
  skipped_duplicates: number;
  skipped_empty: number;
  message?: string;
  already_running?: boolean;
}

export interface Post {
  id: number;
  title: string;
  url: string;
  published_at: string | null;
  created_at: string;
}

export interface StatsResponse {
  substack_posts: number;
  medium_posts: number;
  faq_documents: number;
  last_published_at: string | null;
  days_since_last_post: number | null;
  last_synced_at: string | null;
}


export interface WritingIdea {
  title: string;
  description: string;
}

export interface WritingIdeasResponse {
  summary: string;
  ideas: string[];
}