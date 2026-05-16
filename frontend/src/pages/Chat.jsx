import { useEffect, useState } from "react";
import { approveMatch, generateIntro, getActors, matchActors, notifyActors } from "../api/client";

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

function scoreColor(score) {
  if (score >= 80) return "var(--teal)";
  if (score >= 60) return "var(--amber)";
  return "var(--danger)";
}

function AiResultCard({ result, actionLabel, onAction }) {
  return (
    <div style={{
      padding: "12px 14px",
      border: "1px solid var(--border)",
      borderRadius: "var(--radius)",
      marginBottom: 8,
      background: "var(--bg)",
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 4 }}>
        <span style={{ fontSize: 22, fontWeight: 700, color: scoreColor(result.score), minWidth: 36 }}>
          {result.score}
        </span>
        <div style={{ flex: 1 }}>
          <span style={{ fontWeight: 600, fontSize: 14 }}>{result.actor_name}</span>
        </div>
        <button className="btn btn-primary" style={{ fontSize: 13, padding: "6px 14px" }} onClick={() => onAction(result)}>
          {actionLabel}
        </button>
      </div>
      <p style={{ margin: 0, fontSize: 13, color: "var(--text-muted)", paddingLeft: 46 }}>
        {result.reasoning}
      </p>
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
      {onClear && (
        <button onClick={onClear} style={{ background: "none", border: "none", cursor: "pointer", color: "var(--text-muted)", fontSize: 20, lineHeight: 1 }}>
          ×
        </button>
      )}
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
      <button className="btn" style={{ marginTop: 6, fontSize: 13 }} onClick={() => navigator.clipboard.writeText(message)}>
        Copy
      </button>
    </div>
  );
}

