
import type { StatsResponse } from "../types/api";

interface ProfileBannerProps {
  stats: StatsResponse | null;
  loading: boolean;
}

function formatDate(value: string | null): string {
  if (!value) return "No posts yet";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) return "—";

  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "2-digit",
    year: "numeric",
  }).format(date);
}

export function ProfileBanner({ stats, loading }: ProfileBannerProps) {
  const days = stats?.days_since_last_post;

  return (
    <section className="profile-banner">
      <div className="profile-identity">
        <div className="avatar">SA</div>

        <div>
          <h1>Salman Akhtar</h1>
          <p>Python Developer <span>•</span> Writer <span>•</span> Lifelong Learner</p>
        </div>
      </div>

      <div className="profile-metrics">
        <div className="metric">
          <svg viewBox="0 0 24 24" fill="none">
            <path d="m14 5 5 5M4 20l4.5-1 10-10a2.12 2.12 0 0 0-3-3l-10 10L4 20Z" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          <strong>{loading ? "—" : stats?.substack_posts ?? "—"}</strong>
          <span>Substack</span>
          <small>Posts</small>
        </div>

        <div className="metric">
          <span className="medium-letter">M</span>
          <strong>—</strong>
          <span>Medium</span>
          <small>Coming soon</small>
        </div>

        <div className="metric">
          <svg viewBox="0 0 24 24" fill="none">
            <rect x="5" y="3" width="14" height="18" rx="2" stroke="currentColor" strokeWidth="1.8" />
            <path d="M9 3v3m6-3v3M8 10h8m-8 4h8m-8 4h5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
          </svg>
          <strong>{loading ? "—" : stats?.faq_documents ?? "—"}</strong>
          <span>Pages</span>
        </div>
      </div>

      <div className="last-published">
        <svg viewBox="0 0 24 24" fill="none">
          <rect x="3" y="5" width="18" height="16" rx="2" stroke="currentColor" strokeWidth="1.8" />
          <path d="M7 3v4m10-4v4M3 10h18m-12 4h2m3 0h2m-7 3h2" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
        </svg>
        <span>Last published</span>
        <strong>{loading ? "Loading..." : formatDate(stats?.last_published_at ?? null)}</strong>
        <small>
          {days === null || days === undefined
            ? " "
            : days === 0
              ? "Today"
              : days === 1
                ? "(1 day ago)"
                : `(${days} days ago)`}
        </small>
      </div>
    </section>
  );
}
