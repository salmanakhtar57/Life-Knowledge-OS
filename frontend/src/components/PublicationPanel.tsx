
import { useState } from "react";
import { getAllPosts, getLatestPosts, syncPosts } from "../api/client";
import type { Post } from "../types/api";
import { SuggestionsPanel } from "./SuggestionsPanel";

interface PublicationPanelProps {
  platform: "substack" | "medium";
  posts: Post[];
  onPostsUpdated: (posts: Post[]) => void;
  onSynced: () => Promise<void>;
}

function formatDate(date: string | null) {
  if (!date) return "";

  const parsed = new Date(date);

  if (Number.isNaN(parsed.getTime())) return "";

  return parsed.toLocaleDateString("en-US", {
    month: "short",
    day: "2-digit",
    year: "numeric",
  });
}

export function PublicationPanel({
  platform,
  posts,
  onPostsUpdated,
  onSynced,
}: PublicationPanelProps) {
  const [showAll, setShowAll] = useState(false);
  const [loadingAll, setLoadingAll] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [status, setStatus] = useState("");

  const isSubstack = platform === "substack";

  async function handleSeeAll() {
    if (!isSubstack || loadingAll) return;

    if (showAll) {
      setShowAll(false);
      return;
    }

    setLoadingAll(true);
    setStatus("");

    try {
      const allPosts = await getAllPosts();
      onPostsUpdated(allPosts);
      setShowAll(true);
    } catch (error) {
      setStatus(
        error instanceof Error ? error.message : "Could not load all posts.",
      );
    } finally {
      setLoadingAll(false);
    }
  }

  async function handleSync() {
    if (!isSubstack || syncing) return;

    setSyncing(true);
    setStatus("Syncing your Substack...");

    try {
      const result = await syncPosts();

      const latest = await getLatestPosts();
      onPostsUpdated(latest);

      setShowAll(false);

      setStatus(
        result.message ||
          `Sync complete. ${result.new} new posts added, ${result.skipped_duplicates} already stored.`,
      );

      await onSynced();
    } catch (error) {
      setStatus(
        error instanceof Error ? error.message : "Could not sync Substack.",
      );
    } finally {
      setSyncing(false);
    }
  }

  const displayedPosts = showAll ? posts : posts.slice(0, 3);

  return (
    <section className={`publication-card ${platform}-card`}>
      <div className="publication-heading">
        <div className="publication-title">
          {isSubstack ? (
            <div className="publication-logo substack-logo" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M3 4.2h18v3.2H3zM3 9h18v3.2H3zM3 13.8h18v3.1H3zM3 18.2l9 4.7 9-4.7v-1.5H3z" />
              </svg>
            </div>
          ) : (
            <div className="publication-logo medium-logo" aria-hidden="true">
              M
            </div>
          )}

          <h2>Latest on {isSubstack ? "Substack" : "Medium"}</h2>
        </div>

        <div className="publication-actions">
          {isSubstack && (
            <button
              type="button"
              className="icon-action"
              onClick={handleSync}
              disabled={syncing}
              title="Sync latest Substack posts"
              aria-label="Sync latest Substack posts"
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
          )}

          {isSubstack && (
            <button
              type="button"
              className="see-all-button"
              onClick={handleSeeAll}
              disabled={loadingAll}
            >
              {loadingAll
                ? "Loading..."
                : showAll
                  ? "Show latest"
                  : "See all"}
              <span aria-hidden="true">→</span>
            </button>
          )}
        </div>
      </div>

      {isSubstack ? (
        <>
          <div className="post-list">
            {displayedPosts.length > 0 ? (
              displayedPosts.map((post) => (
                <a
                  key={post.id}
                  href={post.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="post-row"
                >
                  <svg
                    className="post-icon"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="1.8"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    aria-hidden="true"
                  >
                    <path d="M6 3h8l4 4v14H6z" />
                    <path d="M14 3v5h4M9 12h6M9 16h6" />
                  </svg>

                  <span className="post-title">{post.title}</span>

                  <time dateTime={post.published_at ?? undefined}>
                    {formatDate(post.published_at)}
                  </time>
                </a>
              ))
            ) : (
              <div className="publication-empty">
                <span>No Substack posts found yet.</span>
                <button type="button" onClick={handleSync} disabled={syncing}>
                  {syncing ? "Syncing..." : "Sync posts"}
                </button>
              </div>
            )}
          </div>

          {status && <p className="sync-status">{status}</p>}
        </>
      ) : (
        <div className="medium-placeholder">
          <div className="medium-placeholder-mark">M</div>
          <div>
            <strong>Medium integration coming soon</strong>
            <p>
              Your Medium articles, publishing statistics and recommendations
              will appear here once connected.
            </p>
          </div>
        </div>
      )}

      <SuggestionsPanel platform={platform} />
    </section>
  );
}
