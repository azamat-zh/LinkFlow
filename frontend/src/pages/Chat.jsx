import { useEffect, useRef, useState } from "react";
import { approveMatch, generateIntro, getActors, notifyActors } from "../api/client";

const TYPE_LABEL = {
  mentor: "Mentor",
  company: "Company",
  partner: "Partner",
  service_provider: "Service Provider",
};

const TYPE_BADGE = {
  company: "badge--company",
  mentor: "badge--mentor",
  partner: "badge--partner",
  service_provider: "badge--service-provider",
};

function ActorSearch({ label, exclude, onSelect }) {
  const [query, setQuery] = useState("");
  const [all, setAll] = useState([]);
  const inputRef = useRef(null);

  useEffect(() => {
    getActors().then(setAll).catch(() => {});
    inputRef.current?.focus();
  }, []);

  const filtered = all
    .filter((a) => a.id !== exclude?.id)
    .filter((a) => {
      const q = query.toLowerCase();
      return (
        !q ||
        a.name.toLowerCase().includes(q) ||
        a.sector.toLowerCase().includes(q) ||
        a.actor_type.toLowerCase().includes(q) ||
        a.tags.some((t) => t.toLowerCase().includes(q))
      );
    });

  return (
    <div className="card" style={{ marginBottom: 16 }}>
      <p style={{ margin: "0 0 10px", fontSize: 13, fontWeight: 600, color: "var(--text-muted)" }}>
        {label}
      </p>
      <input
        ref={inputRef}
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search by name, sector, or type…"
        style={{ width: "100%", marginBottom: 12, boxSizing: "border-box" }}
      />
      <div style={{ maxHeight: 320, overflowY: "auto", display: "flex", flexDirection: "column", gap: 8 }}>
        {filtered.length === 0 && (
          <p style={{ color: "var(--text-muted)", fontSize: 14, margin: 0 }}>No actors found.</p>
        )}
        {filtered.map((actor) => (
          <div
            key={actor.id}
            onClick={() => onSelect(actor)}
            style={{
              padding: "10px 14px",
              border: "1px solid var(--border)",
              borderRadius: "var(--radius)",
              cursor: "pointer",
              transition: "border-color 0.15s, background 0.15s",
            }}
            onMouseEnter={(e) => e.currentTarget.style.borderColor = "var(--primary)"}
            onMouseLeave={(e) => e.currentTarget.style.borderColor = "var(--border)"}
          >
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 2 }}>
              <span style={{ fontWeight: 600, fontSize: 14 }}>{actor.name}</span>
              <span className={`badge ${TYPE_BADGE[actor.actor_type]}`}>
                {TYPE_LABEL[actor.actor_type]}
              </span>
            </div>
            <p style={{ margin: 0, fontSize: 12, color: "var(--text-muted)" }}>
              {actor.sector} · {actor.location}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

function SelectedBadge({ actor, onClear }) {
  return (
    <div style={{
      display: "flex", alignItems: "center", gap: 10,
      padding: "10px 14px", background: "var(--primary-light)",
      borderRadius: "var(--radius)", marginBottom: 16,
      border: "1px solid var(--primary)",
    }}>
      <span className={`badge ${TYPE_BADGE[actor.actor_type]}`}>{TYPE_LABEL[actor.actor_type]}</span>
      <span style={{ fontWeight: 600, flex: 1 }}>{actor.name}</span>
      <span style={{ fontSize: 12, color: "var(--text-muted)" }}>{actor.sector}</span>
      <button
        onClick={onClear}
        style={{ background: "none", border: "none", cursor: "pointer", color: "var(--text-muted)", fontSize: 18, lineHeight: 1 }}
      >×</button>
    </div>
  );
}

function MessageBox({ label, actorName, message, onEdit, sent }) {
  return (
    <div style={{ marginBottom: 20 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
        <p style={{ margin: 0, fontSize: 13, fontWeight: 600, color: "var(--text-muted)" }}>
          📧 {label}: <strong>{actorName}</strong>
        </p>
        {sent && <span className="badge badge--active">Sent</span>}
      </div>
      <textarea
        value={message}
        onChange={(e) => onEdit(e.target.value)}
        rows={5}
        style={{ width: "100%", boxSizing: "border-box", fontSize: 14, resize: "vertical" }}
      />
      <button
        className="btn"
        style={{ marginTop: 6, fontSize: 13 }}
        onClick={() => navigator.clipboard.writeText(message)}
      >
        Copy
      </button>
    </div>
  );
}

export default function Chat() {
  const [phase, setPhase] = useState("pick-a"); // pick-a | pick-b | confirm
  const [actorA, setActorA] = useState(null);
  const [actorB, setActorB] = useState(null);

  const [loadingIntro, setLoadingIntro] = useState(false);
  const [msgToA, setMsgToA] = useState("");
  const [msgToB, setMsgToB] = useState("");

  const [sending, setSending] = useState(false);
  const [sendResults, setSendResults] = useState(null);
  const [approved, setApproved] = useState(false);

  async function handleConfirm() {
    setPhase("confirm");
    setLoadingIntro(true);
    try {
      const intro = await generateIntro(actorA.id, actorB.id);
      setMsgToA(intro.message_to_a);
      setMsgToB(intro.message_to_b);
    } catch {
      setMsgToA(`Hi ${actorA.name},\n\nWe'd like to connect you with ${actorB.name}. We think you'd be a great match.\n\nBest,\nThe LinkFlow Team`);
      setMsgToB(`Hi ${actorB.name},\n\nWe'd like to connect you with ${actorA.name}. We think you'd be a great match.\n\nBest,\nThe LinkFlow Team`);
    } finally {
      setLoadingIntro(false);
    }
  }

  async function handleSendEmails() {
    setSending(true);
    try {
      const results = await notifyActors(actorA.id, actorB.id, msgToA, msgToB);
      setSendResults(results);
    } finally {
      setSending(false);
    }
  }

  async function handleApprove() {
    await approveMatch(actorA.id, actorB.id, 0, "Manually matched by coordinator", "default");
    setApproved(true);
  }

  function reset() {
    setPhase("pick-a");
    setActorA(null);
    setActorB(null);
    setMsgToA("");
    setMsgToB("");
    setSendResults(null);
    setApproved(false);
  }

  return (
    <div className="page-container" style={{ maxWidth: 760, margin: "0 auto" }}>
      <h2 className="page-title">AI Matchmaker</h2>

      {/* Progress indicator */}
      <div style={{ display: "flex", gap: 8, marginBottom: 24, fontSize: 13 }}>
        {["Select Actor A", "Select Actor B", "Confirm & Notify"].map((step, i) => {
          const active = (phase === "pick-a" && i === 0) || (phase === "pick-b" && i === 1) || (phase === "confirm" && i === 2);
          const done = (i === 0 && (phase === "pick-b" || phase === "confirm")) || (i === 1 && phase === "confirm");
          return (
            <div key={step} style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <span style={{
                padding: "3px 10px", borderRadius: 999, fontSize: 12, fontWeight: 600,
                background: done ? "var(--teal-light)" : active ? "var(--primary)" : "var(--bg-surface)",
                color: done ? "var(--teal)" : active ? "#fff" : "var(--text-muted)",
                border: `1px solid ${done ? "var(--teal)" : active ? "var(--primary)" : "var(--border)"}`,
              }}>
                {done ? "✓ " : ""}{step}
              </span>
              {i < 2 && <span style={{ color: "var(--border)" }}>→</span>}
            </div>
          );
        })}
      </div>

      {/* Phase 1 — pick actor A */}
      {phase === "pick-a" && (
        <ActorSearch
          label="STEP 1 — Who are you finding a match for?"
          exclude={null}
          onSelect={(a) => { setActorA(a); setPhase("pick-b"); }}
        />
      )}

      {/* Phase 2 — pick actor B */}
      {(phase === "pick-b" || phase === "confirm") && actorA && (
        <SelectedBadge actor={actorA} onClear={reset} />
      )}

      {phase === "pick-b" && (
        <ActorSearch
          label="STEP 2 — Who do you want to match them with?"
          exclude={actorA}
          onSelect={(b) => { setActorB(b); }}
        />
      )}

      {phase === "pick-b" && actorB && (
        <>
          <SelectedBadge actor={actorB} onClear={() => setActorB(null)} />
          <button className="btn btn-primary" style={{ width: "100%", padding: 12, fontSize: 15 }} onClick={handleConfirm}>
            Continue to Confirmation →
          </button>
        </>
      )}

      {/* Phase 3 — confirm */}
      {phase === "confirm" && (
        <>
          {actorB && <SelectedBadge actor={actorB} onClear={() => { setActorB(null); setPhase("pick-b"); }} />}

          <div className="card" style={{ marginBottom: 16 }}>
            <p style={{ margin: "0 0 16px", fontSize: 14, fontWeight: 600 }}>
              Review and edit the intro messages before sending
            </p>

            {loadingIntro ? (
              <p style={{ color: "var(--text-muted)", fontSize: 14 }}>Generating personalised messages…</p>
            ) : (
              <>
                <MessageBox
                  label="To"
                  actorName={actorA.name}
                  message={msgToA}
                  onEdit={setMsgToA}
                  sent={sendResults?.actor_a?.sent}
                />
                <MessageBox
                  label="To"
                  actorName={actorB.name}
                  message={msgToB}
                  onEdit={setMsgToB}
                  sent={sendResults?.actor_b?.sent}
                />
              </>
            )}

            {sendResults && (
              <div style={{ marginBottom: 12, fontSize: 13 }}>
                {sendResults.actor_a?.sent
                  ? <p style={{ color: "var(--teal)", margin: "0 0 4px" }}>✓ Email sent to {actorA.name}</p>
                  : <p style={{ color: "var(--text-muted)", margin: "0 0 4px" }}>⚠ {actorA.name}: {sendResults.actor_a?.reason}</p>
                }
                {sendResults.actor_b?.sent
                  ? <p style={{ color: "var(--teal)", margin: 0 }}>✓ Email sent to {actorB.name}</p>
                  : <p style={{ color: "var(--text-muted)", margin: 0 }}>⚠ {actorB.name}: {sendResults.actor_b?.reason}</p>
                }
              </div>
            )}

            <div style={{ display: "flex", gap: 10 }}>
              <button
                className="btn btn-primary"
                onClick={handleSendEmails}
                disabled={sending || loadingIntro}
                style={{ flex: 1, padding: 12 }}
              >
                {sending ? "Sending…" : "Send Emails"}
              </button>
              <button
                className="btn"
                onClick={handleApprove}
                disabled={approved}
                style={{ flex: 1, padding: 12 }}
              >
                {approved ? "✓ Relationship Created" : "Approve & Create Relationship"}
              </button>
            </div>
          </div>

          <button className="btn" onClick={reset} style={{ fontSize: 13 }}>
            ← Start over
          </button>
        </>
      )}
    </div>
  );
}
