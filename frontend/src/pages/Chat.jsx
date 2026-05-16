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
    <div style={{ padding: "2rem", maxWidth: 800, margin: "0 auto" }}>
      <h2 style={{ marginTop: 0 }}>AI Match</h2>

      <div style={{ display: "flex", gap: 10, marginBottom: 24 }}>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder='Try: "Find mentors with fintech experience for seed-stage startups"'
          style={{ flex: 1 }}
        />
        <button className="btn btn-primary" onClick={handleSend} disabled={loading}>
          {loading ? "Searching…" : "Send"}
        </button>
      </div>

      {results.length === 0 && !loading && (
        <p style={{ color: "var(--text-muted)" }}>
          Enter a query above to find matching actors.
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
