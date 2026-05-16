import json
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from models.relationship import Relationship, RelationshipState, RelationshipType, SessionLog
from services import firebase_client, gemini_matcher, email_service
from services.workflow_engine import WorkflowTrigger, execute_workflow
from google import genai
from google.genai import types
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
    fallback: bool = False


class NotifyRequest(BaseModel):
    actor_a_id: str
    actor_b_id: str
    message_to_a: str
    message_to_b: str
    relationship_id: str | None = None


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
  "message_to_a": "email body to {actor_a.name} — mention {actor_b.name} by name, explain the match",
  "message_to_b": "email body to {actor_b.name} — mention {actor_a.name} by name, explain the match"
}}
Under 100 words each. Warm, human, no corporate jargon."""

    try:
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", ""))
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json"),
        )
        data = json.loads(response.text.strip())
        return IntroMessages(**data, fallback=False)
    except Exception:
        return IntroMessages(
            message_to_a=(
                f"Hi {actor_a.name},\n\n"
                f"We'd like to introduce you to {actor_b.name} — {actor_b.sector} based in {actor_b.location}. "
                f"We believe their {actor_b.actor_type.replace('_', ' ')} profile is a strong fit for your needs.\n\n"
                f"Best,\nThe LinkFlow Team"
            ),
            message_to_b=(
                f"Hi {actor_b.name},\n\n"
                f"We'd like to introduce you to {actor_a.name} — {actor_a.sector} based in {actor_a.location}. "
                f"We believe their {actor_a.actor_type.replace('_', ' ')} profile is a strong fit for your needs.\n\n"
                f"Best,\nThe LinkFlow Team"
            ),
            fallback=True,
        )


@router.post("/match/notify")
async def notify(body: NotifyRequest):
    actor_a = firebase_client.get_actor(body.actor_a_id)
    actor_b = firebase_client.get_actor(body.actor_b_id)

    if not actor_a or not actor_b:
        raise HTTPException(status_code=404, detail="One or both actors not found.")

    results = email_service.send_match_notifications(
        actor_a_name=actor_a.name,
        message_to_a=body.message_to_a,
        actor_b_name=actor_b.name,
        message_to_b=body.message_to_b,
        actor_a_email=actor_a.email,
        actor_b_email=actor_b.email,
    )

    # Log the notification as a session entry on the relationship
    if body.relationship_id:
        rel = firebase_client.get_relationship(body.relationship_id)
        if rel:
            now = datetime.now(timezone.utc)
            mode = "simulated" if results["actor_a"].get("simulated") else "sent"
            rel.session_log.append(SessionLog(
                date=now,
                notes=f"Intro email {mode} to {actor_a.name} ({actor_a.email or 'no email'}) and {actor_b.name} ({actor_b.email or 'no email'}).",
                logged_by="system",
            ))
            rel.last_updated = now
            firebase_client.save_relationship(rel)

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
        session_log=[SessionLog(
            date=now,
            notes=f"Match approved by coordinator. Score: {body.match_score}. {body.match_reasoning}",
            logged_by="coordinator",
        )],
        created_at=now,
        last_updated=now,
        programme_id=body.programme_id,
        mentor_confirmed=False,
        startup_confirmed=False,
    )
    firebase_client.save_relationship(rel)
    execute_workflow(WorkflowTrigger.match_approved, {
        "relationship_id": rel.id,
        "actor_a_id": body.actor_a_id,
        "actor_b_id": body.actor_b_id,
        "match_score": body.match_score,
    })
    return rel
