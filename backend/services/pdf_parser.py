import json
import os
import uuid
from datetime import datetime, timezone
from io import BytesIO

import httpx
from pypdf import PdfReader

from models.actor import ActorProfile, ActorType

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")

_SYSTEM_PROMPT = """You are an expert venture capital analyst and profile extraction assistant for an innovation ecosystem platform.
Extract structured information from the following document and return ONLY a valid JSON object with these exact fields:
{
    "name": "string — person or company name",
    "actor_type": "one of: company, mentor, partner, service_provider",
    "sector": "string — primary industry sector",
    "stage": "string — for companies: idea/pre-seed/seed/series-a/growth; for mentors: their seniority level",
    "tags": ["array of 3-7 keyword strings"],
    "needs": ["array of strings describing what this actor needs"],
    "expertise": ["array of strings describing what this actor offers"],
    "location": "string — city or country",
    "bio": "string — 2-3 sentence summary"
}
Return only the JSON object, no explanation, no markdown backticks."""


def _extract_text(file_bytes: bytes) -> str:
    reader = PdfReader(BytesIO(file_bytes))
    parts = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            parts.append(text)
    return "\n".join(parts)


def _call_ollama(text: str) -> dict | None:
    prompt = f"{_SYSTEM_PROMPT}\n\nDocument:\n{text[:8000]}\n\nOutput only the JSON:"
    try:
        response = httpx.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False,
                "format": "json",
            },
            timeout=120.0,
        )
        response.raise_for_status()
        raw = response.json().get("response", "")
        return json.loads(raw)
    except (httpx.RequestError, httpx.HTTPStatusError):
        return None
    except json.JSONDecodeError:
        return None


def parse_pdf_to_profile(file_bytes: bytes, filename: str) -> ActorProfile:
    raw_text = _extract_text(file_bytes)
    parsed = _call_ollama(raw_text)

    actor_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)

    if parsed is None:
        return ActorProfile(
            id=actor_id,
            name="[MANUAL REVIEW NEEDED]",
            actor_type=ActorType.company,
            sector="",
            stage="",
            tags=[],
            needs=[],
            expertise=[],
            location="",
            bio=raw_text[:500],
            source_file=filename,
            created_at=now,
            programme_history=[],
        )

    return ActorProfile(
        id=actor_id,
        name=parsed.get("name", "Unknown"),
        actor_type=ActorType(parsed.get("actor_type", "company")),
        sector=parsed.get("sector", ""),
        stage=parsed.get("stage", ""),
        tags=parsed.get("tags", []),
        needs=parsed.get("needs", []),
        expertise=parsed.get("expertise", []),
        location=parsed.get("location", ""),
        bio=parsed.get("bio", ""),
        source_file=filename,
        created_at=now,
        programme_history=[],
    )
