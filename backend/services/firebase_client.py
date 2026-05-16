import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import firebase_admin
from firebase_admin import credentials, firestore

from models.actor import ActorProfile, ActorType
from models.relationship import Relationship, RelationshipState

_db = None


def get_db():
    global _db
    if _db is None:
        cred_path = os.environ.get("FIREBASE_CREDENTIALS_PATH", "./firebase-credentials.json")
        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        _db = firestore.client()
    return _db


def _doc_to_actor(doc) -> ActorProfile:
    data = doc.to_dict()
    data["id"] = doc.id
    if hasattr(data.get("created_at"), "timestamp"):
        data["created_at"] = data["created_at"].replace(tzinfo=timezone.utc) if data["created_at"].tzinfo is None else data["created_at"]
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


def get_actor(id: str) -> Optional[ActorProfile]:
    db = get_db()
    doc = db.collection("actors").document(id).get()
    if not doc.exists:
        return None
    return _doc_to_actor(doc)


def save_actor(actor: ActorProfile) -> str:
    db = get_db()
    data = actor.model_dump()
    data.pop("id", None)
    db.collection("actors").document(actor.id).set(data)
    return actor.id


def get_all_actors() -> list[ActorProfile]:
    db = get_db()
    docs = db.collection("actors").stream()
    return [_doc_to_actor(doc) for doc in docs]


def get_actors_by_type(actor_type: ActorType) -> list[ActorProfile]:
    db = get_db()
    docs = db.collection("actors").where("actor_type", "==", actor_type.value).stream()
    return [_doc_to_actor(doc) for doc in docs]


def get_relationship(id: str) -> Optional[Relationship]:
    db = get_db()
    doc = db.collection("relationships").document(id).get()
    if not doc.exists:
        return None
    return _doc_to_relationship(doc)


def save_relationship(rel: Relationship) -> str:
    db = get_db()
    data = rel.model_dump()
    data.pop("id", None)
    db.collection("relationships").document(rel.id).set(data)
    return rel.id


def update_relationship_state(id: str, state: RelationshipState) -> None:
    db = get_db()
    db.collection("relationships").document(id).update({"state": state.value})


def get_relationships_by_actor(actor_id: str) -> list[Relationship]:
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
    db = get_db()
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    docs = db.collection("relationships").where("state", "==", "active").stream()
    stale = []
    for doc in docs:
        rel = _doc_to_relationship(doc)
        last = rel.last_updated
        if last.tzinfo is None:
            last = last.replace(tzinfo=timezone.utc)
        if last < cutoff:
            stale.append(rel)
    return stale


def log_workflow_event(trigger: str, context: dict) -> None:
    db = get_db()
    db.collection("workflow_events").add({
        "trigger": trigger,
        "timestamp": datetime.now(timezone.utc),
        "context": context,
    })
