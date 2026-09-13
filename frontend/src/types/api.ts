export interface SourceOut {
  document_id: number;
  document_title: string;
  chunk_id: number;
  chunk_index: number;
  snippet: string;
}

export interface AskResponse {
  answer: string;
  sources: SourceOut[];
}
