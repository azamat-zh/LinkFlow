import { useEffect, useState } from "react";
import { getActors, getRelationships, getStaleRelationships, logSession } from "../api/client";
import RelationshipCard from "../components/RelationshipCard";

function MetricCard({ label, value }) {
  return (
    <div className="metric-card">
      <div className="value">{value}</div>
      <div className="label">{label}</div>
    </div>
  );
}

export default function Dashboard() {
  const [actors, setActors] = useState([]);
  const [rels, setRels] = useState([]);
  const [stale, setStale] = useState([]);
  const [checkingStale, setCheckingStale] = useState(false);
  const [copiedId, setCopiedId] = useState(null);

  useEffect(() => {
    getActors().then(setActors).catch(() => {});
    getRelationships().then(setRels).catch(() => {});
  }, []);

  // Create a map of IDs to Names for trustworthy display
  const actorMap = actors.reduce((acc, actor) => {
    acc[actor.id] = actor.name;
    return acc;
  }, {});

  async function handleLogSession(relId, notes, loggedBy) {
    const updated = await logSession(relId, notes, loggedBy);
    setRels((prev) => prev.map((r) => (r.id === relId ? updated : r)));
  }

  async function handleCheckStale() {
    setCheckingStale(true);
    try {
      const data = await getStaleRelationships();
      setStale(data);
    } finally {
      setCheckingStale(false);
    }
  }

  function handleCopy(text, id) {
    navigator.clipboard.writeText(text).then(() => {
      setCopiedId(id);
      setTimeout(() => setCopiedId(null), 2000);
    });
  }

  const companies = actors.filter((a) => a.actor_type === "company").length;
  const mentors = actors.filter((a) => a.actor_type === "mentor").length;
  const partners = actors.filter((a) => a.actor_type === "partner").length;
  const activeRels = rels.filter((r) => r.state === "active").length;

  return (
    <div className="three-col page-container">
      <div>
        <h2 className="page-title">Metrics</h2>
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          <MetricCard label="Total Companies" value={companies} />
          <MetricCard label="Total Mentors" value={mentors} />
          <MetricCard label="Total Partners" value={partners} />
          <MetricCard label="Active Relationships" value={activeRels} />
        </div>
      </div>

      <div>
        <h2 className="page-title">All Relationships</h2>
        {rels.length === 0
          ? <p style={{ color: "var(--text-muted)" }}>No relationships yet.</p>
          : rels.map((rel) => (
            <RelationshipCard 
              key={rel.id} 
              relationship={rel} 
              actorMap={actorMap}
              onLogSession={handleLogSession} 
            />
          ))
        }
      </div>

      <div>
        <h2 className="page-title">Needs Attention</h2>
        <button className="btn btn-primary" onClick={handleCheckStale} disabled={checkingStale}>
          {checkingStale ? "Checking…" : "🔍 Check Stale"}
        </button>

        {stale.length === 0 && !checkingStale && (
          <p style={{ color: "var(--text-muted)", marginTop: 16, fontSize: 14 }}>
            Click to check for relationships with no activity in 14 days.
          </p>
        )}

        {stale.map((item, i) => (
          <div key={i} className="card" style={{ marginTop: 16 }}>
            <p style={{ margin: "0 0 4px", fontWeight: 600, fontSize: 14 }}>
              {actorMap[item.relationship.actor_a_id] || "Unknown"} ↔ {actorMap[item.relationship.actor_b_id] || "Unknown"}
            </p>
            <p style={{ margin: "0 0 12px", fontSize: 13, color: "var(--text-muted)" }}>
              Last updated: {new Date(item.relationship.last_updated).toLocaleDateString()}
            </p>
            <div style={{
              background: "var(--amber-light)",
              borderRadius: "var(--radius)",
              padding: "12px 14px",
              fontSize: 13,
              marginBottom: 12,
              border: "1px solid rgba(217, 119, 6, 0.2)"
            }}>
              💬 {item.nudge_message}
            </div>
            <button
              className="btn"
              style={{ fontSize: 13 }}
              onClick={() => handleCopy(item.nudge_message, i)}
            >
              {copiedId === i ? "✓ Copied!" : "Copy message"}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}