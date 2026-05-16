const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, options);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Request failed: ${res.status}`);
  }
  return res.json();
}

export async function uploadPDF(file) {
  const form = new FormData();
  form.append("file", file);
  return request("/api/onboarding/upload", { method: "POST", body: form });
}

export async function getActors(type) {
  const qs = type ? `?type=${encodeURIComponent(type)}` : "";
  return request(`/api/actors${qs}`);
}

export async function getActor(id) {
  return request(`/api/actors/${id}`);
}

export async function matchActors(query, programmeId = "default") {
  return request("/api/match", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, programme_id: programmeId }),
  });
}

export async function generateIntro(actorAId, actorBId) {
  return request("/api/match/generate-intro", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ actor_a_id: actorAId, actor_b_id: actorBId }),
  });
}

export async function notifyActors(actorAId, actorBId, messageToA, messageToB) {
  return request("/api/match/notify", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      actor_a_id: actorAId,
      actor_b_id: actorBId,
      message_to_a: messageToA,
      message_to_b: messageToB,
    }),
  });
}

export async function approveMatch(actorAId, actorBId, score, reasoning, programmeId) {
  return request("/api/match/approve", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      actor_a_id: actorAId,
      actor_b_id: actorBId,
      match_score: score,
      match_reasoning: reasoning,
      programme_id: programmeId,
    }),
  });
}

export async function getRelationships(filters = {}) {
  const qs = new URLSearchParams(
    Object.fromEntries(Object.entries(filters).filter(([, v]) => v != null))
  ).toString();
  return request(`/api/relationships${qs ? `?${qs}` : ""}`);
}

export async function logSession(relId, notes, loggedBy) {
  return request(`/api/relationships/${relId}/session`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ notes, logged_by: loggedBy }),
  });
}

export async function updateRelationshipState(relId, state) {
  return request(`/api/relationships/${relId}/state`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ state }),
  });
}

export async function getStaleRelationships() {
  return request("/api/workflows/stale");
}
