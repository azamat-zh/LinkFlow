import json
import os

import google.generativeai as genai
from pydantic import BaseModel

from models.actor import ActorProfile

_SYSTEM_INSTRUCTION = (
    "You are an ecosystem relationship matching engine for an innovation programme platform. "
    "Given an administrator's natural language request and a list of actor profiles, return the "
    "top 5 matches ranked by fit score. For each match return a JSON object with: actor_id (string), "
    "actor_name (string), score (integer 0-100 representing match quality), reasoning (one sentence "
    "explaining the match), suggested_intro (a 2-sentence introduction message the admin could send "
    "to both parties). Consider sector alignment, stage compatibility, and complementary needs versus "
    "expertise. Be honest about weak matches. Return only a valid JSON array, no markdown."
)


class MatchResult(BaseModel):
    actor_id: str
    actor_name: str
    score: int
    reasoning: str
    suggested_intro: str


def _get_model():
    api_key = os.environ.get("GEMINI_API_KEY", "")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=_SYSTEM_INSTRUCTION,
    )


def match_actors(query: str, candidates: list[ActorProfile]) -> list[MatchResult]:
    if not candidates:
        return [MatchResult(
            actor_id="",
            actor_name="No candidates",
            score=0,
            reasoning="No candidate profiles were found in the database for the requested type.",
            suggested_intro="",
        )]

    profiles_json = json.dumps(
        [c.model_dump(mode="json") for c in candidates],
        indent=2,
        default=str,
    )
    prompt = (
        f"Admin query: {query}\n\n"
        f"Candidate profiles:\n{profiles_json}"
    )

    try:
        model = _get_model()
        response = model.generate_content(prompt)
        raw = response.text.strip()
        data = json.loads(raw)
        return [MatchResult(**item) for item in data]
    except Exception as exc:
        return [MatchResult(
            actor_id="",
            actor_name="Error",
            score=0,
            reasoning=f"Gemini API error: {exc}",
            suggested_intro="",
        )]
