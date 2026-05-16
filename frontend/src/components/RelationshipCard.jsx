import { useState } from "react";
import { confirmActor, generateNudge, getRelationship, logSession, updateRelationshipState } from "../api/client";

const STATE_BADGE = {
  pending:   { cls: "badge--pending",   label: "Pending" },
  active:    { cls: "badge--active",    label: "Active" },
  stale:     { cls: "badge--stale",     label: "Stale" },
  completed: { cls: "badge--completed", label: "Completed" },
  closed:    { cls: "badge--closed",    label: "Closed" },
};

const TYPE_LABEL = {
  mentor_company:     "Mentor ↔ Company",
  partner_initiative: "Partner ↔ Initiative",
  company_programme:  "Company ↔ Programme",
};

function fmt(dateStr) {
  if (!dateStr) return "—";
  return new Date(dateStr).toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" });
}

function fmtFull(dateStr) {
  if (!dateStr) return "—";
  return new Date(dateStr).toLocaleString("en-GB", { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" });
}

function isStale(rel) {
  if (rel.state !== "active") return false;
  const cutoff = new Date(Date.now() - 14 * 24 * 60 * 60 * 1000);
  return new Date(rel.last_updated) < cutoff;
}

export default function RelationshipCard({ relationship: initialRel, actorMap = {}, onUpdate }) {
  const [rel, setRel] = useState(initialRel);
  const [showLogs, setShowLogs] = useState(false);
  const [noteText, setNoteText] = useState("");
  const [showNoteForm, setShowNoteForm] = useState(false);
  const [nudgeMsg, setNudgeMsg] = useState(null);
  const [loading, setLoading] = useState("");
  const [copiedNudge, setCopiedNudge] = useState(false);

  const stale = isStale(rel);
  const nameA = actorMap[rel.actor_a_id] || rel.actor_a_id.slice(0, 8) + "…";
  const nameB = actorMap[rel.actor_b_id] || rel.actor_b_id.slice(0, 8) + "…";
  const badge = STATE_BADGE[rel.state] || { cls: "", label: rel.state };

  async function mutate(action, fn) {
    setLoading(action);
    try {
      const updated = await fn();
      if (updated && updated.id) { setRel(updated); onUpdate?.(updated); }
      return updated;
    } finally { setLoading(""); }
  }

  async function handleConfirm(role) {
    await mutate(`confirm-${role}`, () => confirmActor(rel.id, role));
  }

  async function handleState(state) {
    await mutate(state, () => updateRelationshipState(rel.id, state));
  }

  async function handleAddNote(e) {
    e.preventDefault();
    if (!noteText.trim()) return;
    await mutate("note", () => logSession(rel.id, noteText.trim(), "coordinator"));
    setNoteText(""); setShowNoteForm(false);
  }

  async function handleNudge() {
    setLoading("nudge");
    try {
      const result = await generateNudge(rel.id);
      setNudgeMsg(result.nudge_message);
      const updated = await getRelationship(rel.id);
      setRel(updated); onUpdate?.(updated);
    } finally { setLoading(""); }
  }

  return (
    <div className="card" style={{ marginBottom: 14, borderLeft: stale ? "3px solid var(--danger)" : undefined }}>

      {/* Header */}
      <div style={{ marginBottom: 8 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap", marginBottom: 4 }}>
          <span style={{ fontWeight: 700, fontSize: 15 }}>{nameA}</span>
          <span style={{ color: "var(--text-muted)" }}>↔</span>
          <span style={{ fontWeight: 700, fontSize: 15 }}>{nameB}</span>
          <span className={`badge ${badge.cls}`}>{badge.label}</span>
          {stale && <span className="badge badge--stale">⚠ Stale</span>}
        </div>
        <div style={{ fontSize: 12, color: "var(--text-muted)", display: "flex", gap: 14, flexWrap: "wrap" }}>
          <span>{TYPE_LABEL[rel.relationship_type] || rel.relationship_type}</span>
          {rel.match_score > 0 && <span>Score: <strong>{rel.match_score}</strong></span>}
          <span>Updated: {fmt(rel.last_updated)}</span>
          <span>Created: {fmt(rel.created_at)}</span>
        </div>
      </div>

      {/* Match reasoning */}
      {rel.match_reasoning && (
        <p style={{ margin: "0 0 10px", fontSize: 13, color: "var(--text-muted)", fontStyle: "italic" }}>
          "{rel.match_reasoning}"
        </p>
      )}

      {/* Confirmation status — pending only */}
      {rel.state === "pending" && (
        <div style={{ display: "flex", gap: 12, marginBottom: 10, padding: "8px 10px", background: "var(--bg-surface)", borderRadius: "var(--radius)", fontSize: 12 }}>
          <span style={{ fontWeight: 600, color: "var(--text-muted)" }}>Confirmations:</span>
          <span>Mentor {rel.mentor_confirmed ? "✅" : "⏳"}</span>
          <span>Startup {rel.startup_confirmed ? "✅" : "⏳"}</span>
        </div>
      )}

      {/* Actions */}
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        {rel.state === "pending" && !rel.mentor_confirmed && (
          <button className="btn" style={{ fontSize: 12 }} disabled={!!loading} onClick={() => handleConfirm("mentor")}>
            {loading === "confirm-mentor" ? "…" : "✓ Mentor Confirmed"}
          </button>
        )}
        {rel.state === "pending" && !rel.startup_confirmed && (
          <button className="btn" style={{ fontSize: 12 }} disabled={!!loading} onClick={() => handleConfirm("startup")}>
            {loading === "confirm-startup" ? "…" : "✓ Startup Confirmed"}
          </button>
        )}
        {rel.state === "pending" && (
          <button className="btn btn-primary" style={{ fontSize: 12 }} disabled={!!loading} onClick={() => handleState("active")}>
            {loading === "active" ? "…" : "Mark Active"}
          </button>
        )}
        {(rel.state === "active" || stale) && (
          <>
            <button className="btn" style={{ fontSize: 12 }} onClick={() => setShowNoteForm((v) => !v)}>
              + Add Note
            </button>
            <button className="btn" style={{ fontSize: 12 }} disabled={!!loading} onClick={handleNudge}>
              {loading === "nudge" ? "Generating…" : "💬 Nudge"}
            </button>
            <button className="btn" style={{ fontSize: 12 }} disabled={!!loading} onClick={() => handleState("completed")}>
              {loading === "completed" ? "…" : "Mark Completed"}
            </button>
          </>
        )}
        <button className="btn" style={{ fontSize: 12, marginLeft: "auto" }} onClick={() => setShowLogs((v) => !v)}>
          {showLogs ? "Hide Log" : `Log (${rel.session_log.length})`}
        </button>
      </div>

      {/* Add note form */}
      {showNoteForm && (
        <form onSubmit={handleAddNote} style={{ marginTop: 10 }}>
          <textarea
            value={noteText}
            onChange={(e) => setNoteText(e.target.value)}
            placeholder="Session notes…"
            rows={2}
            style={{ width: "100%", boxSizing: "border-box", marginBottom: 6, fontSize: 13 }}
          />
          <div style={{ display: "flex", gap: 6 }}>
            <button className="btn btn-primary" type="submit" disabled={loading === "note"} style={{ fontSize: 12 }}>
              {loading === "note" ? "Saving…" : "Save Note"}
            </button>
            <button className="btn" type="button" style={{ fontSize: 12 }} onClick={() => setShowNoteForm(false)}>Cancel</button>
          </div>
        </form>
      )}

      {/* Nudge result */}
      {nudgeMsg && (
        <div style={{ marginTop: 10, padding: "10px 12px", background: "var(--amber-light)", borderRadius: "var(--radius)", fontSize: 13 }}>
          <strong style={{ display: "block", marginBottom: 4, fontSize: 11, color: "var(--amber)" }}>GENERATED NUDGE</strong>
          {nudgeMsg}
          <button className="btn" style={{ marginTop: 6, fontSize: 12 }} onClick={() => navigator.clipboard.writeText(nudgeMsg).then(() => setCopiedNudge(true))}>
            {copiedNudge ? "✓ Copied" : "Copy"}
          </button>
        </div>
      )}

      {/* Session log */}
      {showLogs && (
        <div style={{ marginTop: 12, borderTop: "1px solid var(--border)", paddingTop: 10 }}>
          <p style={{ margin: "0 0 8px", fontSize: 11, fontWeight: 600, color: "var(--text-muted)" }}>SESSION LOG</p>
          {rel.session_log.length === 0
            ? <p style={{ fontSize: 13, color: "var(--text-muted)" }}>No entries yet.</p>
            : [...rel.session_log].reverse().map((entry, i) => (
              <div key={i} style={{ marginBottom: 8, paddingLeft: 10, borderLeft: "2px solid var(--border)" }}>
                <div style={{ fontSize: 11, color: "var(--text-muted)", marginBottom: 2 }}>
                  {fmtFull(entry.date)} · {entry.logged_by}
                </div>
                <div style={{ fontSize: 13 }}>{entry.notes}</div>
              </div>
            ))
          }
        </div>
      )}
    </div>
  );
}
