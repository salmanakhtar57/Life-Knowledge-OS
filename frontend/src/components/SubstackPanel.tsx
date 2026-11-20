import { useState } from "react";
import { syncSubstack } from "../api/client";

export function SubstackPanel() {
  const [url, setUrl] = useState("");
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSync() {
    if (!url.trim()) {
      setStatus("Enter a Substack URL.");
      return;
    }
    setLoading(true);
    setStatus("Syncing…");
    try {
      const r = await syncSubstack(url.trim());
      setStatus(
        `Fetched ${r.fetched} · ${r.new} new · ${r.skipped_duplicates} already stored · ${r.skipped_empty} too short`
      );
    } catch (e) {
      setStatus(e instanceof Error ? e.message : "Could not reach the server.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="substack-panel">
      <label>Add a Substack</label>
      <div>
        <input
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="yourname.substack.com"
        />
        <button type="button" onClick={handleSync} disabled={loading}>
          {loading ? "Syncing…" : "Sync"}
        </button>
      </div>
      {status && <p>{status}</p>}
    </section>
  );
}