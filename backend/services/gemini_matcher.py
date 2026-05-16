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
Given an administrator's natural language request and a list of actor profiles, return the top 5 matches ranked by fit score.
You MUST output ONLY a valid JSON array. Do not include any markdown formatting or text outside the JSON.
Each object in the array must strictly match this structure:
{
    "actor_id": "the exact id of the actor",
    "actor_name": "the actor's name",
    "score": integer between 0 and 100 representing match quality,
    "reasoning": "one sentence explaining the match",
    "suggested_intro": "a 2-sentence introduction message the admin could send to both parties"
}
Consider sector alignment, stage compatibility, and complementary needs versus expertise. Be honest about weak matches."""


def match_actors(query: str, candidates: list[ActorProfile]) -> list[MatchResult]:
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

    profiles_json = json.dumps(
        [c.model_dump(mode="json") for c in candidates],
        indent=2,
        default=str,
    )
    prompt = f"{_SYSTEM_PROMPT}\n\nAdmin query: {query}\n\nCandidate profiles:\n{profiles_json}\n\nOutput only the JSON array:"

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
