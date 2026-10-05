import { useState, type FormEvent } from "react";
import { ApiError, uploadDocument } from "../api/client";

export function UploadPanel() {
  const [file, setFile] = useState<File | null>(null);
  const [fileInputKey, setFileInputKey] = useState(0);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!file || loading) return;

    setLoading(true);
    setError(null);
    setMessage(null);
    try {
      const result = await uploadDocument(file);
      setMessage(`Added ${result.title} (${result.chunk_count} chunks). You can ask about it now.`);
      setFile(null);
      setFileInputKey((key) => key + 1);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not reach the server.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="upload-panel" onSubmit={handleSubmit}>
      <p className="upload-hint">
        Upload a .txt or .md document. It's added to your notes and can be asked about right away.
      </p>
      <div className="upload-row">
        <input
          key={fileInputKey}
          type="file"
          accept=".txt,.md"
          onChange={(event) => setFile(event.target.files?.[0] ?? null)}
          disabled={loading}
          required
        />
        <button type="submit" disabled={loading || !file}>
          {loading ? "Adding..." : "Upload"}
        </button>
      </div>
      {message && <p className="upload-message">{message}</p>}
      {error && <p className="question-form-error">{error}</p>}
    </form>
  );
}
