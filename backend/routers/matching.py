import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from models.actor import ActorType
from models.relationship import Relationship, RelationshipState, RelationshipType
from services import firebase_client, gemini_matcher
from services.workflow_engine import WorkflowTrigger, execute_workflow

router = APIRouter()


class MatchRequest(BaseModel):
    query: str
    target_type: str
    programme_id: str


class ApproveRequest(BaseModel):
    actor_a_id: str
    actor_b_id: str
    match_score: float
    match_reasoning: str
    programme_id: str


@router.post("/match", response_model=list[gemini_matcher.MatchResult])
async def match(body: MatchRequest):
    try:
        actor_type = ActorType(body.target_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid target_type: {body.target_type}")

    candidates = firebase_client.get_actors_by_type(actor_type)
    results = gemini_matcher.match_actors(body.query, candidates)
    return results


@router.post("/match/approve", response_model=Relationship)
async def approve_match(body: ApproveRequest):
    now = datetime.now(timezone.utc)
    rel = Relationship(
        id=str(uuid.uuid4()),
        relationship_type=RelationshipType.mentor_company,
        actor_a_id=body.actor_a_id,
        actor_b_id=body.actor_b_id,
        state=RelationshipState.pending,
        match_score=body.match_score,
        match_reasoning=body.match_reasoning,
        session_log=[],
        created_at=now,
        last_updated=now,
        programme_id=body.programme_id,
    )
    firebase_client.save_relationship(rel)
    execute_workflow(WorkflowTrigger.match_approved, {
        "relationship_id": rel.id,
        "actor_a_id": body.actor_a_id,
        "actor_b_id": body.actor_b_id,
    })
    return rel
