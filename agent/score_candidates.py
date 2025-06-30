import re
from typing import List, Dict, Any


def score_education(candidate_info: str) -> float:
    """
    Score education based on school prestige and progression.
    Returns score 0-10.
    """
    text = candidate_info.lower()
    
    # Elite schools
    elite_schools = [
        'mit', 'stanford', 'harvard', 'caltech', 'princeton', 'yale', 'columbia',
        'university of pennsylvania', 'upenn', 'northwestern', 'duke', 'berkeley',
        'uc berkeley', 'carnegie mellon', 'cmu', 'georgia tech', 'gatech'
    ]
    
    # Strong schools
    strong_schools = [
        'ucla', 'usc', 'nyu', 'boston university', 'bu', 'university of michigan',
        'umich', 'university of illinois', 'uiuc', 'university of texas', 'utexas',
        'university of washington', 'uw', 'university of wisconsin', 'uw-madison'
    ]
    
    # Check for elite schools
    for school in elite_schools:
        if school in text:
            return 9.5
    
    # Check for strong schools
    for school in strong_schools:
        if school in text:
            return 7.5
    
    # Check for clear progression (bachelor's to master's/PhD)
    if re.search(r'(bachelor|b\.?s\.?|b\.?a\.?)', text) and re.search(r'(master|m\.?s\.?|m\.?a\.?|ph\.?d|doctorate)', text):
        return 8.5
    
    # Standard universities
    if re.search(r'university|college|institute', text):
        return 5.5
    
    return 3.0


def score_career_trajectory(candidate_info: str) -> float:
    """
    Score career trajectory based on job progression.
    Returns score 0-10.
    """
    text = candidate_info.lower()
    
    # Look for progression indicators
    senior_indicators = ['senior', 'lead', 'principal', 'staff', 'director', 'manager', 'head of']
    junior_indicators = ['junior', 'associate', 'entry', 'intern', 'graduate']
    
    senior_count = sum(1 for indicator in senior_indicators if indicator in text)
    junior_count = sum(1 for indicator in junior_indicators if indicator in text)
    
    # Steady growth (more senior positions)
    if senior_count >= 2:
        return 7.5
    elif senior_count >= 1:
        return 6.5
    elif junior_count >= 2:
        return 4.0  # Limited progression
    else:
        return 5.0  # Neutral


def score_company_relevance(candidate_info: str) -> float:
    """
    Score company relevance based on tech industry presence.
    Returns score 0-10.
    """
    text = candidate_info.lower()
    
    # Top tech companies
    top_tech = [
        'google', 'microsoft', 'apple', 'amazon', 'meta', 'facebook', 'netflix',
        'tesla', 'nvidia', 'intel', 'amd', 'oracle', 'salesforce', 'adobe',
        'uber', 'lyft', 'airbnb', 'stripe', 'square', 'palantir', 'databricks',
        'snowflake', 'mongodb', 'atlassian', 'slack', 'zoom', 'shopify'
    ]
    
    # Strong tech companies
    strong_tech = [
        'ibm', 'cisco', 'dell', 'hp', 'hewlett-packard', 'vmware', 'sap',
        'workday', 'servicenow', 'splunk', 'elastic', 'confluent', 'hashicorp',
        'gitlab', 'github', 'docker', 'kubernetes', 'red hat', 'canonical'
    ]
    
    # Check for top tech companies
    for company in top_tech:
        if company in text:
            return 9.5
    
    # Check for strong tech companies
    for company in strong_tech:
        if company in text:
            return 7.5
    
    # Check for any tech-related experience
    tech_indicators = ['software', 'technology', 'tech', 'engineering', 'development', 'programming']
    if any(indicator in text for indicator in tech_indicators):
        return 6.0
    
    return 4.0


def score_experience_match(candidate_info: str, job_description: str) -> float:
    """
    Score experience match based on skill overlap.
    Returns score 0-10.
    """
    candidate_text = candidate_info.lower()
    job_text = " ".join(job_description).lower() if isinstance(job_description, list) else job_description.lower()
    
    # Common programming languages and technologies
    skills = [
        'python', 'javascript', 'java', 'c++', 'c#', 'php', 'ruby', 'go', 'rust',
        'react', 'angular', 'vue', 'node.js', 'django', 'flask', 'spring',
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'git', 'sql', 'mongodb',
        'machine learning', 'ai', 'data science', 'devops', 'agile', 'scrum',
        'typescript', 'html', 'css', 'bootstrap', 'jquery', 'express', 'fastapi',
        'postgresql', 'mysql', 'redis', 'elasticsearch', 'kafka', 'rabbitmq',
        'jenkins', 'github actions', 'terraform', 'ansible', 'puppet', 'chef'
    ]
    
    # Count matching skills
    matches = 0
    for skill in skills:
        if skill in candidate_text and skill in job_text:
            matches += 1
    
    # Perfect skill match
    if matches >= 8:
        return 9.5
    elif matches >= 5:
        return 7.5
    elif matches >= 3:
        return 6.0
    elif matches >= 1:
        return 4.5
    else:
        return 2.0


