
import { useCallback, useEffect, useState } from "react";

import {
  getLatestPosts,
  getLatestMediumPosts,
  getStats,
} from "./api/client";
import type { Post, StatsResponse } from "./types/api";
import { PublicationPanel } from "./components/PublicationPanel";
import { Header } from "./components/Header";
import { ProfileBanner } from "./components/ProfileBanner";
import { AskYourWork } from "./components/AskYourWork";
import { UploadPanel } from "./components/UploadPanel";

type Theme = "light" | "dark" | "system";

export default function App() {
  const [theme, setTheme] = useState<Theme>(() => {
    const savedTheme = localStorage.getItem("theme");

    if (
      savedTheme === "light" ||
      savedTheme === "dark" ||
      savedTheme === "system"
    ) {
      return savedTheme;
    }

    return "system";
  });

  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [posts, setPosts] = useState<Post[]>([]);
  const [mediumPosts, setMediumPosts] = useState<Post[]>([]);

  const [loadingStats, setLoadingStats] = useState(true);
  const [loadingPosts, setLoadingPosts] = useState(true);
  const [loadingMediumPosts, setLoadingMediumPosts] = useState(true);

  const [dashboardError, setDashboardError] = useState("");

  // Theme handling
  useEffect(() => {
    localStorage.setItem("theme", theme);

    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");

    const applyTheme = () => {
      const isDark =
        theme === "dark" ||
        (theme === "system" && mediaQuery.matches);

      document.documentElement.dataset.theme = isDark ? "dark" : "light";
    };

    applyTheme();

    if (theme === "system") {
      mediaQuery.addEventListener("change", applyTheme);

      return () => {
        mediaQuery.removeEventListener("change", applyTheme);
      };
    }
  }, [theme]);

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
        error instanceof Error ? error.message : "Could not load Substack posts.",
      );
    } finally {
      setLoadingPosts(false);
    }
  }, []);

  const refreshMediumPosts = useCallback(async () => {
    try {
      const result = await getLatestMediumPosts();
      setMediumPosts(result);
    } catch (error) {
      setDashboardError(
        error instanceof Error ? error.message : "Could not load Medium posts.",
      );
    } finally {
      setLoadingMediumPosts(false);
    }
  }, []);

  const refreshDashboard = useCallback(async () => {
    await Promise.all([
      refreshStats(),
      refreshPosts(),
      refreshMediumPosts(),
    ]);
  }, [refreshStats, refreshPosts, refreshMediumPosts]);

  useEffect(() => {
    void refreshDashboard();
  }, [refreshDashboard]);

  function handleRetry() {
    setDashboardError("");
    setLoadingStats(true);
    setLoadingPosts(true);
    setLoadingMediumPosts(true);
    void refreshDashboard();
  }

  return (
    <main className="dashboard">
      <Header theme={theme} onThemeChange={setTheme} />

      <ProfileBanner stats={stats} loading={loadingStats} />

      {dashboardError && (
        <div className="dashboard-error" role="alert">
          {dashboardError}
          <button type="button" onClick={handleRetry}>
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
          posts={mediumPosts}
          onPostsUpdated={setMediumPosts}
          onSynced={refreshDashboard}
        />
      </section>

      {loadingPosts && (
        <p className="loading-note">Loading your latest Substack posts...</p>
      )}

      {loadingMediumPosts && (
        <p className="loading-note">Loading your latest Medium posts...</p>
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
