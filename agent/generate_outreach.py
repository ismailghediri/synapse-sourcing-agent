import os
import requests
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

def query_gemini(prompt: str) -> str:
    """Query Gemini API with the prompt"""
    API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"
    headers = {"Content-Type": "application/json"}
    
    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": 100}
    }
    
    try:
        # Get API key from environment variables
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file")
        
        response = requests.post(
            f"{API_URL}?key={api_key}",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        
        result = response.json()
        return result["candidates"][0]["content"]["parts"][0]["text"].strip()
    
    except Exception as e:
        return f"Error querying Gemini API: {str(e)}"

def generate_outreach(candidates: list, job_description: str) -> list:
    """Generate personalized outreach messages for candidates"""
    messages = []
    for candidate in candidates:
        name = candidate["name"]
        headline = candidate.get("headline", "N/A")

        prompt = f"""You are a technical recruiter writing a personalized LinkedIn message.

Here is the candidate's profile:
- Name: {name}
- Headline: {headline}

Here is the job description summary:
{job_description}

Write a short, professional, and engaging message that:
1. Mentions the candidate's role or current company
2. Explains why they're a good match for this role
3. Sounds like it's coming from a real recruiter

Return only the message."""

        message = query_gemini(prompt)
        messages.append({
            "candidate": name,
            "message": message.strip()
        })
    
    return messages

# Example usage (for testing)
if __name__ == "__main__":
    # Test with mock data
    test_candidates = [
        {"name": "John Doe", "headline": "Software Engineer at TechCorp"},
        {"name": "Jane Smith", "headline": "Data Scientist at DataWorks"}
    ]
    test_job = "Seeking Senior Python Developer with ML experience"
    
    results = generate_outreach(test_candidates, test_job)
    for result in results:
        print(f"To: {result['candidate']}")
        print(f"Message: {result['message']}\n")