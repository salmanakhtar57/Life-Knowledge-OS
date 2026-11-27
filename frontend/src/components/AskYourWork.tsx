
import { useState, type FormEvent } from "react";
import { askQuestion, ApiError } from "../api/client";
import type { AskResponse } from "../types/api";
import { SourceTag } from "./SourceTag";

export function AskYourWork() {
  const [question, setQuestion] = useState("");
  const [response, setResponse] = useState<AskResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const value = question.trim();

    if (!value || loading) return;

    setLoading(true);
    setError("");
    setResponse(null);

    try {
      const result = await askQuestion(value);
      setResponse(result);
      setQuestion("");
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : "Could not reach the server.",
      );
    } finally {
      setLoading(false);
    }
  }

  const uniqueSources = response
    ? Array.from(
        new Map(
          response.sources.map((source) => [
            `${source.document_title}-${source.source_platform}`,
            source,
          ]),
        ).values(),
      )
    : [];

  return (
    <section className="ask-section">
      <div className="ask-heading">
        <span className="ask-heading-icon" aria-hidden="true">
          <svg viewBox="0 0 40 40" fill="none">
            <path
              d="M5 17c0-7 6-12 14-12s14 5 14 12-6 12-14 12c-2 0-4-.4-6-1l-7 4 2-7c-2-2-3-5-3-8Z"
              stroke="currentColor"
              strokeWidth="2.3"
              strokeLinejoin="round"
            />
            <path d="m27 28 7 6" stroke="currentColor" strokeWidth="2.3" strokeLinecap="round" />
          </svg>
        </span>

        <h2>Ask your work</h2>
        <span className="ask-description">
          Search across your posts and knowledge
        </span>
      </div>

      <form className="ask-form" onSubmit={handleSubmit}>
        <div className="ask-input-wrap">
          <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <circle cx="10.8" cy="10.8" r="7.2" stroke="currentColor" strokeWidth="1.8" />
            <path d="m16 16 5 5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
          </svg>

          <input
            type="text"
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="What did I write about...?"
            aria-label="Ask a question about your writing"
            disabled={loading}
          />
        </div>

        <button type="submit" disabled={loading || !question.trim()}>
          {loading ? "Asking..." : "Ask"}
          <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path d="m4 4 17 8-17 8 3-8-3-8Z" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" />
            <path d="M7 12h14" stroke="currentColor" strokeWidth="1.8" />
          </svg>
        </button>
      </form>

      {error && <p className="ask-error" role="alert">{error}</p>}

      {response && (
        <article className="ask-result">
          <div className="answer-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none">
              <path d="M4 11c0-4 3.5-7 8-7s8 3 8 7-3.5 7-8 7h-2l-5 2 1-5c-1-1-2-2-2-4Z" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" />
            </svg>
          </div>

          <div className="ask-result-content">
            <p className="answer-text">{response.answer}</p>

            {uniqueSources.length > 0 && (
              <div className="ask-sources">
                {uniqueSources.map((source) => (
                  <SourceTag
                    key={`${source.document_id}-${source.chunk_id}`}
                    label={source.document_title}
                    platform={source.source_platform}
                    url={source.document_url}
                  />
                ))}
              </div>
            )}
          </div>
        </article>
      )}

      {!response && !loading && !error && (
        <div className="ask-hint">
          <span>Try asking:</span>
          <button type="button" onClick={() => setQuestion("What have I written about productivity?")}>
            What have I written about productivity?
          </button>
          <button type="button" onClick={() => setQuestion("What have I learned about software development?")}>
            What have I learned about software development?
          </button>
        </div>
      )}
    </section>
  );
}
