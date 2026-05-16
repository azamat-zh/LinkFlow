import { useState } from "react";
import { approveMatch, matchActors } from "../api/client";
import MatchCard from "../components/MatchCard";

export default function Chat() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [approved, setApproved] = useState(new Set());

  async function handleSend() {
    if (!query.trim()) return;
    setLoading(true);
    setResults([]);
    try {
      const matches = await matchActors(query, "mentor", "default");
      setResults(matches);
    } catch (err) {
      setResults([]);
    } finally {
      setLoading(false);
    }
  }

  async function handleApprove(match) {
    try {
      await approveMatch(match.actor_id, "default-requester", match.score, match.reasoning, "default");
      setApproved((prev) => new Set([...prev, match.actor_id]));
    } catch (err) {
      alert("Failed to approve match: " + err.message);
    }
  }

  return (
    <div className="page-container" style={{ maxWidth: 860, margin: "0 auto" }}>
      <h2 className="page-title">AI Matchmaker</h2>

      <div style={{ display: "flex", gap: 12, marginBottom: 32, background: "var(--bg-surface)", padding: "8px", borderRadius: "var(--radius-lg)", border: "1px solid var(--border)", boxShadow: "var(--shadow-sm)" }}>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder='Try: "Find mentors with fintech experience for seed-stage startups"'
          style={{ flex: 1, border: "none", background: "transparent", fontSize: 15 }}
        />
        <button className="btn btn-primary" onClick={handleSend} disabled={loading} style={{padding: "10px 24px"}}>
          {loading ? "Searching…" : "✨ Find Match"}
        </button>
      </div>

      {results.length === 0 && !loading && (
        <div style={{ textAlign: "center", padding: "4rem 0", color: "var(--text-muted)" }}>
          <div style={{ fontSize: 48, marginBottom: 12 }}>🤝</div>
          <p style={{ fontSize: 16, margin: 0 }}>Enter a query above to find matching actors.</p>
          <p style={{ fontSize: 14, margin: "4px 0 0" }}>Our AI will analyze profiles to find the best fits.</p>
        </div>
      )}

      {results.map((match) => (
        <MatchCard
          key={match.actor_id}
          match={match}
          approved={approved.has(match.actor_id)}
          onApprove={handleApprove}
        />
      ))}
    </div>
  );
}