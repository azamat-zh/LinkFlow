function scoreClass(score) {
  if (score >= 80) return "score-high";
  if (score >= 60) return "score-mid";
  return "score-low";
}

export default function MatchCard({ match, onApprove, approved }) {
  return (
    <div className="card" style={{ marginBottom: 12 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 8 }}>
        <span className={`match-score ${scoreClass(match.score)}`}>{match.score}</span>
        <span style={{ fontWeight: 600, fontSize: 16 }}>{match.actor_name}</span>
        {approved && <span className="badge badge--active">Matched</span>}
      </div>

      <p style={{ margin: "0 0 8px", fontSize: 14 }}>{match.reasoning}</p>

      <div style={{
        background: "var(--bg-surface)",
        borderRadius: "var(--radius)",
        padding: "10px 12px",
        fontSize: 13,
        marginBottom: 12,
        color: "var(--text-muted)",
      }}>
        <strong style={{ display: "block", marginBottom: 4, fontSize: 11 }}>SUGGESTED INTRO</strong>
        {match.suggested_intro}
      </div>

      <button
        className="btn btn-primary"
        onClick={() => onApprove(match)}
        disabled={approved}
      >
        {approved ? "Approved" : "Approve Match"}
      </button>
    </div>
  );
}
