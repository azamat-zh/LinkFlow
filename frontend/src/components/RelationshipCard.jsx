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

export default function RelationshipCard({ relationship: rel, onLogSession }) {
  const [open, setOpen] = useState(false);
  const [notes, setNotes] = useState("");
  const [loggedBy, setLoggedBy] = useState("");
  const [submitting, setSubmitting] = useState(false);

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
    <div className="card" style={{ marginBottom: 12 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 6 }}>
        <span style={{ fontWeight: 600, fontSize: 14 }}>
          {rel.actor_a_id} ↔ {rel.actor_b_id}
        </span>
        <span className={`badge ${STATE_BADGE[rel.state] || ""}`}>{rel.state}</span>
      </div>

      <p style={{ margin: "0 0 4px", fontSize: 13, color: "var(--text-muted)" }}>
        {rel.relationship_type.replace("_", " ")}
      </p>

      <p style={{ margin: "0 0 10px", fontSize: 12, color: "var(--text-muted)" }}>
        Created {fmt(rel.created_at)} · Updated {fmt(rel.last_updated)}
      </p>

      {!open && (
        <button className="btn" style={{ fontSize: 13 }} onClick={() => setOpen(true)}>
          Log Session
        </button>
      )}

      {open && (
        <form onSubmit={handleSubmit} style={{ marginTop: 8 }}>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Session notes…"
            rows={3}
            style={{ width: "100%", boxSizing: "border-box", marginBottom: 6 }}
          />
          <input
            value={loggedBy}
            onChange={(e) => setLoggedBy(e.target.value)}
            placeholder="Logged by (optional)"
            style={{ width: "100%", boxSizing: "border-box", marginBottom: 6 }}
          />
          <div style={{ display: "flex", gap: 6 }}>
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
