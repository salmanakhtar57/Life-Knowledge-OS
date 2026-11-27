
import { useEffect, useState } from "react";
import { getStats, ApiError } from "../api/client";
import type { StatsResponse } from "../types/api";

function formatDate(value: string | null): string {
  if (!value) return "Not available";

  return new Intl.DateTimeFormat("en", {
    day: "numeric",
    month: "short",
    year: "numeric",
  }).format(new Date(value));
}

export function StatsGrid() {
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadStats() {
    setLoading(true);
    setError("");

    try {
      setStats(await getStats());
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Could not load statistics.",
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadStats();
  }, []);

  const items = [
    {
      label: "Substack posts",
      value: stats?.substack_posts ?? "—",
      detail: "Published articles",
    },
    {
      label: "Medium posts",
      value: "—",
      detail: "Integration coming later",
    },
    {
      label: "Personal pages",
      value: stats?.faq_documents ?? "—",
      detail: "Knowledge documents",
    },
    {
      label: "Last published",
      value: stats ? formatDate(stats.last_published_at) : "—",
      detail:
        stats?.days_since_last_post == null
          ? "Publication activity"
          : `${stats.days_since_last_post} days ago`,
    },
  ];

  return (
    <section className="stats-section">
      <div className="section-heading">
        <div>
          <div className="eyebrow">AT A GLANCE</div>
          <h2>My writing, in numbers.</h2>
        </div>

        <button className="text-button" onClick={loadStats} disabled={loading}>
          {loading ? "Refreshing…" : "Refresh ↻"}
        </button>
      </div>

      {error && <p className="inline-error">{error}</p>}

      <div className="stats-grid">
        {items.map((item) => (
          <article className="stat-card" key={item.label}>
            <div className="stat-label">{item.label}</div>

            <div className="stat-value">
              {loading ? "…" : item.value}
            </div>

            <div className="stat-detail">{item.detail}</div>
          </article>
        ))}
      </div>

      {stats?.last_synced_at && (
        <p className="sync-meta">
          Last synced: {formatDate(stats.last_synced_at)}
        </p>
      )}
    </section>
  );
}
