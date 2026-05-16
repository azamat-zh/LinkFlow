import json
import os
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from models.relationship import Relationship, RelationshipState, SessionLog
from services import firebase_client
from services.workflow_engine import WorkflowTrigger, execute_workflow
from google import genai

router = APIRouter()


class SessionRequest(BaseModel):
    notes: str
    logged_by: str = "coordinator"


class StateRequest(BaseModel):
    state: str


class ConfirmRequest(BaseModel):
    role: str          # "mentor" or "startup"
    confirmed_by: str = "coordinator"


class SeedRelationshipRequest(BaseModel):
    id: str
    relationship_type: str
    actor_a_id: str
    actor_b_id: str
    state: str
    match_score: float
    match_reasoning: str
    session_log: list[dict]
    created_at: str
    last_updated: str
    programme_id: str
    mentor_confirmed: bool = False
    startup_confirmed: bool = False


@router.get("/relationships", response_model=list[Relationship])
async def list_relationships(
    actor_id: str = Query(default=None),
    state: str = Query(default=None),
    programme_id: str = Query(default=None),
):
    if actor_id:
        rels = firebase_client.get_relationships_by_actor(actor_id)
    else:
        rels = firebase_client.get_all_relationships()

    if state:
        try:
            state_enum = RelationshipState(state)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid state: {state}")
        rels = [r for r in rels if r.state == state_enum]

    if programme_id:
        rels = [r for r in rels if r.programme_id == programme_id]

    return rels


@router.get("/relationships/{rel_id}", response_model=Relationship)
async def get_relationship(rel_id: str):
    rel = firebase_client.get_relationship(rel_id)
    if rel is None:
        raise HTTPException(status_code=404, detail="Relationship not found.")
    return rel


@router.post("/relationships/{rel_id}/session", response_model=Relationship)
async def log_session(rel_id: str, body: SessionRequest):
    rel = firebase_client.get_relationship(rel_id)
    if rel is None:
        raise HTTPException(status_code=404, detail="Relationship not found.")

    now = datetime.now(timezone.utc)
    rel.session_log.append(SessionLog(date=now, notes=body.notes, logged_by=body.logged_by))
    rel.last_updated = now
    firebase_client.save_relationship(rel)
    execute_workflow(WorkflowTrigger.session_logged, {"relationship_id": rel_id, "logged_by": body.logged_by})
    return rel


@router.patch("/relationships/{rel_id}/state", response_model=Relationship)
async def update_state(rel_id: str, body: StateRequest):
    try:
        new_state = RelationshipState(body.state)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid state: {body.state}")

    rel = firebase_client.get_relationship(rel_id)
    if rel is None:
        raise HTTPException(status_code=404, detail="Relationship not found.")

    now = datetime.now(timezone.utc)
    rel.state = new_state
    rel.last_updated = now
    rel.session_log.append(SessionLog(
        date=now,
        notes=f"State changed to {new_state.value}.",
        logged_by="coordinator",
    ))
    firebase_client.save_relationship(rel)
    return rel


@router.post("/relationships/{rel_id}/confirm", response_model=Relationship)
async def confirm_actor(rel_id: str, body: ConfirmRequest):
    rel = firebase_client.get_relationship(rel_id)
    if rel is None:
        raise HTTPException(status_code=404, detail="Relationship not found.")

    role = body.role.lower()
    if role not in ("mentor", "startup"):
        raise HTTPException(status_code=400, detail="role must be 'mentor' or 'startup'")

    now = datetime.now(timezone.utc)

    if role == "mentor":
        rel.mentor_confirmed = True
        rel.session_log.append(SessionLog(date=now, notes="Mentor confirmed participation.", logged_by=body.confirmed_by))
    else:
        rel.startup_confirmed = True
        rel.session_log.append(SessionLog(date=now, notes="Startup confirmed participation.", logged_by=body.confirmed_by))

    # Auto-activate when both sides confirmed
    if rel.mentor_confirmed and rel.startup_confirmed and rel.state == RelationshipState.pending:
        rel.state = RelationshipState.active
        rel.session_log.append(SessionLog(
            date=now,
            notes="Both parties confirmed — relationship marked active.",
            logged_by="system",
        ))

    rel.last_updated = now
    firebase_client.save_relationship(rel)
    return rel


@router.post("/relationships/{rel_id}/nudge")
async def generate_nudge(rel_id: str):
    rel = firebase_client.get_relationship(rel_id)
    if rel is None:
        raise HTTPException(status_code=404, detail="Relationship not found.")

    actor_a = firebase_client.get_actor(rel.actor_a_id)
    actor_b = firebase_client.get_actor(rel.actor_b_id)
    name_a = actor_a.name if actor_a else "the mentor"
    name_b = actor_b.name if actor_b else "the startup"

    fallback = (
        f"Hi {name_a}, just checking in — it's been a while since your last session with {name_b}. "
        f"Hope things are going well! Let us know if you need anything."
    )

    try:
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", ""))
        from google.genai import types
        prompt = (
            f"Write a friendly 2-sentence check-in message from a programme coordinator to {name_a} "
            f"who has not logged a session with {name_b} in the past 14 days. "
            f"Be warm and non-accusatory. Return only the message text."
        )
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        nudge = response.text.strip()
    except Exception:
        nudge = fallback

    now = datetime.now(timezone.utc)
    rel.session_log.append(SessionLog(date=now, notes=f"Nudge generated: {nudge}", logged_by="system"))
    rel.last_updated = now
    firebase_client.save_relationship(rel)

    return {"nudge_message": nudge, "relationship_id": rel_id}


@router.post("/relationships/seed-demo", response_model=Relationship)
async def seed_demo_relationship(body: SeedRelationshipRequest):
    """Dev-only endpoint for seeding relationships with custom dates."""
    from models.relationship import RelationshipType
    from datetime import datetime

    session_logs = [
        SessionLog(
            date=datetime.fromisoformat(e["date"]),
            notes=e["notes"],
            logged_by=e["logged_by"],
        )
        for e in body.session_log
    ]

    rel = Relationship(
        id=body.id,
        relationship_type=RelationshipType(body.relationship_type),
        actor_a_id=body.actor_a_id,
        actor_b_id=body.actor_b_id,
        state=RelationshipState(body.state),
        match_score=body.match_score,
        match_reasoning=body.match_reasoning,
        session_log=session_logs,
        created_at=datetime.fromisoformat(body.created_at),
        last_updated=datetime.fromisoformat(body.last_updated),
        programme_id=body.programme_id,
        mentor_confirmed=body.mentor_confirmed,
        startup_confirmed=body.startup_confirmed,
    )
    firebase_client.save_relationship(rel)
    return rel