function StepIndicator({ phase }) {
  const steps = ["Find Actor A", "Find Actor B", "Confirm & Notify"];
  const idx = { "search": 0, "pick-b": 1, "confirm": 2 }[phase];
  return (
    <div style={{ display: "flex", gap: 8, marginBottom: 24, fontSize: 13, flexWrap: "wrap" }}>
      {steps.map((step, i) => {
        const active = i === idx;
        const done = i < idx;
        return (
          <div key={step} style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span style={{
              padding: "3px 12px", borderRadius: 999, fontSize: 12, fontWeight: 600,
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
  );
}

export default function Chat() {
  const [phase, setPhase] = useState("search");

  // Phase 1
  const [query1, setQuery1] = useState("");
  const [results1, setResults1] = useState([]);
  const [loading1, setLoading1] = useState(false);
  const [searched1, setSearched1] = useState(false);
  const [actorA, setActorA] = useState(null);

  // Phase 2
  const [query2, setQuery2] = useState("");
  const [results2, setResults2] = useState([]);
  const [loading2, setLoading2] = useState(false);
  const [actorB, setActorB] = useState(null);

  // Phase 3
  const [loadingIntro, setLoadingIntro] = useState(false);
  const [msgToA, setMsgToA] = useState("");
  const [msgToB, setMsgToB] = useState("");
  const [sending, setSending] = useState(false);
  const [sendResults, setSendResults] = useState(null);
  const [approved, setApproved] = useState(false);

  // When Actor A is selected: check if original query mentions any actor by name.
  // If yes → pre-select that actor as B. If no → AI search based on Actor A's profile.
  useEffect(() => {
    if (!actorA) return;

    async function resolveActorB() {
      const allActors = await getActors().catch(() => []);
      const q = query1.toLowerCase();

      // Split query into whole words for exact matching (avoids "tech" matching "fintech")
      const qWords = new Set(q.split(/\W+/).filter((w) => w.length > 2));

      const mentioned = allActors
        .filter((a) => a.id !== actorA.id)
        .map((a) => {
          const nameWords = a.name.toLowerCase().split(/\W+/).filter((w) => w.length > 2);
          const matchCount = nameWords.filter((w) => qWords.has(w)).length;
          return { actor: a, matchCount };
        })
        .filter((x) => x.matchCount > 0)
        .sort((a, b) => b.matchCount - a.matchCount)[0]?.actor;

      if (mentioned) {
        // A specific actor was named in the query — pre-select them as Actor B
        setActorB({ id: mentioned.id, name: mentioned.name, actor_type: mentioned.actor_type, sector: mentioned.sector });
        setQuery2(`Matched from query: "${query1}"`);
        setResults2([]);
      } else {
        // No name found — AI suggests best matches using Actor A's profile AND original query context
        const autoQuery = `The coordinator's request: "${query1}". Now find the best match for ${actorA.name}, a ${actorA.actor_type.replace("_", " ")} in ${actorA.sector}. Their expertise: ${actorA.expertise?.join(", ")}. Prioritise actors that fit both the coordinator's request and ${actorA.name}'s profile.`;
        setQuery2(autoQuery);
        runSearch2(autoQuery);
      }
    }

    resolveActorB();
  }, [actorA]);

  async function runSearch1() {
    if (!query1.trim()) return;
    setLoading1(true);
    setResults1([]);
    setSearched1(true);
    try {
      const res = await matchActors(query1);
      setResults1(res.filter((r) => r.score > 0));
    } catch {
      setResults1([]);
    } finally {
      setLoading1(false);
    }
  }

  async function runSearch2(q) {
    const searchQuery = q || query2;
    if (!searchQuery.trim()) return;
    setLoading2(true);
    setResults2([]);
    try {
      const res = await matchActors(searchQuery);
      setResults2(res.filter((r) => r.score > 0 && r.actor_id !== actorA?.id));
    } catch {
      setResults2([]);
    } finally {
      setLoading2(false);
    }
  }

  function selectActorA(result) {
    setActorA({ id: result.actor_id, name: result.actor_name, actor_type: "mentor", sector: "", needs: [], expertise: [], ...result._profile });
    // fetch full profile from results for display — store what we have
    setActorA({ id: result.actor_id, name: result.actor_name, actor_type: result.actor_type || "mentor", sector: result.sector || "", needs: result.needs || [], expertise: result.expertise || [] });
    setPhase("pick-b");
  }

  function selectActorB(result) {
    setActorB({ id: result.actor_id, name: result.actor_name, actor_type: result.actor_type || "company", sector: result.sector || "" });
  }

  async function handleConfirm() {
    setPhase("confirm");
    setLoadingIntro(true);
    try {
      const intro = await generateIntro(actorA.id, actorB.id);
      setMsgToA(intro.message_to_a);
      setMsgToB(intro.message_to_b);
    } catch {
      setMsgToA(`Hi ${actorA.name},\n\nWe'd like to connect you with ${actorB.name}.\n\nBest,\nThe LinkFlow Team`);
      setMsgToB(`Hi ${actorB.name},\n\nWe'd like to connect you with ${actorA.name}.\n\nBest,\nThe LinkFlow Team`);
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
    setPhase("search");
    setActorA(null); setActorB(null);
    setQuery1(""); setResults1([]); setSearched1(false);
    setQuery2(""); setResults2([]);
    setMsgToA(""); setMsgToB("");
    setSendResults(null); setApproved(false);
  }

  return (
    <div className="page-container" style={{ maxWidth: 760, margin: "0 auto" }}>
      <h2 className="page-title">AI Matchmaker</h2>
      <StepIndicator phase={phase} />

      {/* ── Phase 1: Find Actor A ─────────────────────────────── */}
      {phase === "search" && (
        <div className="card" style={{ marginBottom: 16 }}>
          <p style={{ margin: "0 0 10px", fontSize: 13, fontWeight: 600, color: "var(--text-muted)" }}>
            STEP 1 — Describe who or what you're looking for
          </p>
          <div style={{ display: "flex", gap: 10 }}>
            <input
              value={query1}
              onChange={(e) => setQuery1(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && runSearch1()}
              placeholder='e.g. "SaaS mentor with EU expansion experience"'
              style={{ flex: 1 }}
              autoFocus
            />
            <button className="btn btn-primary" onClick={runSearch1} disabled={loading1 || !query1.trim()}>
              {loading1 ? "Searching…" : "Search"}
            </button>
          </div>

          {loading1 && <p style={{ color: "var(--text-muted)", fontSize: 14, marginTop: 12 }}>Analysing profiles…</p>}

          {!loading1 && searched1 && results1.length === 0 && (
            <p style={{ color: "var(--text-muted)", fontSize: 14, marginTop: 12 }}>No matches found. Try rephrasing.</p>
          )}

          {results1.length > 0 && (
            <div style={{ marginTop: 16 }}>
              <p style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 8 }}>
                {results1.length} results — click to select as Actor A
              </p>
              {results1.map((r) => (
                <AiResultCard key={r.actor_id} result={r} actionLabel="Select" onAction={selectActorA} />
              ))}
            </div>
          )}
        </div>
      )}

      {/* ── Phase 2: Find Actor B ─────────────────────────────── */}
      {(phase === "pick-b" || phase === "confirm") && actorA && (
        <SelectedBadge actor={actorA} onClear={phase === "pick-b" ? reset : null} />
      )}

      {phase === "pick-b" && (
        <div className="card" style={{ marginBottom: 16 }}>
          <p style={{ margin: "0 0 10px", fontSize: 13, fontWeight: 600, color: "var(--text-muted)" }}>
            STEP 2 — Who to match {actorA?.name} with?
          </p>

          {/* Name detected from original query */}
          {actorB && results2.length === 0 && (
            <div style={{ padding: "10px 12px", background: "var(--teal-light)", borderRadius: "var(--radius)", marginBottom: 12, fontSize: 13 }}>
              <strong style={{ color: "var(--teal)" }}>Detected from your query:</strong> {actorB.name} was mentioned — pre-selected below. You can change this.
            </div>
          )}

          <div style={{ display: "flex", gap: 10, marginBottom: 12 }}>
            <input
              value={query2}
              onChange={(e) => setQuery2(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && runSearch2()}
              placeholder="Refine the search…"
              style={{ flex: 1 }}
            />
            <button className="btn" onClick={() => runSearch2()} disabled={loading2}>
              {loading2 ? "…" : "Refine"}
            </button>
          </div>

          {loading2 && <p style={{ color: "var(--text-muted)", fontSize: 14 }}>Finding best matches for {actorA?.name}…</p>}

          {!loading2 && results2.length === 0 && !actorB && (
            <p style={{ color: "var(--text-muted)", fontSize: 14 }}>No suggestions yet.</p>
          )}

          {results2.map((r) => (
            <AiResultCard key={r.actor_id} result={r} actionLabel="Select" onAction={selectActorB} />
          ))}
        </div>
      )}

      {phase === "pick-b" && actorB && (
        <>
          <SelectedBadge actor={actorB} onClear={() => setActorB(null)} />
          <button className="btn btn-primary" style={{ width: "100%", padding: 12, fontSize: 15 }} onClick={handleConfirm}>
            Continue to Confirmation →
          </button>
        </>
      )}

      {/* ── Phase 3: Confirm & Notify ─────────────────────────── */}
      {phase === "confirm" && actorB && (
        <>
          <SelectedBadge actor={actorB} onClear={() => { setActorB(null); setPhase("pick-b"); }} />

          <div className="card" style={{ marginBottom: 16 }}>
            <p style={{ margin: "0 0 16px", fontSize: 14, fontWeight: 600 }}>
              Review and edit the intro messages before sending
            </p>

            {loadingIntro
              ? <p style={{ color: "var(--text-muted)", fontSize: 14 }}>Generating personalised messages…</p>
              : (
                <>
                  <MessageBox label="To" actorName={actorA.name} message={msgToA} onEdit={setMsgToA} sent={sendResults?.actor_a?.sent} />
                  <MessageBox label="To" actorName={actorB.name} message={msgToB} onEdit={setMsgToB} sent={sendResults?.actor_b?.sent} />
                </>
              )
            }

            {sendResults && (
              <div style={{ marginBottom: 12, fontSize: 13 }}>
                {sendResults.actor_a?.sent
                  ? <p style={{ color: "var(--teal)", margin: "0 0 4px" }}>✓ Email sent to {actorA.name}</p>
                  : <p style={{ color: "var(--text-muted)", margin: "0 0 4px" }}>⚠ {actorA.name}: {sendResults.actor_a?.reason}</p>}
                {sendResults.actor_b?.sent
                  ? <p style={{ color: "var(--teal)", margin: 0 }}>✓ Email sent to {actorB.name}</p>
                  : <p style={{ color: "var(--text-muted)", margin: 0 }}>⚠ {actorB.name}: {sendResults.actor_b?.reason}</p>}
              </div>
            )}

            <div style={{ display: "flex", gap: 10 }}>
              <button className="btn btn-primary" onClick={handleSendEmails} disabled={sending || loadingIntro} style={{ flex: 1, padding: 12 }}>
                {sending ? "Sending…" : "Send Emails"}
              </button>
              <button className="btn" onClick={handleApprove} disabled={approved} style={{ flex: 1, padding: 12 }}>
                {approved ? "✓ Relationship Created" : "Approve & Create Relationship"}
              </button>
            </div>
          </div>

          <button className="btn" onClick={reset} style={{ fontSize: 13 }}>← Start over</button>
        </>
      )}
    </div>
  );
}
