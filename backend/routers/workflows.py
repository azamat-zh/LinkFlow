from fastapi import APIRouter

from services import firebase_client
from services.workflow_engine import WorkflowTrigger, execute_workflow

router = APIRouter()


@router.get("/workflows/stale")
async def get_stale():
    stale_rels = firebase_client.get_stale_relationships(days=14)
    results = []
    for rel in stale_rels:
        outcome = execute_workflow(WorkflowTrigger.relationship_stale, {
            "relationship_id": rel.id,
            "actor_a_id": rel.actor_a_id,
            "actor_b_id": rel.actor_b_id,
        })
        results.append({
            "relationship": rel.model_dump(mode="json"),
            "nudge_message": outcome.get("nudge_message", ""),
        })
    return results


@router.get("/workflows/events")
async def get_events():
    db = firebase_client.get_db()
    docs = (
        db.collection("workflow_events")
        .order_by("timestamp", direction="DESCENDING")
        .limit(50)
        .stream()
    )
    events = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        if hasattr(data.get("timestamp"), "isoformat"):
            data["timestamp"] = data["timestamp"].isoformat()
        events.append(data)
    return events
