import { useEffect, useState } from "react";
import { approveMatch, getActors, matchActors } from "../api/client";
import MatchCard from "../components/MatchCard";

const ALL_TYPES = [
  { value: "mentor",           label: "Mentor" },
  { value: "company",          label: "Company" },
  { value: "partner",          label: "Partner" },
  { value: "service_provider", label: "Service Provider" },
];

export default function Chat() {
  // Step 1 — category + actor selection
  const [focusType, setFocusType] = useState("mentor");
  const [actorList, setActorList] = useState([]);
  const [selectedActorId, setSelectedActorId] = useState("");
  const [loadingActors, setLoadingActors] = useState(false);

  // Step 2 — query + results
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [approved, setApproved] = useState(new Set());

  // Load actors whenever the focus type changes
  useEffect(() => {
    setActorList([]);
    setSelectedActorId("");
    setResults([]);
    setLoadingActors(true);
    getActors(focusType)
      .then((list) => {
        setActorList(list);
        if (list.length > 0) setSelectedActorId(list[0].id);
      })
      .catch(() => {})
      .finally(() => setLoadingActors(false));
  }, [focusType]);

  const selectedActor = actorList.find((a) => a.id === selectedActorId);
  const otherTypes = ALL_TYPES.filter((t) => t.value !== focusType);

  async function handleSend() {
    if (!selectedActorId) return;
    const q = query.trim() ||
      `Find the best matches for ${selectedActor?.name || "this actor"} in the ecosystem`;
    setLoading(true);
    setResults([]);
    try {
      // Search all other categories in parallel and merge results
      const allResults = await Promise.all(
        otherTypes.map((t) => matchActors(q, t.value, "default").catch(() => []))
      );
      const merged = allResults
        .flat()
        .filter((m) => m.score > 0)
        .sort((a, b) => b.score - a.score);
      setResults(merged);
    } finally {
      setLoading(false);
    }
  }

  async function handleApprove(match) {
    try {
      await approveMatch(selectedActorId, match.actor_id, match.score, match.reasoning, "default");
      setApproved((prev) => new Set([...prev, match.actor_id]));
    } catch (err) {
      alert("Failed to approve match: " + err.message);
    }
  }

  return (
    <div className="page-container" style={{ maxWidth: 860, margin: "0 auto" }}>
      <h2 className="page-title">AI Matchmaker</h2>

      {/* Step 1 */}
      <div className="card" style={{ marginBottom: 16 }}>
        <p style={{ margin: "0 0 10px", fontSize: 13, fontWeight: 600, color: "var(--text-muted)" }}>
          STEP 1 — Select who you are finding matches for
        </p>
        <div style={{ display: "flex", gap: 10 }}>
          <select
            value={focusType}
            onChange={(e) => setFocusType(e.target.value)}
            style={{ padding: "8px 12px", borderRadius: "var(--radius)", border: "1px solid var(--border)", background: "var(--bg)", fontSize: 14, color: "var(--text)", cursor: "pointer" }}
          >
            {ALL_TYPES.map((t) => (
              <option key={t.value} value={t.value}>{t.label}</option>
            ))}
          </select>

          {loadingActors ? (
            <p style={{ margin: "auto 0", fontSize: 14, color: "var(--text-muted)" }}>Loading…</p>
          ) : actorList.length === 0 ? (
            <p style={{ margin: "auto 0", fontSize: 14, color: "var(--danger)" }}>
              No {focusType.replace("_", " ")}s onboarded yet — go to Onboard page first.
            </p>
          ) : (
            <select
              value={selectedActorId}
              onChange={(e) => setSelectedActorId(e.target.value)}
              style={{ flex: 1, padding: "8px 12px", borderRadius: "var(--radius)", border: "1px solid var(--border)", background: "var(--bg)", fontSize: 14, color: "var(--text)", cursor: "pointer" }}
            >
              {actorList.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.name} — {a.sector} · {a.stage}
                </option>
              ))}
            </select>
          )}
        </div>

        {selectedActor && (
          <p style={{ margin: "10px 0 0", fontSize: 13, color: "var(--text-muted)" }}>
            Will search across: <strong>{otherTypes.map((t) => t.label).join(", ")}</strong>
          </p>
        )}
      </div>

      {/* Step 2 */}
      <div className="card" style={{ marginBottom: 24 }}>
        <p style={{ margin: "0 0 10px", fontSize: 13, fontWeight: 600, color: "var(--text-muted)" }}>
          STEP 2 — Describe what you're looking for (or leave blank for auto)
        </p>
        <div style={{ display: "flex", gap: 10 }}>
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder={`e.g. "Looking for fintech expertise and B2B sales mentoring"`}
            style={{ flex: 1 }}
            disabled={!selectedActorId}
          />
          <button
            className="btn btn-primary"
            onClick={handleSend}
            disabled={loading || !selectedActorId}
          >
            {loading ? "Searching…" : "✨ Find Matches"}
          </button>
        </div>
      </div>

      {results.length === 0 && !loading && (
        <div style={{ textAlign: "center", padding: "4rem 0", color: "var(--text-muted)" }}>
          <div style={{ fontSize: 48, marginBottom: 12 }}>🤝</div>
          <p style={{ fontSize: 16, margin: 0 }}>Select an actor above and click Find Matches.</p>
          <p style={{ fontSize: 14, margin: "4px 0 0" }}>
            All other categories will be searched and ranked by fit.
          </p>
        </div>
      )}

      {results.length > 0 && (
        <p style={{ fontSize: 13, color: "var(--text-muted)", marginBottom: 12 }}>
          {results.length} matches found across {otherTypes.map((t) => t.label).join(", ")} — sorted by score
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
