
import { useEffect, useState } from "react";
import {
  getSubstackWritingIdeas,
  getMediumWritingIdeas,
  refreshSubstackWritingIdeas,
  refreshMediumWritingIdeas,
} from "../api/client";
import type { WritingIdeasResponse } from "../types/api";

interface SuggestionsPanelProps {
  platform: "substack" | "medium";
}

export function SuggestionsPanel({ platform }: SuggestionsPanelProps) {
  const [data, setData] = useState<WritingIdeasResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  const isSubstack = platform === "substack";
  const platformName = isSubstack ? "Substack" : "Medium";

  useEffect(() => {
    let cancelled = false;

    async function fetchIdeas() {
      setLoading(true);
      setError("");

      try {
        const result = isSubstack
          ? await getSubstackWritingIdeas()
          : await getMediumWritingIdeas();

        if (!cancelled) {
          setData(result);
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error
              ? err.message
              : `Could not load ${platformName} writing suggestions.`,
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
  }, [platform, isSubstack, platformName]);

  async function handleRefresh() {
    if (refreshing) return;

    setRefreshing(true);
    setError("");

    try {
      const result = isSubstack
        ? await refreshSubstackWritingIdeas()
        : await refreshMediumWritingIdeas();

      setData(result);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : `Could not refresh ${platformName} writing suggestions.`,
      );
    } finally {
      setRefreshing(false);
    }
  }

  return (
    <section className={`suggestions-panel ${platform}-suggestions`}>
      <div className="suggestion-heading">
        <span className="bulb-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none">
            <path
              d="M9 18h6m-5 3h4m-6-6.5A7 7 0 0 1 16 14.5c-.8.7-1 1.3-1 2h-6c0-.7-.2-1.3-1-2Z"
              stroke="currentColor"
              strokeWidth="1.8"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </span>

        <div className="suggestion-content">
          <div className="suggestion-title-row">
            <h3>Writing Ideas</h3>

            <button
              type="button"
              className="icon-action"
              onClick={handleRefresh}
              disabled={loading || refreshing}
              title={`Refresh ${platformName} writing ideas`}
              aria-label={`Refresh ${platformName} writing ideas`}
            >
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.8"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M20 7v5h-5" />
                <path d="M4 17v-5h5" />
                <path d="M5.5 9A7 7 0 0 1 18 6l2 1" />
                <path d="M18.5 15A7 7 0 0 1 6 18l-2-1" />
              </svg>
            </button>
          </div>

          {loading && (
            <p>Analyzing your recent articles...</p>
          )}

          {refreshing && (
            <p>Generating new writing ideas...</p>
          )}

          {!loading && !refreshing && error && (
            <p className="suggestions-error">{error}</p>
          )}

          {!loading && !refreshing && !error && data && (
            <p>{data.summary}</p>
          )}
        </div>
      </div>

      {!loading && !refreshing && !error && data && data.ideas.length > 0 && (
        <div className="suggestion-chips">
          {data.ideas.map((idea, index) => (
            <div className="suggestion-chip" key={index}>
              {idea}
            </div>
          ))}
        </div>
      )}

      {!loading && !refreshing && !error && !data && (
        <p>No writing suggestions available yet.</p>
      )}
    </section>
  );
}
