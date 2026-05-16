def evaluate_match_workflow(match_score: int) -> str:
    """
    Determines the next workflow step based on the mentor match score.
    """
    try:
        score = int(match_score)
    except (ValueError, TypeError):
        return "reject" # Default to reject if score is invalid
        
    if score >= 80:
        return "auto_approve_and_notify"
    elif score >= 50:
        return "flag_for_human_review"
    else:
        return "reject"