def score_location_match(candidate_info: str, job_location: str = "") -> float:
    """
    Score location match based on geographic proximity.
    Returns score 0-10.
    """
    if not job_location:
        return 6.0  # Remote-friendly default
    
    candidate_text = candidate_info.lower()
    job_location_lower = job_location.lower()
    
    # Extract city names from candidate info
    city_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*(?:CA|NY|TX|FL|WA|MA|IL|PA|OH|GA|NC|VA|MI|NJ|CO|AZ|OR|TN|IN|MN|WI|MO|LA|AL|SC|KY|OK|CT|IA|NV|AR|MS|KS|UT|NE|ID|NH|ME|RI|MT|DE|SD|ND|AK|VT|WY|WV|HI)\b'
    candidate_cities = re.findall(city_pattern, candidate_info)
    
    # Exact city match
    for city in candidate_cities:
        if city.lower() in job_location_lower or job_location_lower in city.lower():
            return 10.0
    
    # Same metro area (simplified check)
    metro_areas = {
        'san francisco': ['san francisco', 'oakland', 'san jose', 'palo alto', 'mountain view'],
        'new york': ['new york', 'brooklyn', 'queens', 'manhattan', 'bronx'],
        'los angeles': ['los angeles', 'hollywood', 'beverly hills', 'santa monica'],
        'seattle': ['seattle', 'bellevue', 'redmond', 'kirkland'],
        'austin': ['austin', 'round rock', 'cedar park'],
        'boston': ['boston', 'cambridge', 'somerville', 'brookline']
    }
    
    for metro, cities in metro_areas.items():
        if any(city in job_location_lower for city in cities):
            if any(city in candidate_text for city in cities):
                return 8.0
    
    # Remote indicators
    remote_indicators = ['remote', 'work from home', 'wfh', 'virtual', 'distributed']
    if any(indicator in candidate_text for indicator in remote_indicators):
        return 6.0
    
    return 3.0


def score_tenure(candidate_info: str) -> float:
    """
    Score tenure based on job duration patterns.
    Returns score 0-10.
    """
    text = candidate_info.lower()
    
    # Look for duration patterns
    duration_patterns = [
        r'(\d+)\s*(?:year|yr)s?',
        r'(\d+)\s*months?',
        r'(\d+)\s*weeks?'
    ]
    
    durations = []
    for pattern in duration_patterns:
        matches = re.findall(pattern, text)
        durations.extend([int(match) for match in matches])
    
    if not durations:
        return 5.0  # Default if no duration info
    
    avg_duration = sum(durations) / len(durations)
    
    # Convert to years if needed
    if avg_duration < 12:  # Assuming months
        avg_duration = avg_duration / 12
    
    # Score based on average tenure
    if 2 <= avg_duration <= 3:
        return 9.5
    elif 1 <= avg_duration < 2:
        return 7.0
    elif avg_duration < 1:
        return 3.0  # Job hopping
    else:
        return 6.0  # Long tenure


def score_candidates(candidates: List[Dict], job_description: str, job_location: str = "") -> List[Dict]:
    """
    Assigns a fit score to each candidate based on the comprehensive rubric.
    
    Scoring weights:
    - Education: 20%
    - Career Trajectory: 20%
    - Company Relevance: 15%
    - Experience Match: 25%
    - Location Match: 10%
    - Tenure: 10%
    """
    scored = []
    
    for candidate in candidates:
        # Combine candidate information for analysis
        candidate_info = f"{candidate.get('name', '')} {candidate.get('headline', '')} {candidate.get('linkedin_url', '')}"
        
        # Calculate individual scores
        education_score = score_education(candidate_info)
        trajectory_score = score_career_trajectory(candidate_info)
        company_score = score_company_relevance(candidate_info)
        experience_score = score_experience_match(candidate_info, job_description)
        location_score = score_location_match(candidate_info, job_location)
        tenure_score = score_tenure(candidate_info)
        
        # Calculate weighted total score
        total_score = (
            education_score * 0.20 +
            trajectory_score * 0.20 +
            company_score * 0.15 +
            experience_score * 0.25 +
            location_score * 0.10 +
            tenure_score * 0.10
        )
        
        scored.append({
            "name": candidate.get("name", "Unknown"),
            "linkedin_url": candidate.get("linkedin_url", ""),
            "headline": candidate.get("headline", ""),
            "score": round(total_score, 2),
            "breakdown": {
                "education": round(education_score, 2),
                "career_trajectory": round(trajectory_score, 2),
                "company_relevance": round(company_score, 2),
                "experience_match": round(experience_score, 2),
                "location_match": round(location_score, 2),
                "tenure": round(tenure_score, 2)
            }
        })
    
    # Sort by score in descending order
    scored.sort(key=lambda x: x["score"], reverse=True)
    
    return scored