import os
from datetime import datetime, timezone
from enum import Enum

from google import genai

from services import firebase_client


class WorkflowTrigger(str, Enum):
    actor_joined = "actor_joined"
    match_approved = "match_approved"
    relationship_stale = "relationship_stale"
    session_logged = "session_logged"


def evaluate_match_workflow(match_score: int) -> str:
    """Returns the recommended next action based on match score."""
    try:
        score = int(match_score)
    except (ValueError, TypeError):
        return "reject"
    if score >= 80:
        return "auto_approve_and_notify"
    elif score >= 50:
        return "flag_for_human_review"
    else:
        return "reject"


def _generate_nudge() -> str:
    try:
        api_key = os.environ.get("GEMINI_API_KEY", "")
        client = genai.Client(api_key=api_key)
        prompt = (
            "Write a friendly 2-sentence check-in message from a programme coordinator to a mentor "
            "who has not logged a session with their assigned startup in the past 14 days. "
            "Be warm and non-accusatory. Return only the message text."
        )
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return response.text.strip()
    except Exception:
        return "Hi! Just checking in — it's been a while since your last session. Hope everything is going well!"


def execute_workflow(trigger: WorkflowTrigger, context: dict) -> dict:
    firebase_client.log_workflow_event(trigger.value, context)

    if trigger == WorkflowTrigger.actor_joined:
        return {"status": "logged", "trigger": trigger.value, "message": "Actor joined event recorded."}

    if trigger == WorkflowTrigger.match_approved:
        score = context.get("match_score", 0)
        action = evaluate_match_workflow(score)
        return {"status": "logged", "trigger": trigger.value, "message": "Match approved event recorded.", "recommended_action": action}

    if trigger == WorkflowTrigger.relationship_stale:
        nudge = _generate_nudge()
        return {"status": "logged", "trigger": trigger.value, "nudge_message": nudge}

    if trigger == WorkflowTrigger.session_logged:
        return {"status": "logged", "trigger": trigger.value, "message": "Session logged event recorded."}

    return {"status": "no_op", "trigger": trigger.value}
