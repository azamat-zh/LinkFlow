import { useEffect, useState } from "react";
import { getActors, getRelationships, getStaleRelationships } from "../api/client";
import RelationshipCard from "../components/RelationshipCard";

function MetricCard({ label, value, highlight }) {
  return (
    <div className="metric-card" style={highlight ? { borderLeft: "3px solid var(--danger)" } : {}}>
      <div className="value" style={{ fontSize: 22, color: highlight ? "var(--danger)" : undefined }}>{value}</div>
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

  const actorMap = actors.reduce((acc, a) => { acc[a.id] = a.name; return acc; }, {});

  function handleRelUpdate(updated) {
    setRels((prev) => prev.map((r) => (r.id === updated.id ? updated : r)));
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

  const companies  = actors.filter((a) => a.actor_type === "company").length;
  const mentors    = actors.filter((a) => a.actor_type === "mentor").length;
  const partners   = actors.filter((a) => a.actor_type === "partner").length;
  const activeRels = rels.filter((r) => r.state === "active").length;
  const pendingRels = rels.filter((r) => r.state === "pending").length;

  const staleRels = rels.filter((r) => {
    if (r.state !== "active") return false;
    return new Date(r.last_updated) < new Date(Date.now() - 14 * 24 * 60 * 60 * 1000);
  });

  return (
    <div className="three-col page-container">

      {/* Left: metrics */}
      <div>
        <h2 className="page-title">Metrics</h2>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
          <MetricCard label="Companies"   value={companies} />
          <MetricCard label="Mentors"     value={mentors} />
          <MetricCard label="Partners"    value={partners} />
          <MetricCard label="Active"      value={activeRels} />
          <MetricCard label="Pending"     value={pendingRels} />
          <MetricCard label="Stale"       value={staleRels.length} highlight={staleRels.length > 0} />
        </div>
      </div>

      {/* Center: all relationships */}
      <div>
        <h2 className="page-title">All Relationships</h2>
        {rels.length === 0
          ? <p style={{ color: "var(--text-muted)" }}>No relationships yet. Approve a match to create one.</p>
          : rels.map((rel) => (
            <RelationshipCard
              key={rel.id}
              relationship={rel}
              actorMap={actorMap}
              onUpdate={handleRelUpdate}
            />
          ))
        }
      </div>

      {/* Right: stale / needs attention */}
      <div>
        <h2 className="page-title">Needs Attention</h2>
        <p style={{ fontSize: 13, color: "var(--text-muted)", marginBottom: 12 }}>
          Relationships with no session activity for 14+ days.
        </p>
        <button className="btn btn-primary" onClick={handleCheckStale} disabled={checkingStale} style={{ marginBottom: 16 }}>
          {checkingStale ? "Checking…" : "🔍 Check Stale"}
        </button>

        {stale.length === 0 && !checkingStale && (
          <p style={{ color: "var(--text-muted)", fontSize: 14 }}>
            Click to scan for stale relationships.
          </p>
        )}

        {stale.map((item, i) => {
          const relData = item.relationship;
          const nameA = actorMap[relData.actor_a_id] || relData.actor_a_id?.slice(0, 8) + "…";
          const nameB = actorMap[relData.actor_b_id] || relData.actor_b_id?.slice(0, 8) + "…";
          return (
            <div key={i} className="card" style={{ marginBottom: 14, borderLeft: "3px solid var(--danger)" }}>
              <p style={{ margin: "0 0 2px", fontWeight: 600, fontSize: 14 }}>
                {nameA} ↔ {nameB}
              </p>
              <p style={{ margin: "0 0 10px", fontSize: 12, color: "var(--text-muted)" }}>
                Last activity: {new Date(relData.last_updated).toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" })}
              </p>
              {item.nudge_message && (
                <div style={{
                  background: "var(--amber-light)",
                  borderRadius: "var(--radius)",
                  padding: "10px 12px",
                  fontSize: 13,
                  marginBottom: 10,
                }}>
                  💬 {item.nudge_message}
                </div>
              )}
              <button
                className="btn"
                style={{ fontSize: 12 }}
                onClick={() => {
                  navigator.clipboard.writeText(item.nudge_message || "").then(() => {
                    setCopiedId(i);
                    setTimeout(() => setCopiedId(null), 2000);
                  });
                }}
              >
                {copiedId === i ? "✓ Copied" : "Copy message"}
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}
