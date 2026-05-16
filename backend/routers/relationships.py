from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from models.relationship import Relationship, RelationshipState, SessionLog
from services import firebase_client
from services.workflow_engine import WorkflowTrigger, execute_workflow

router = APIRouter()


class SessionRequest(BaseModel):
    notes: str
    logged_by: str


class StateRequest(BaseModel):
    state: str


@router.get("/relationships", response_model=list[Relationship])
async def list_relationships(
    actor_id: str = Query(default=None),
    state: str = Query(default=None),
    programme_id: str = Query(default=None),
):
    if actor_id:
        rels = firebase_client.get_relationships_by_actor(actor_id)
    else:
        db = firebase_client.get_db()
        docs = db.collection("relationships").stream()
        rels = [firebase_client._doc_to_relationship(doc) for doc in docs]

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
    entry = SessionLog(date=now, notes=body.notes, logged_by=body.logged_by)
    rel.session_log.append(entry)
    rel.last_updated = now

    firebase_client.save_relationship(rel)
    execute_workflow(WorkflowTrigger.session_logged, {
        "relationship_id": rel_id,
        "logged_by": body.logged_by,
    })
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

    firebase_client.update_relationship_state(rel_id, new_state)
    rel.state = new_state
    return rel
