import { useEffect, useState } from "react";
import { approveMatch, getActors, matchActors } from "../api/client";
import MatchCard from "../components/MatchCard";

const TARGET_TYPES = [
  { value: "mentor",           label: "Mentor" },
  { value: "company",          label: "Company" },
  { value: "partner",          label: "Partner" },
  { value: "service_provider", label: "Service Provider" },
];

export default function Chat() {
  const [query, setQuery] = useState("");
  const [targetType, setTargetType] = useState("mentor");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [approved, setApproved] = useState(new Set());

  const [companies, setCompanies] = useState([]);
  const [selectedCompanyId, setSelectedCompanyId] = useState("");

  useEffect(() => {
    getActors("company").then((list) => {
      setCompanies(list);
      if (list.length > 0) setSelectedCompanyId(list[0].id);
    }).catch(() => {});
  }, []);

  async function handleSend() {
    if (!query.trim()) return;
    if (!selectedCompanyId) {
      alert("Please onboard at least one company first, then search for matches.");
      return;
    }
    setLoading(true);
    setResults([]);
    try {
      const matches = await matchActors(query, targetType, "default");
      setResults(matches);
    } catch (err) {
      setResults([]);
    } finally {
      setLoading(false);
    }
  }

  async function handleApprove(match) {
    if (!selectedCompanyId) {
      alert("Select a company to match with first.");
      return;
    }
    try {
      await approveMatch(match.actor_id, selectedCompanyId, match.score, match.reasoning, "default");
      setApproved((prev) => new Set([...prev, match.actor_id]));
    } catch (err) {
      alert("Failed to approve match: " + err.message);
    }
  }

  return (
    <div className="page-container" style={{ maxWidth: 860, margin: "0 auto" }}>
      <h2 className="page-title">AI Matchmaker</h2>

      {/* Step 1 — pick the company */}
      <div className="card" style={{ marginBottom: 16 }}>
        <p style={{ margin: "0 0 8px", fontSize: 13, fontWeight: 600, color: "var(--text-muted)" }}>
          STEP 1 — Which company are you finding a match for?
        </p>
        {companies.length === 0 ? (
          <p style={{ margin: 0, fontSize: 14, color: "var(--danger)" }}>
            No companies onboarded yet. Go to the Onboard page and upload a company pitch deck first.
          </p>
        ) : (
          <select
            value={selectedCompanyId}
            onChange={(e) => setSelectedCompanyId(e.target.value)}
            style={{ width: "100%", padding: "8px 12px", borderRadius: "var(--radius)", border: "1px solid var(--border)", background: "var(--bg)", fontSize: 14, color: "var(--text)", cursor: "pointer" }}
          >
            {companies.map((c) => (
              <option key={c.id} value={c.id}>{c.name} — {c.sector} · {c.stage}</option>
            ))}
          </select>
        )}
      </div>

      {/* Step 2 — search */}
      <div className="card" style={{ marginBottom: 24 }}>
        <p style={{ margin: "0 0 8px", fontSize: 13, fontWeight: 600, color: "var(--text-muted)" }}>
          STEP 2 — Find a match
        </p>
        <div style={{ display: "flex", gap: 10 }}>
          <select
            value={targetType}
            onChange={(e) => setTargetType(e.target.value)}
            style={{ padding: "8px 12px", borderRadius: "var(--radius)", border: "1px solid var(--border)", background: "var(--bg)", fontSize: 14, color: "var(--text)", cursor: "pointer" }}
          >
            {TARGET_TYPES.map((t) => (
              <option key={t.value} value={t.value}>{t.label}</option>
            ))}
          </select>

          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder={`e.g. "Find ${targetType}s with fintech experience for seed-stage startups"`}
            style={{ flex: 1 }}
          />

          <button className="btn btn-primary" onClick={handleSend} disabled={loading || !selectedCompanyId}>
            {loading ? "Searching…" : "✨ Find Match"}
          </button>
        </div>
      </div>

      {results.length === 0 && !loading && (
        <div style={{ textAlign: "center", padding: "4rem 0", color: "var(--text-muted)" }}>
          <div style={{ fontSize: 48, marginBottom: 12 }}>🤝</div>
          <p style={{ fontSize: 16, margin: 0 }}>Select a company and enter a query to find matches.</p>
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
