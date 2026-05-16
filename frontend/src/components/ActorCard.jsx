const TYPE_BADGE = {
  company: "badge--company",
  mentor: "badge--mentor",
  partner: "badge--partner",
  service_provider: "badge--service-provider",
};

export default function ActorCard({ actor }) {
  return (
    <div className="card" style={{ marginBottom: 12 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 6 }}>
        <span style={{ fontWeight: 600, fontSize: 16 }}>{actor.name}</span>
        <span className={`badge ${TYPE_BADGE[actor.actor_type] || ""}`}>
          {actor.actor_type.replace("_", " ")}
        </span>
      </div>

      <p style={{ margin: "0 0 4px", fontSize: 13, color: "var(--text-muted)" }}>
        {actor.sector} · {actor.location}
      </p>

      <p style={{ margin: "0 0 10px", fontSize: 14 }}>{actor.bio}</p>

      {actor.tags.length > 0 && (
        <div style={{ display: "flex", flexWrap: "wrap", gap: 4, marginBottom: 8 }}>
          {actor.tags.map((tag) => (
            <span key={tag} className="pill">{tag}</span>
          ))}
        </div>
      )}

      {actor.needs.length > 0 && (
        <div style={{ marginBottom: 6 }}>
          <span style={{ fontSize: 12, fontWeight: 600, color: "var(--text-muted)" }}>NEEDS</span>
          <ul style={{ margin: "4px 0 0 16px", padding: 0, fontSize: 13 }}>
            {actor.needs.map((n) => <li key={n}>{n}</li>)}
          </ul>
        </div>
      )}

      {actor.expertise.length > 0 && (
        <div>
          <span style={{ fontSize: 12, fontWeight: 600, color: "var(--text-muted)" }}>EXPERTISE</span>
          <ul style={{ margin: "4px 0 0 16px", padding: 0, fontSize: 13 }}>
            {actor.expertise.map((e) => <li key={e}>{e}</li>)}
          </ul>
        </div>
      )}
    </div>
  );
}
