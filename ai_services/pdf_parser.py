import json
import requests
from pypdf import PdfReader

def parse_pdf_to_profile(file_path: str) -> dict:
    """
    Extracts text from a PDF pitch deck and uses a local Ollama model to parse it into a structured JSON profile.
    """
    try:
        # Extract text from PDF
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        
        # Prepare Ollama prompt
        system_prompt = """You are an expert venture capital analyst. Your task is to extract key information from the provided pitch deck text and format it STRICTLY as a JSON object. 
DO NOT include any markdown formatting, explanation, or text outside of the JSON block.
The JSON must perfectly match this schema:
{
    "name": "Startup Name",
    "industry": "Primary Industry",
    "stage": "Company Stage (e.g., Pre-seed, Seed, Series A)",
    "needs": ["Need 1", "Need 2", "Need 3"],
    "summary": "A concise 2-sentence summary of what the startup does"
}
"""
        
        prompt = f"{system_prompt}\n\nPitch Deck Text:\n{text}\n\nOutput only the JSON:"

        # Call local Ollama
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False,
                "format": "json"
            },
            timeout=120
        )
        response.raise_for_status()
        
        result_text = response.json().get("response", "")
        
        # Parse JSON
        profile = json.loads(result_text)
        return profile
        
    except Exception as e:
        print(f"Error parsing PDF to profile: {e}")
        # Return fallback dictionary
        return {
            "name": "Unknown",
            "industry": "Unknown",
            "stage": "Unknown",
            "needs": [],
            "summary": "Failed to parse PDF."
        }
