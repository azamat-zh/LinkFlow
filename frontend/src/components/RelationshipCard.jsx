import { useState } from "react";

const STATE_BADGE = {
  pending: "badge--pending",
  active: "badge--active",
  stale: "badge--stale",
  completed: "badge--completed",
  closed: "badge--closed",
};

function fmt(dateStr) {
  if (!dateStr) return "—";
  return new Date(dateStr).toLocaleDateString("en-GB", {
    day: "numeric", month: "short", year: "numeric",
  });
}

export default function RelationshipCard({ relationship: rel, actorMap = {}, onLogSession }) {
  const [open, setOpen] = useState(false);
  const [notes, setNotes] = useState("");
  const [loggedBy, setLoggedBy] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const nameA = actorMap[rel.actor_a_id] || rel.actor_a_id.substring(0, 8) + "...";
  const nameB = actorMap[rel.actor_b_id] || rel.actor_b_id.substring(0, 8) + "...";

  async function handleSubmit(e) {
    e.preventDefault();
    if (!notes.trim()) return;
    setSubmitting(true);
    await onLogSession(rel.id, notes, loggedBy || "admin");
    setNotes("");
    setLoggedBy("");
    setOpen(false);
    setSubmitting(false);
  }

  return (
    <div className="card" style={{ marginBottom: 16 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
        <span style={{ fontWeight: 600, fontSize: 15 }}>
          {nameA} ↔ {nameB}
        </span>
        <span className={`badge ${STATE_BADGE[rel.state] || ""}`}>{rel.state}</span>
      </div>

      <p style={{ margin: "0 0 4px", fontSize: 13, color: "var(--text-muted)", textTransform: "capitalize" }}>
        {rel.relationship_type.replace("_", " ")}
      </p>

      <p style={{ margin: "0 0 12px", fontSize: 12, color: "var(--text-muted)" }}>
        Created {fmt(rel.created_at)} · Updated {fmt(rel.last_updated)}
      </p>

      {!open && (
        <button className="btn" style={{ fontSize: 13 }} onClick={() => setOpen(true)}>
          📝 Log Session
        </button>
      )}

      {open && (
        <form onSubmit={handleSubmit} style={{ marginTop: 8 }}>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Session notes…"
            rows={3}
            style={{ width: "100%", boxSizing: "border-box", marginBottom: 8 }}
          />
          <input
            value={loggedBy}
            onChange={(e) => setLoggedBy(e.target.value)}
            placeholder="Logged by (optional)"
            style={{ width: "100%", boxSizing: "border-box", marginBottom: 8 }}
          />
          <div style={{ display: "flex", gap: 8 }}>
            <button className="btn btn-primary" type="submit" disabled={submitting}>
              {submitting ? "Saving…" : "Submit"}
            </button>
            <button className="btn" type="button" onClick={() => setOpen(false)}>
              Cancel
            </button>
          </div>
        </form>
      )}
    </div>
  );
}