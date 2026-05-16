import json
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from models.relationship import Relationship, RelationshipState, RelationshipType
from services import firebase_client, gemini_matcher, email_service
from services.workflow_engine import WorkflowTrigger, execute_workflow
from google import genai
import os

router = APIRouter()


class MatchRequest(BaseModel):
    query: str
    programme_id: str = "default"


class ApproveRequest(BaseModel):
    actor_a_id: str
    actor_b_id: str
    match_score: float = 0
    match_reasoning: str = ""
    programme_id: str = "default"
    relationship_type: RelationshipType = RelationshipType.mentor_company


class IntroRequest(BaseModel):
    actor_a_id: str
    actor_b_id: str


class IntroMessages(BaseModel):
    message_to_a: str
    message_to_b: str


class NotifyRequest(BaseModel):
    actor_a_id: str
    actor_b_id: str
    message_to_a: str
    message_to_b: str


@router.post("/match", response_model=list[gemini_matcher.MatchResult])
async def match(body: MatchRequest):
    candidates = firebase_client.get_all_actors()
    results = gemini_matcher.match_actors(body.query, candidates)
    return results


@router.post("/match/generate-intro", response_model=IntroMessages)
async def generate_intro(body: IntroRequest):
    actor_a = firebase_client.get_actor(body.actor_a_id)
    actor_b = firebase_client.get_actor(body.actor_b_id)

    if not actor_a or not actor_b:
        raise HTTPException(status_code=404, detail="One or both actors not found.")

    prompt = f"""You are a programme coordinator introducing two ecosystem actors who have been matched.
Write two short, warm, professional intro emails — one to each party.

Actor A: {actor_a.name} ({actor_a.actor_type}) — {actor_a.sector}, {actor_a.location}
Bio: {actor_a.bio}

Actor B: {actor_b.name} ({actor_b.actor_type}) — {actor_b.sector}, {actor_b.location}
Bio: {actor_b.bio}

Return ONLY a JSON object with exactly these two fields:
{{
  "message_to_a": "the email body text to send to {actor_a.name} — mention {actor_b.name} by name and explain why this match was made",
  "message_to_b": "the email body text to send to {actor_b.name} — mention {actor_a.name} by name and explain why this match was made"
}}
Keep each message under 100 words. Warm, human, no corporate jargon."""

    try:
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", ""))
        from google.genai import types
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json"),
        )
        data = json.loads(response.text.strip())
        return IntroMessages(**data)
    except Exception as e:
        return IntroMessages(
            message_to_a=f"Hi {actor_a.name},\n\nWe'd like to introduce you to {actor_b.name} from our ecosystem. We think you'd have a lot to offer each other.\n\nBest,\nThe LinkFlow Team",
            message_to_b=f"Hi {actor_b.name},\n\nWe'd like to introduce you to {actor_a.name} from our ecosystem. We think you'd have a lot to offer each other.\n\nBest,\nThe LinkFlow Team",
        )


@router.post("/match/notify")
async def notify(body: NotifyRequest):
    actor_a = firebase_client.get_actor(body.actor_a_id)
    actor_b = firebase_client.get_actor(body.actor_b_id)

    if not actor_a or not actor_b:
        raise HTTPException(status_code=404, detail="One or both actors not found.")

    results = email_service.send_match_notifications(
        actor_a_email=actor_a.email,
        actor_a_name=actor_a.name,
        message_to_a=body.message_to_a,
        actor_b_email=actor_b.email,
        actor_b_name=actor_b.name,
        message_to_b=body.message_to_b,
    )
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
