
import { useEffect, useState } from "react";
import { getWritingIdeas } from "../api/client";
import type { WritingIdeasResponse } from "../types/api";

interface SuggestionsPanelProps {
  platform: "substack" | "medium";
}

export function SuggestionsPanel({ platform }: SuggestionsPanelProps) {
  const [data, setData] = useState<WritingIdeasResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (platform !== "substack") {
      setLoading(false);
      return;
    }

    let cancelled = false;

    async function fetchIdeas() {
      try {
        const result = await getWritingIdeas();

        if (!cancelled) {
          setData(result);
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error
              ? err.message
              : "Could not load writing suggestions."
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void fetchIdeas();

    return () => {
      cancelled = true;
    };
  }, [platform]);

  if (platform !== "substack") return null;

  return (
    <section className="suggestions-panel substack-suggestions">
      <div className="suggestion-heading">
        <span className="bulb-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none">
            <path
              d="M9 18h6m-5 3h4m-6-6.5A7 7 0 1-A16 14.5c-.8.7-1 1.3-1 2h-6c0-.7-.2-1.3-1-2Z"
              stroke="currentColor"
              strokeWidth="1.8"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </span>

        <div>
          <h3>Writing Ideas</h3>

          {loading && <p>Analyzing your recent articles...</p>}

          {!loading && error && (
            <p className="suggestions-error">{error}</p>
          )}

          {!loading && !error && data && (
            <p>{data.summary}</p>
          )}
        </div>
      </div>

      {!loading && !error && data && data.ideas.length > 0 && (
        <div className="suggestion-chips">
      {data.ideas.map((idea, index) => (
        <div className="suggestion-chip" key={index}>
          {idea}
        </div>
      ))}
        </div>
      )}

      {!loading && !error && !data && (
        <p>No writing suggestions available yet.</p>
      )}
    </section>
  );
}
