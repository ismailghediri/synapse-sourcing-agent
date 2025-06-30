import os
import requests
import re
import time
import pickle
from datetime import datetime, timedelta
from typing import List, Dict
from urllib.parse import quote
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Constants
MAX_RETRIES = 3
REQUEST_DELAY = 2
CACHE_FILE = "cache.pkl"
CACHE_EXPIRY_DAYS = 7

def load_cache() -> Dict[str, Dict]:
    """Load cached profiles from file."""
    try:
        with open(CACHE_FILE, "rb") as f:
            print("Loading from cache")
            return pickle.load(f)
    except (FileNotFoundError, pickle.PickleError):
        return {}

def save_cache(cache: Dict[str, Dict]):
    """Save profiles to cache file."""
    try:
        with open(CACHE_FILE, "wb") as f:
            pickle.dump(cache, f)
    except Exception as e:
        print(f"Cache save error: {str(e)}")

def is_cache_valid(entry: Dict) -> bool:
    """Check if cached entry is still valid (not expired)."""
    timestamp = entry.get("timestamp")
    if not timestamp:
        return False
    return datetime.now() >= timestamp and (datetime.now() - timestamp).days < CACHE_EXPIRY_DAYS

def search_linkedin(job_description: str) -> List[Dict[str, str]]:
    """
    Search LinkedIn profiles using Serper.dev

    Args:
        job_description: Job description to search candidates for

    Returns:
        List of candidate profiles with name, URL, headline, current company, and location
    """
    try:
        candidates = search_with_serper(job_description)
        return candidates
    except Exception as e:
        print(f"Search error: {str(e)}")
        return []

def search_with_serper(query: str) -> List[Dict[str, str]]:
    """Search using Serper.dev API"""
    cache = load_cache()
    candidates = []
    
    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": os.getenv("SERPER_API_KEY"),
        "Content-Type": "application/json"
    }
    payload = {
        "q": f'site:linkedin.com/in {query}'
    }

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            for result in data.get("organic", []):
                linkedin_url = result.get("link", "")
                # Check cache first
                if linkedin_url in cache and is_cache_valid(cache[linkedin_url]):
                    print(f"Using cached profile for {linkedin_url}")
                    candidates.append(cache[linkedin_url]["profile"])
                else:
                    name, headline = parse_linkedin_title(result.get("title", ""))
                    profile = {
                        "name": name,
                        "linkedin_url": linkedin_url,
                        "headline": headline,
                        "current_company": headline.split(" at ")[-1] if " at " in headline else "",
                        "location": ""
                    }
                    candidates.append(profile)
                    cache[linkedin_url] = {"profile": profile, "timestamp": datetime.now()}
            
            save_cache(cache)
            return candidates
        except requests.exceptions.RequestException as e:
            print(f"Serper attempt {attempt + 1} failed: {str(e)}")
            if attempt == MAX_RETRIES - 1:
                raise
            time.sleep(REQUEST_DELAY * (attempt + 1))
    
    save_cache(cache)
    return candidates

def parse_linkedin_title(title: str) -> tuple[str, str]:
    """Extract name and headline from LinkedIn title"""
    match = re.search(r"(.*?)\s*-\s*(.*?)\s*\|\s*LinkedIn", title, re.IGNORECASE)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return title.strip(), ""

# Example usage
if __name__ == "__main__":
    job_desc = "Senior Machine Learning Engineer fintech San Francisco"
    print("Searching LinkedIn for candidates...")
    candidates = search_linkedin(job_desc)

    print(f"Found {len(candidates)} candidates:")
    for candidate in candidates:
        print(f"\nName: {candidate['name']}")
        print(f"URL: {candidate['linkedin_url']}")
        print(f"Headline: {candidate['headline']}")
        print(f"Current Company: {candidate['current_company']}")
        print(f"Location: {candidate['location']}")