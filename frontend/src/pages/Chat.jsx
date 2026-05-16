import { useState } from "react";
import { approveMatch, matchActors } from "../api/client";
import MatchCard from "../components/MatchCard";

export default function Chat() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [approved, setApproved] = useState(new Set());

  async function handleSend() {
    if (!query.trim()) return;
    setLoading(true);
    setResults([]);
    setSearched(true);
    try {
      const matches = await matchActors(query, "default");
      setResults(matches.filter((m) => m.score > 0));
    } catch (err) {
      setResults([]);
    } finally {
      setLoading(false);
    }
  }

  async function handleApprove(match) {
    try {
      await approveMatch(match.actor_id, match.actor_id, match.score, match.reasoning, "default");
      setApproved((prev) => new Set([...prev, match.actor_id]));
    } catch (err) {
      alert("Failed to approve match: " + err.message);
    }
  }

  return (
    <div className="page-container" style={{ maxWidth: 760, margin: "0 auto" }}>
      <h2 className="page-title">AI Matchmaker</h2>
      <p style={{ color: "var(--text-muted)", marginBottom: 24, fontSize: 15 }}>
        Describe the situation. The AI will find the right mentors, partners, and services from everyone in the ecosystem.
      </p>

      <div style={{ display: "flex", gap: 10, marginBottom: 32 }}>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder='e.g. "I have a SaaS startup struggling with expansion, need a mentor and cloud services"'
          style={{ flex: 1, fontSize: 15, padding: "12px 16px" }}
          autoFocus
        />
        <button
          className="btn btn-primary"
          onClick={handleSend}
          disabled={loading || !query.trim()}
          style={{ padding: "12px 28px", fontSize: 15, whiteSpace: "nowrap" }}
        >
          {loading ? "Finding…" : "Find Matches"}
        </button>
      </div>

      {loading && (
        <div style={{ textAlign: "center", padding: "3rem 0", color: "var(--text-muted)" }}>
          <p style={{ fontSize: 15 }}>Analysing all profiles…</p>
        </div>
      )}

      {!loading && searched && results.length === 0 && (
        <div style={{ textAlign: "center", padding: "3rem 0", color: "var(--text-muted)" }}>
          <p style={{ fontSize: 15 }}>No relevant matches found. Try rephrasing or onboard more actors.</p>
        </div>
      )}

      {!loading && !searched && (
        <div style={{ textAlign: "center", padding: "3rem 0", color: "var(--text-muted)" }}>
          <div style={{ fontSize: 40, marginBottom: 12 }}>🤝</div>
          <p style={{ fontSize: 15, margin: 0 }}>Describe what you need and hit Find Matches.</p>
        </div>
      )}

      {results.length > 0 && (
        <p style={{ fontSize: 13, color: "var(--text-muted)", marginBottom: 12 }}>
          {results.length} match{results.length > 1 ? "es" : ""} found — sorted by relevance
        </p>
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
