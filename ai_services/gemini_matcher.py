import os
import json
from google import genai
from google.genai import types

def score_mentors(startup_profile: dict, mentors_list: list[dict]) -> list[dict]:
    """
    Compares a startup profile against a list of mentor profiles using Gemini 1.5 Flash.
    Returns a list of match scores and justifications.
    """
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set.")
            
        client = genai.Client(api_key=api_key)
        
        system_prompt = """You are an expert venture ecosystem matchmaker. You will be provided with a startup's profile and a list of mentor profiles.
Your task is to evaluate how well each mentor matches the startup's needs, industry, and stage.
You MUST output ONLY a valid JSON array of objects. Do not include any markdown formatting like ```json or any other text.
Each object in the array must strictly match this structure:
{
    "mentor_id": "the exact ID of the mentor",
    "score": integer between 0 and 100 representing the match quality,
    "justification": "A single sentence explaining why this score was given"
}
"""
        
        prompt = f"""{system_prompt}

Startup Profile:
{json.dumps(startup_profile, indent=2)}

Mentors List:
{json.dumps(mentors_list, indent=2)}

Output ONLY the JSON array:"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            )
        )
        
        result_text = response.text.strip()
        matches = json.loads(result_text)
        
        # Ensure it's a list
        if not isinstance(matches, list):
            matches = [matches]
            
        return matches
        
    except Exception as e:
        print(f"Error scoring mentors: {e}")
        return []
