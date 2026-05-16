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


_SYSTEM_PROMPT = """You are an expert innovation ecosystem matchmaker.
A programme coordinator will describe a situation in plain language — a startup's problem, a need, a goal.
Your job is to read ALL available actor profiles (mentors, companies, partners, service providers) and return the most relevant ones that could help.

Rules:
- Pick the best matches regardless of actor type — if the coordinator needs a mentor AND a service provider, return both
- Score each match on genuine relevance to the described situation (0-100)
- Only return actors that are actually useful — do not pad results with weak matches
- Return up to 5 results maximum, sorted by score descending

You MUST output ONLY a valid JSON array. No markdown, no explanation, nothing outside the JSON.
Each object must strictly match:
{
    "actor_id": "exact id from the profile",
    "actor_name": "actor's name",
    "score": integer 0-100,
    "reasoning": "one sentence — why this actor helps with the described situation",
    "suggested_intro": "2-sentence message the coordinator could send to introduce this actor to the startup"
}"""


def match_actors(query: str, candidates: list[ActorProfile]) -> list[MatchResult]:
    if not candidates:
        return [MatchResult(
            actor_id="",
            actor_name="No actors onboarded",
            score=0,
            reasoning="No profiles exist in the database yet. Onboard some actors first.",
            suggested_intro="",
        )]

    api_key = os.environ.get("GEMINI_API_KEY", "")
    client = genai.Client(api_key=api_key)

    profiles_json = json.dumps(
        [c.model_dump(mode="json") for c in candidates],
        indent=2,
        default=str,
    )

    prompt = (
        f"{_SYSTEM_PROMPT}"
        f"\n\nCoordinator's request: {query}"
        f"\n\nAll available actors:\n{profiles_json}"
        f"\n\nReturn only the JSON array:"
    )

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
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
