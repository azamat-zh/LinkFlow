import json
from gemini_matcher import score_mentors
from workflow_engine import evaluate_match_workflow

def main():
    print("--- LinkFlow AI Services Test ---")
    
    # Mock Startup Profile
    startup_profile = {
        "name": "HealthAI",
        "industry": "Healthcare Tech",
        "stage": "Seed",
        "needs": ["Go-to-market strategy", "FDA compliance advice", "Seed round fundraising"],
        "summary": "HealthAI uses machine learning to predict patient readmission rates, helping hospitals reduce costs and improve care."
    }
    
    # Mock Mentors List
    mentors_list = [
        {
            "mentor_id": "m101",
            "name": "Dr. Sarah Chen",
            "expertise": ["Healthcare SaaS", "Regulatory Compliance", "Series A"],
            "bio": "Former Chief Medical Officer turned VC. Specializes in helping healthtech startups navigate FDA approvals."
        },
        {
            "mentor_id": "m102",
            "name": "James Smith",
            "expertise": ["E-commerce", "Digital Marketing", "Pre-seed"],
            "bio": "Marketing guru who has scaled 5 D2C brands to $10M+ in revenue."
        },
        {
            "mentor_id": "m103",
            "name": "Elena Rodriguez",
            "expertise": ["B2B Enterprise", "Go-to-market", "Seed funding"],
            "bio": "Angel investor and former CRO. Loves helping founders build their first sales motion and raise Seed rounds."
        }
    ]
    
    print("\n[1] Testing Gemini Matcher...")
    print("Startup:", startup_profile["name"])
    print(f"Matching against {len(mentors_list)} mentors...")
    
    matches = score_mentors(startup_profile, mentors_list)
    
    if not matches:
        print("Failed to get matches. Ensure GEMINI_API_KEY is set in your environment.")
        return
        
    print("\nMatches found:")
    print(json.dumps(matches, indent=2))
    
    print("\n[2] Testing Workflow Engine...")
    for match in matches:
        mentor_id = match.get("mentor_id")
        score = match.get("score", 0)
        action = evaluate_match_workflow(score)
        print(f"Mentor {mentor_id} with score {score} -> Action: {action}")
        
if __name__ == "__main__":
    main()
