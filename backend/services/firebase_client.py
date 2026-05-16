import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from models.actor import ActorProfile, ActorType
from models.relationship import Relationship, RelationshipState

# ── In-memory mock store (used when USE_MOCK_DB=true) ──────────────────────────
_mock_actors: dict[str, dict] = {}
_mock_relationships: dict[str, dict] = {}
_mock_events: list[dict] = []

_USE_MOCK = os.environ.get("USE_MOCK_DB", "false").lower() == "true"

# ── Real Firestore client ───────────────────────────────────────────────────────
_db = None

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
DEFAULT_CREDENTIALS_PATH = os.path.join(BACKEND_DIR, "firebase-credentials.json")

def get_db():
    global _db
    if _db is None:
            import firebase_admin
            from firebase_admin import credentials, firestore

            cred_path = os.environ.get("FIREBASE_CREDENTIALS_PATH", DEFAULT_CREDENTIALS_PATH)

            if not os.path.exists(cred_path):
                raise FileNotFoundError(
                    f"Firebase credentials file not found at {cred_path}. "
                    "Place firebase-credentials.json in the backend/ folder or set FIREBASE_CREDENTIALS_PATH."
                )
        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        _db = firestore.client()
    return _db


# ── Firestore doc converters ────────────────────────────────────────────────────

def _doc_to_actor(doc) -> ActorProfile:
    data = doc.to_dict()
    data["id"] = doc.id
    if hasattr(data.get("created_at"), "timestamp"):
        val = data["created_at"]
        data["created_at"] = val.replace(tzinfo=timezone.utc) if val.tzinfo is None else val
    return ActorProfile(**data)


def _doc_to_relationship(doc) -> Relationship:
    data = doc.to_dict()
    data["id"] = doc.id
    for ts_field in ("created_at", "last_updated"):
        if hasattr(data.get(ts_field), "timestamp"):
            val = data[ts_field]
            data[ts_field] = val.replace(tzinfo=timezone.utc) if val.tzinfo is None else val
    session_log = data.get("session_log", [])
    for entry in session_log:
        if hasattr(entry.get("date"), "timestamp"):
            val = entry["date"]
            entry["date"] = val.replace(tzinfo=timezone.utc) if val.tzinfo is None else val
    data["session_log"] = session_log
    return Relationship(**data)


# ── Actor functions ─────────────────────────────────────────────────────────────

def get_actor(id: str) -> Optional[ActorProfile]:
    if _USE_MOCK:
        data = _mock_actors.get(id)
        return ActorProfile(**data) if data else None
    doc = get_db().collection("actors").document(id).get()
    return _doc_to_actor(doc) if doc.exists else None


def save_actor(actor: ActorProfile) -> str:
    if _USE_MOCK:
        _mock_actors[actor.id] = actor.model_dump(mode="json")
        return actor.id
    data = actor.model_dump()
    data.pop("id", None)
    get_db().collection("actors").document(actor.id).set(data)
    return actor.id


def get_all_actors() -> list[ActorProfile]:
    if _USE_MOCK:
        return [ActorProfile(**d) for d in _mock_actors.values()]
    docs = get_db().collection("actors").stream()
    return [_doc_to_actor(doc) for doc in docs]


def get_actors_by_type(actor_type: ActorType) -> list[ActorProfile]:
    if _USE_MOCK:
        return [
            ActorProfile(**d) for d in _mock_actors.values()
            if d.get("actor_type") == actor_type.value
        ]
    docs = get_db().collection("actors").where("actor_type", "==", actor_type.value).stream()
    return [_doc_to_actor(doc) for doc in docs]


# ── Relationship functions ──────────────────────────────────────────────────────

def get_all_relationships() -> list[Relationship]:
    if _USE_MOCK:
        return [Relationship(**d) for d in _mock_relationships.values()]
    docs = get_db().collection("relationships").stream()
    return [_doc_to_relationship(doc) for doc in docs]


def get_relationship(id: str) -> Optional[Relationship]:
    if _USE_MOCK:
        data = _mock_relationships.get(id)
        return Relationship(**data) if data else None
    doc = get_db().collection("relationships").document(id).get()
    return _doc_to_relationship(doc) if doc.exists else None


def save_relationship(rel: Relationship) -> str:
    if _USE_MOCK:
        _mock_relationships[rel.id] = rel.model_dump(mode="json")
        return rel.id
    data = rel.model_dump()
    data.pop("id", None)
    get_db().collection("relationships").document(rel.id).set(data)
    return rel.id


def update_relationship_state(id: str, state: RelationshipState) -> None:
    if _USE_MOCK:
        if id in _mock_relationships:
            _mock_relationships[id]["state"] = state.value
        return
    get_db().collection("relationships").document(id).update({"state": state.value})


def get_relationships_by_actor(actor_id: str) -> list[Relationship]:
    if _USE_MOCK:
        return [
            Relationship(**d) for d in _mock_relationships.values()
            if d.get("actor_a_id") == actor_id or d.get("actor_b_id") == actor_id
        ]
    db = get_db()
    docs_a = db.collection("relationships").where("actor_a_id", "==", actor_id).stream()
    docs_b = db.collection("relationships").where("actor_b_id", "==", actor_id).stream()
    seen = set()
    results = []
    for doc in list(docs_a) + list(docs_b):
        if doc.id not in seen:
            seen.add(doc.id)
            results.append(_doc_to_relationship(doc))
    return results


def get_stale_relationships(days: int = 14) -> list[Relationship]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    if _USE_MOCK:
        return [
            Relationship(**d) for d in _mock_relationships.values()
            if d.get("state") == "active"
            and datetime.fromisoformat(str(d.get("last_updated"))) < cutoff
        ]
    docs = get_db().collection("relationships").where("state", "==", "active").stream()
    stale = []
    for doc in docs:
        rel = _doc_to_relationship(doc)
        last = rel.last_updated
        if last.tzinfo is None:
            last = last.replace(tzinfo=timezone.utc)
        if last < cutoff:
            stale.append(rel)
    return stale


# ── Workflow events ─────────────────────────────────────────────────────────────

def log_workflow_event(trigger: str, context: dict) -> None:
    if _USE_MOCK:
        _mock_events.append({
            "trigger": trigger,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "context": context,
        })
        return
    get_db().collection("workflow_events").add({
        "trigger": trigger,
        "timestamp": datetime.now(timezone.utc),
        "context": context,
    })


def get_mock_events() -> list[dict]:
    return list(reversed(_mock_events[-50:]))
