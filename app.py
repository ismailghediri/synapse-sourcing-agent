from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging
from agent.search_linkedin import search_linkedin
from agent.score_candidates import score_candidates
from agent.generate_outreach import generate_outreach
import os
import json

# Configure environment
os.environ['WDM_LOCAL'] = '1'
os.environ['WDM_CACHE_PATH'] = '/tmp/.wdm'

app = FastAPI(title="Synapse Recruitment API")

class JobRequest(BaseModel):
    description: str
    location: str = ""
    max_candidates: int = 10  # Update to 10 as per requirement

def safe_get(d, keys, default=""):
    """Safely get nested dictionary values"""
    for key in keys:
        if isinstance(d, dict):
            d = d.get(key, default)
        else:
            return default
    return d

@app.post("/get_candidates/")
async def get_candidates(request: JobRequest):
    try:
        candidates = search_linkedin(request.description)
        if not candidates:
            return {
                "job_description": request.description,
                "warning": "No candidates found",
                "top_candidates": []
            }

        scored = score_candidates(candidates, request.description)
        print(f"Scored candidate: {scored[0]}")  # Debug to check data
        outreach_msgs = generate_outreach(scored, request.description)  # Returns list of dicts
        
        messages = []
        for i, candidate in enumerate(scored[:request.max_candidates]):
            # Find the corresponding outreach message for this candidate
            msg_dict = next((m for m in outreach_msgs if m.get("candidate") == safe_get(candidate, ["name"])), {})
            outreach_msg = safe_get(msg_dict, ["message"], "Unable to generate message")
            messages.append({
                "name": safe_get(candidate, ["name"]),
                "linkedin_url": safe_get(candidate, ["linkedin_url"]),
                "score": safe_get(candidate, ["score"], 0),
                "outreach_message": outreach_msg,
                "match_analysis": [
                    f"Experience: {safe_get(candidate, ['breakdown', 'experience_match'], 0)}/10",
                    f"Education: {safe_get(candidate, ['breakdown', 'education'], 0)}/10"
                ]
            })
        
        return {
            "job_description": request.description,
            "location": request.location,
            "top_candidates": messages
        }

    except Exception as e:
        logging.error(f"API Error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail=f"Processing failed: {str(e)}"
        )