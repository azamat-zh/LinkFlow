import uuid
from datetime import datetime, timezone

from fastapi import APIRouter
from pydantic import BaseModel

from models.relationship import Relationship, RelationshipState, RelationshipType
from services import firebase_client, gemini_matcher
from services.workflow_engine import WorkflowTrigger, execute_workflow

router = APIRouter()


class MatchRequest(BaseModel):
    query: str
    programme_id: str = "default"


class ApproveRequest(BaseModel):
    actor_a_id: str
    actor_b_id: str
    match_score: float
    match_reasoning: str
    programme_id: str = "default"
    relationship_type: RelationshipType = RelationshipType.mentor_company


@router.post("/match", response_model=list[gemini_matcher.MatchResult])
async def match(body: MatchRequest):
    candidates = firebase_client.get_all_actors()
    results = gemini_matcher.match_actors(body.query, candidates)
    return results


@router.post("/match/approve", response_model=Relationship)
async def approve_match(body: ApproveRequest):
    now = datetime.now(timezone.utc)
    rel = Relationship(
        id=str(uuid.uuid4()),
        relationship_type=body.relationship_type,
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
