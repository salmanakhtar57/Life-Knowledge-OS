
import { useCallback, useEffect, useState } from "react";

import { getLatestPosts, getStats } from "./api/client";
import type { Post, StatsResponse } from "./types/api";
import { PublicationPanel } from "./components/PublicationPanel";
import { Header } from "./components/Header";
import { ProfileBanner } from "./components/ProfileBanner";
import { AskYourWork } from "./components/AskYourWork";
import { UploadPanel } from "./components/UploadPanel";

export default function App() {
  const [darkMode, setDarkMode] = useState(false);

  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [posts, setPosts] = useState<Post[]>([]);

  const [loadingStats, setLoadingStats] = useState(true);
  const [loadingPosts, setLoadingPosts] = useState(true);

  const [dashboardError, setDashboardError] = useState("");

  useEffect(() => {
    document.documentElement.dataset.theme = darkMode ? "dark" : "light";
  }, [darkMode]);

  const refreshStats = useCallback(async () => {
    try {
      const result = await getStats();
      setStats(result);
    } catch (error) {
      setDashboardError(
        error instanceof Error ? error.message : "Could not load statistics.",
      );
    } finally {
      setLoadingStats(false);
    }
  }, []);

  const refreshPosts = useCallback(async () => {
    try {
      const result = await getLatestPosts();
      setPosts(result);
    } catch (error) {
      setDashboardError(
        error instanceof Error ? error.message : "Could not load posts.",
      );
    } finally {
      setLoadingPosts(false);
    }
  }, []);

  const refreshDashboard = useCallback(async () => {
    await Promise.all([refreshStats(), refreshPosts()]);
  }, [refreshStats, refreshPosts]);

  useEffect(() => {
    void refreshDashboard();
  }, [refreshDashboard]);

  return (
    <main className="dashboard">
      <Header
        darkMode={darkMode}
        onToggleTheme={() => setDarkMode((value) => !value)}
      />

      <ProfileBanner stats={stats} loading={loadingStats} />

      {dashboardError && (
        <div className="dashboard-error" role="alert">
          {dashboardError}
          <button type="button" onClick={() => {
            setDashboardError("");
            setLoadingStats(true);
            setLoadingPosts(true);
            void refreshDashboard();
          }}>
            Retry
          </button>
        </div>
      )}

      <section className="publication-grid">
        <PublicationPanel
          platform="substack"
          posts={posts}
          onPostsUpdated={setPosts}
          onSynced={refreshDashboard}
        />

        <PublicationPanel
          platform="medium"
          posts={[]}
          onPostsUpdated={() => undefined}
          onSynced={refreshDashboard}
        />
      </section>

      {loadingPosts && (
        <p className="loading-note">Loading your latest Substack posts...</p>
      )}

      <AskYourWork />

      <details className="knowledge-management">
        <summary>Manage your knowledge · Upload a document</summary>
        <div className="knowledge-management-content">
          <UploadPanel />
        </div>
      </details>

      <footer className="dashboard-footer">
        <span>Noteway</span>
        <span>Your writing, ideas and knowledge in one place.</span>
      </footer>
    </main>
  );
}
