from fastapi import APIRouter, File, HTTPException, Query, UploadFile

from models.actor import ActorProfile, ActorType
from services import firebase_client, pdf_parser
from services.workflow_engine import WorkflowTrigger, execute_workflow

router = APIRouter()

MAX_PDF_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post("/onboarding/upload", response_model=ActorProfile)
async def upload_pdf(file: UploadFile = File(...)):
    if file.content_type != "application/pdf" and not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    file_bytes = await file.read()
    if len(file_bytes) > MAX_PDF_SIZE:
        raise HTTPException(status_code=400, detail="File exceeds the 10 MB size limit.")

    actor = pdf_parser.parse_pdf_to_profile(file_bytes, file.filename)
    firebase_client.save_actor(actor)
    execute_workflow(WorkflowTrigger.actor_joined, {"actor_id": actor.id, "name": actor.name})

    return actor


@router.get("/actors", response_model=list[ActorProfile])
async def list_actors(actor_type: str = Query(default=None, alias="type")):
    if actor_type:
        try:
            parsed_type = ActorType(actor_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid actor type: {actor_type}")
        return firebase_client.get_actors_by_type(parsed_type)
    return firebase_client.get_all_actors()


@router.get("/actors/{actor_id}", response_model=ActorProfile)
async def get_actor(actor_id: str):
    actor = firebase_client.get_actor(actor_id)
    if actor is None:
        raise HTTPException(status_code=404, detail="Actor not found.")
    return actor
