import json
import os

from google import genai
from google.genai import types
from pydantic import BaseModel

from models.actor import ActorProfile


class MatchResult(BaseModel):
    actor_id: str
    actor_name: str
    score: int
    reasoning: str
    suggested_intro: str


_SYSTEM_PROMPT = """You are an expert venture ecosystem matchmaker for an innovation programme platform.
You will be given a FOCUS ACTOR profile and a list of CANDIDATE profiles.
Your job is to score how well each candidate complements the focus actor — based on their needs vs expertise, sector alignment, and stage compatibility.
The admin's query is an optional hint but the primary scoring must be based on profile-to-profile fit, not keyword matching.
You MUST output ONLY a valid JSON array. Do not include any markdown formatting or text outside the JSON.
Each object in the array must strictly match this structure:
{
    "actor_id": "the exact id of the candidate actor",
    "actor_name": "the candidate's name",
    "score": integer between 0 and 100 representing compatibility with the focus actor,
    "reasoning": "one sentence explaining why this candidate fits the focus actor specifically",
    "suggested_intro": "a 2-sentence introduction message referencing both actors by name"
}
Be honest — a weak profile match should score low even if it matches the query keywords."""


def match_actors(query: str, candidates: list[ActorProfile], focus_actor: ActorProfile | None = None) -> list[MatchResult]:
    if not candidates:
        return [MatchResult(
            actor_id="",
            actor_name="No candidates",
            score=0,
            reasoning="No candidate profiles were found in the database for the requested type.",
            suggested_intro="",
        )]

    api_key = os.environ.get("GEMINI_API_KEY", "")
    client = genai.Client(api_key=api_key)

    focus_section = ""
    if focus_actor:
        focus_json = json.dumps(focus_actor.model_dump(mode="json"), indent=2, default=str)
        focus_section = f"\n\nFOCUS ACTOR (find matches FOR this person/organisation):\n{focus_json}"

    profiles_json = json.dumps(
        [c.model_dump(mode="json") for c in candidates],
        indent=2,
        default=str,
    )
    prompt = (
        f"{_SYSTEM_PROMPT}"
        f"{focus_section}"
        f"\n\nAdmin hint/query: {query}"
        f"\n\nCANDIDATE profiles to score:\n{profiles_json}"
        f"\n\nOutput only the JSON array:"
    )

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )
        data = json.loads(response.text.strip())
        if not isinstance(data, list):
            data = [data]
        return [MatchResult(**item) for item in data]
    except Exception as exc:
        return [MatchResult(
            actor_id="",
            actor_name="Error",
            score=0,
            reasoning=f"Gemini API error: {exc}",
            suggested_intro="",
        )]
